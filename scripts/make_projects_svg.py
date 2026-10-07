#!/usr/bin/env python3
"""
Painel de terminal com os projetos: a saída de `ls ~/projetos`, uma linha por projeto com
status (no ar / código aberto), nome, o que é e o endereço, digitada linha a linha (SMIL, que
o GitHub roda dentro de <img>), e um botão pro portfólio. No README a imagem inteira é um link.

    python scripts/make_projects_svg.py [saida.svg]
    STATIC=1 python scripts/make_projects_svg.py   # quadro congelado pra preview
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "projects.svg")
STATIC = bool(os.environ.get("STATIC"))

W = 869
PAD = 22
TITLEBAR_H = 30
TITLE = "jose@jztech: ~$ ls ~/projetos"

BG, BG2, FRAME = "#0a0e14", "#0d1420", "#1f6feb"
MUTED, INK, ACCENT, CYAN = "#7d8590", "#e6edf3", "#d2ff00", "#22d3ee"
LIVE, CODE = "#3fb950", "#bc8cff"

# (status, pasta, o que é, endereço) — descrição com até 34 caracteres
PROJECTS = [
    ("live", "london-fog/", "loja virtual de calçados", "londonfogoficial.com.br"),
    ("live", "apice-contabilidade/", "site institucional do escritório", "apicecontabilidade.cnt.br"),
    ("live", "otto/", "finanças pessoais com IA", "otto-one-snowy.vercel.app"),
    ("code", "attentionguard/", "sonolência e atenção, por webcam", "github.com/zzin742/AttentionGuard"),
    ("code", "meus-bots/", "automação em Python do dia a dia", "github.com/zzin742/meus-bots"),
]
PORTFOLIO = "joseluiz.dev.br/#projetos"
BUTTON = "abrir o portfólio ↗"

FONT = 13
CHAR_W = FONT * 0.6
LINE_H = 26
X_DOT = PAD + 4
X_NAME = PAD + 20
X_DESC = X_NAME + round(22 * CHAR_W)
X_URL = X_DESC + round(36 * CHAR_W)
LINE_DUR = 0.4


def esc(s):
    return html.escape(s)


# linhas: lista de segmentos (x, texto, cor, peso); None = ponto de status
lines = []
lines.append([(X_NAME - 20, f"total {len(PROJECTS)}", MUTED, "400")])
for status, name, desc, url in PROJECTS:
    lines.append([("dot", status), (X_NAME, name, CYAN, "700"), (X_DESC, desc, INK, "400"), (X_URL, url, MUTED, "400")])
lines.append([])
lines.append([("dot", "live"), (X_NAME, "no ar", MUTED, "400"), ("dot2", "code"), (X_NAME + round(10 * CHAR_W), "código aberto", MUTED, "400")])

n_lines = len(lines)
H = TITLEBAR_H + 22 + n_lines * LINE_H + 22

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

y0 = TITLEBAR_H + 22
for i, segs in enumerate(lines):
    if not segs:
        continue
    top = y0 + i * LINE_H
    base = top + LINE_H * 0.7
    content = ""
    for seg in segs:
        if seg[0] == "dot":
            content += f'<circle cx="{X_DOT + 3}" cy="{base - 4.5:.1f}" r="4" fill="{LIVE if seg[1] == "live" else CODE}"/>'
        elif seg[0] == "dot2":
            content += f'<circle cx="{X_NAME + round(8.5 * CHAR_W)}" cy="{base - 4.5:.1f}" r="4" fill="{LIVE if seg[1] == "live" else CODE}"/>'
        else:
            x, t, c, w = seg
            content += f'<text xml:space="preserve" x="{x}" y="{base:.1f}" font-size="{FONT}" fill="{c}" font-weight="{w}">{esc(t)}</text>'
    if STATIC:
        parts.append(content)
        continue
    delay = i * LINE_DUR
    parts.append(
        f'<clipPath id="l{i}"><rect x="{PAD}" y="{top}" height="{LINE_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{W - PAD * 2}" begin="{delay:.2f}s" dur="{LINE_DUR:.2f}s" fill="freeze"/>'
        f'</rect></clipPath><g clip-path="url(#l{i})">{content}</g>'
    )

# botão "abrir o portfólio" no canto inferior direito, com o endereço ao lado
last_top = y0 + (n_lines - 1) * LINE_H
bw = round(len(BUTTON) * CHAR_W + 28)
bx, by, bh = W - PAD - bw, last_top - 2, 30
delay = n_lines * LINE_DUR
anim = "" if STATIC else f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
parts.append(f'<g opacity="{1 if STATIC else 0}">{anim}'
             f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" fill="#161b22" stroke="{ACCENT}" stroke-opacity="0.8"/>'
             f'<text x="{bx + bw / 2:.1f}" y="{by + 20}" font-size="{FONT}" font-weight="700" fill="{ACCENT}" text-anchor="middle">{esc(BUTTON)}</text>'
             f'<text x="{bx - 12}" y="{by + 20}" font-size="12" fill="{MUTED}" text-anchor="end">{esc(PORTFOLIO)}</text></g>')
parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{W} x {H}")
