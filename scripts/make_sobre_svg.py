#!/usr/bin/env python3
"""
Painel de terminal com o texto "sobre": a saída de `cat sobre.txt`, digitada linha a linha
(SMIL, que o GitHub roda dentro de <img>). A última frase, a do robô, vai em destaque.

    python scripts/make_sobre_svg.py [saida.svg]
    STATIC=1 python scripts/make_sobre_svg.py   # quadro congelado pra preview
"""
import html
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "sobre.svg")
STATIC = bool(os.environ.get("STATIC"))

W = 869
PAD = 22
TITLEBAR_H = 30
TITLE = "jose@jztech: ~$ cat sobre.txt"

BG, BG2, FRAME = "#0a0e14", "#0d1420", "#1f6feb"
MUTED, INK, ACCENT = "#7d8590", "#e6edf3", "#d2ff00"

PARAGRAFOS = [
    "Sou desenvolvedor full stack e responsável pelo TI de uma empresa. Estudo Análise e "
    "Desenvolvimento de Sistemas na UniFAAT, no segundo ano.",
    "Também construo fora do trabalho: loja com pagamento, app de finanças, página de casal e "
    "assistente de voz. Em cada um faço a interface, o banco e o deploy, e entrego no ar.",
    "Quando uma rotina é repetitiva demais para ocupar uma pessoa, eu escrevo um robô.",
]

FONT = 14
CHAR_W = FONT * 0.6
LINE_H = 25
COLS = int((W - PAD * 2) / CHAR_W)   # ~96 caracteres por linha
LINE_DUR = 0.3


def esc(s):
    return html.escape(s)


lines = []  # (texto, cor)
for i, par in enumerate(PARAGRAFOS):
    cor = ACCENT if i == len(PARAGRAFOS) - 1 else INK
    for ln in textwrap.wrap(par, COLS):
        lines.append((ln, cor))
    lines.append(("", INK))
lines.pop()

H = TITLEBAR_H + 24 + len(lines) * LINE_H + 24

parts = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.55"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(TITLE)}</text>')

y0 = TITLEBAR_H + 24
k = 0
for i, (txt, cor) in enumerate(lines):
    if not txt:
        continue
    top = y0 + i * LINE_H
    base = top + LINE_H * 0.72
    text = f'<text xml:space="preserve" x="{PAD}" y="{base:.1f}" font-size="{FONT}" fill="{cor}">{esc(txt)}</text>'
    if STATIC:
        parts.append(text)
        continue
    delay = k * LINE_DUR
    k += 1
    parts.append(
        f'<clipPath id="s{i}"><rect x="{PAD}" y="{top}" height="{LINE_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{W - PAD * 2}" begin="{delay:.2f}s" dur="{LINE_DUR:.2f}s" fill="freeze"/>'
        f'</rect></clipPath><g clip-path="url(#s{i})">{text}</g>'
    )

# cursor depois da última frase
last_i = len(lines) - 1
last_txt = lines[last_i][0]
cx = PAD + round((len(last_txt) + 1) * CHAR_W)
cy = y0 + last_i * LINE_H + 4
begin = "" if STATIC else f' begin="{k * LINE_DUR:.2f}s"'
parts.append(f'<rect x="{cx}" y="{cy}" width="8" height="16" fill="{INK}" opacity="{1 if STATIC else 0}">'
             + ("" if STATIC else f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"{begin}/>')
             + '</rect>')
parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{W} x {H};", len(lines), "linhas")
