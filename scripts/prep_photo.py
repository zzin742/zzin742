#!/usr/bin/env python3
"""
Prepara a foto pro ASCII:
  1. isola a pessoa (rembg) pra que o fundo vire espaço em branco
  2. suaviza a textura da pele sem perder bordas (filtro bilateral)
  3. realça contraste local (CLAHE): uma foto de luz chapada ganha luz e sombra
  4. estica os tons só sobre a pessoa, compõe sobre branco
  5. recorta em quadrado ao redor da pessoa

Saída: um PNG em escala de cinza, consumido por make_ascii_svg.py.

    python scripts/prep_photo.py <foto> [saida.png]

Variáveis opcionais:
    NO_REMBG=1   pula a remoção de fundo
    CLAHE=2.0    força do contraste local (clip limit)
    SMOOTH=2     passadas do filtro bilateral (0 desliga)
    PAD=40       margem em px ao redor do recorte
    HEAD_FRAC=1  fração da altura da pessoa a manter (0.6 = cabeça e pescoço)
    BG=white     cor do fundo composto (black pra usar com INVERT=1 no ASCII)
    FLIP=1       espelha a foto horizontalmente
    LINES=0.5    escurece linhas finas (contorno do rosto, olho, boca)
    FADE=0.12    esmaece a base da imagem pro fundo
    LO=2 HI=98   percentis do estiramento de tons
"""
import os
import sys

import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "portrait", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "assets", "portrait", "source-prepped.png")
CLAHE_CLIP = float(os.environ.get("CLAHE", "2.0"))
SMOOTH = int(os.environ.get("SMOOTH", "2"))
PAD = int(os.environ.get("PAD", "40"))
LO, HI = float(os.environ.get("LO", "2")), float(os.environ.get("HI", "98"))
HEAD_FRAC = float(os.environ.get("HEAD_FRAC", "1.0"))
BGCOL = 0 if os.environ.get("BG", "white").lower() in ("black", "preto", "0") else 255  # cor do fundo composto
LINES = float(os.environ.get("LINES", "0"))   # 0-1: quanto escurecer as linhas finas (contorno, olho, boca, orelha)
FADE = float(os.environ.get("FADE", "0"))     # 0-0.5: fração da altura que esmaece pro fundo na base (some com o colarinho)  # 1.0 = pessoa inteira; 0.6 = só cabeça e pescoço

img = Image.open(INP).convert("RGBA")
if os.environ.get("FLIP"):
    img = ImageOps.mirror(img)  # espelha horizontalmente (perfil olhando pro outro lado)

# 1. isola a pessoa
if os.environ.get("NO_REMBG"):
    cut = img
else:
    try:
        from rembg import remove
        cut = remove(img)
    except Exception as e:
        print(f"rembg indisponível ({e}); seguindo sem remover o fundo", file=sys.stderr)
        cut = img

rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])  # 0 = fundo

# 2 + 3. suaviza e realça contraste local
try:
    import cv2
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    smooth = gray
    for _ in range(SMOOTH):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(8, 8))
    tone = clahe.apply(smooth)
except Exception as e:
    print(f"opencv indisponível ({e}); usando autocontraste do Pillow", file=sys.stderr)
    tone = np.array(ImageOps.autocontrast(Image.fromarray(rgb).convert("L"), cutoff=2))

# 3b. linhas finas escuras sobre claro (diferença de gaussianas) -> escurece
if LINES > 0:
    try:
        import cv2
        fine = cv2.GaussianBlur(tone, (0, 0), 1.2).astype(np.float32)
        coarse = cv2.GaussianBlur(tone, (0, 0), 5.0).astype(np.float32)
        ridges = np.clip((coarse - fine) / 40.0, 0, 1)
        tone = (np.clip(tone.astype(np.float32) / 255.0 - LINES * ridges, 0, 1) * 255).astype(np.uint8)
    except Exception as e:
        print(f"realce de linhas pulado ({e})", file=sys.stderr)

# 4. estica os tons só sobre a pessoa e compõe sobre branco
subj = alpha > 128
lo, hi = (np.percentile(tone[subj], [LO, HI]) if subj.any() else (tone.min(), tone.max()))
out = np.clip((tone.astype(np.float32) - lo) / max(float(hi - lo), 1.0), 0, 1) * 255

mask = alpha.astype(np.float32) / 255.0
try:
    import cv2
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
except Exception:
    pass
out = out * mask + float(BGCOL) * (1.0 - mask)

# 5. recorte quadrado ao redor da pessoa (ou só da cabeça, com HEAD_FRAC < 1)
ys, xs = np.where(alpha > 20)
if len(xs) == 0:
    ys, xs = np.where(np.ones_like(alpha, dtype=bool))
y_min, y_max = int(ys.min()), int(ys.max())
if HEAD_FRAC < 1.0:
    y_max = y_min + int((y_max - y_min) * HEAD_FRAC)
    band = ys <= y_max
    ys, xs = ys[band], xs[band]
x_min, x_max = int(xs.min()), int(xs.max())
side = int(max(x_max - x_min, y_max - y_min) + PAD * 2)
cx, cy = (x_min + x_max) // 2, (y_min + y_max) // 2
canvas = np.full((side, side), BGCOL, np.uint8)
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

# 6. esmaece a base pro fundo (evita o corte seco no pescoço/colarinho)
if FADE > 0:
    n = int(side * FADE)
    if n > 1:
        ramp = (1 - np.cos(np.linspace(0, np.pi, n))) / 2        # 0 -> 1, suave
        band = canvas[side - n:, :].astype(np.float32)
        band = band * (1 - ramp[:, None]) + float(BGCOL) * ramp[:, None]
        canvas[side - n:, :] = band.astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print("gravado", OUT, canvas.shape)
