#!/usr/bin/env python3
"""
Converte o retrato preparado (prep_photo.py) num SVG de ASCII art LIMPO e
monocromático (uma cor cinza-clara, pessoa isolada sobre fundo escuro) que se
"digita" sozinho como num terminal e depois congela.

Monocromático de propósito: colorir cada caractere é o que deixa retrato ASCII
parecendo chuvisco. Uma cor + uma boa rampa de densidade + contraste alto (o
fundo vira espaço em branco) fica limpo e legível.

O GitHub renderiza SVG embutido via <img> e roda as animações SMIL (JS não).
Cada linha é revelada com um recorte da esquerda pra direita e um cursor de
bloco acompanhando a borda, escalonado de cima pra baixo.

    python scripts/make_ascii_svg.py [entrada.png] [saida.svg]

Variáveis: COLS=150 GAMMA=1.18 WHITE_FLOOR=0.80 CONTRAST=1.05 STATIC=1 INVERT=1 DITHER=1 RAMP="..." INK="#hex"
(GAMMA < 1 clareia os meios-tons -> pele mais vazada; GAMMA > 1 escurece)
"""
import html
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "portrait", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "jose-ascii.svg")

TITLE = os.environ.get("ASCII_TITLE", "jose@jztech: ~$ ./portrait.sh")
PROMPT = "jose@jztech:~$ whoami"
NAME = "José Luiz"

# mais colunas = mais detalhe (os olhos precisam de ~6+ caracteres de largura).
# a arte tem sempre ART_W px de largura; as células encolhem mantendo ~1:1.875.
COLS = int(os.environ.get("COLS", 150))
ART_W_TARGET = 800
CELL_W = ART_W_TARGET / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round(COLS * 8 / 15)
RAMP = os.environ.get("RAMP", " .`:-=+*cs#%@")  # claro (esparso) -> escuro (denso); o espaço inicial limpa o fundo
DITHER = bool(os.environ.get("DITHER"))  # Floyd-Steinberg: espalha o erro de quantização, tons mais suaves

CONTRAST = float(os.environ.get("CONTRAST", 1.05))
BRIGHTNESS = float(os.environ.get("BRIGHTNESS", 1.0))
GAMMA = float(os.environ.get("GAMMA", 1.18))        # >1 clareia os meios-tons
SHARPEN = bool(os.environ.get("SHARPEN"))
WHITE_FLOOR = float(os.environ.get("WHITE_FLOOR", 0.80))  # acima disso vira espaço
INVERT = bool(os.environ.get("INVERT"))  # positivo: claro = denso; exige foto preparada com BG=black

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = os.environ.get("INK", "#c9d1d9")
CURSOR = "#c9d1d9"

ROW_DUR = 5.8 / ROWS   # o retrato inteiro imprime em ~6s em qualquer resolução
STAGGER = ROW_DUR      # == ROW_DUR -> um único cursor varrendo de cima pra baixo

# ---- 1. amostra a imagem numa grade COLS x ROWS em cinza --------------------
im = Image.open(SRC).convert("L")
if SHARPEN:
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

STATIC = bool(os.environ.get("STATIC"))  # quadro congelado pra preview

# luminância já com gama (e invertida, se for o caso), em [0,1]
lum_grid = []
for y in range(ROWS):
    row = []
    for x in range(COLS):
        lum = pow(px[x, y] / 255.0, GAMMA)
        if INVERT:
            lum = 1.0 - lum
        row.append(lum)
    lum_grid.append(row)

N = len(RAMP) - 1
rows_txt = []
if DITHER:
    # Floyd-Steinberg sobre o valor de "tinta" v = (1-lum)*N; o fundo (acima do piso branco)
    # vira espaço e não recebe nem espalha erro, pra continuar limpo.
    ink = [[(1.0 - l) * N for l in row] for row in lum_grid]
    bg = [[l >= WHITE_FLOOR for l in row] for row in lum_grid]
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            if bg[y][x]:
                chars.append(" ")
                continue
            v = ink[y][x]
            q = max(0, min(N, int(v + 0.5)))
            err = v - q
            chars.append(RAMP[q])
            for dx, dy, w in ((1, 0, 7 / 16), (-1, 1, 3 / 16), (0, 1, 5 / 16), (1, 1, 1 / 16)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < COLS and 0 <= yy < ROWS and not bg[yy][xx]:
                    ink[yy][xx] += err * w
        rows_txt.append("".join(chars))
else:
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = lum_grid[y][x]
            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * N + 0.5)
            chars.append(RAMP[max(0, min(N, idx))])
        rows_txt.append("".join(chars))

art_top = TITLEBAR_H + PAD * 0.35

# ---- 2. monta o SVG ----------------------------------------------------------
parts = ['<?xml version="1.0" encoding="UTF-8"?>']
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W:.0f}" height="{CANVAS_H:.0f}" '
    f'viewBox="0 0 {CANVAS_W:.0f} {CANVAS_H:.0f}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')

parts.append(f'<rect width="{CANVAS_W:.0f}" height="{CANVAS_H:.0f}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1:.0f}" height="{CANVAS_H-1:.0f}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W:.0f}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2:.0f}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">{html.escape(TITLE)}</text>')

# um <text> por linha (uma cor só -> sem marcação por caractere, arquivo pequeno)
font_size = CELL_H * 0.86
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.74
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = html.escape(line)
    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W:.0f}" lengthAdjust="spacing">{safe}</text>')

    if STATIC:
        parts.append(text)
        continue

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.2f}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W:.0f}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.3f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W:.2f}" height="{CELL_H-2:.2f}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W:.0f}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.3f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

# barra de status com cursor piscando
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W:.0f}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'{html.escape(PROMPT)} <tspan fill="{INK}">{html.escape(NAME)}</tspan></text>')
status_chars = len(f"{PROMPT} {NAME} ")
parts.append(f'<rect x="{PAD + status_chars * 13 * 0.6:.1f}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{CANVAS_W:.0f} x {CANVAS_H:.0f}", f"({COLS}x{ROWS} chars)")
