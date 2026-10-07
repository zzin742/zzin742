#!/usr/bin/env python3
"""
Painel de terminal com os projetos: a saída de `ls -la ~/projetos`, uma linha por projeto
(nome, o que é, endereço), digitada linha a linha (SMIL, que o GitHub roda dentro de <img>).
No README a imagem inteira é um link pro portfólio.

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
TITLE = "jose@jztech: ~$ ls -la ~/projetos"

BG, BG2, FRAME = "#0a0e14", "#0d1420", "#1f6feb"
MUTED, INK, ACCENT, CYAN = "#7d8590", "#e6edf3", "#d2ff00", "#22d3ee"

# (pasta, o que é, endereço) — descrição com até 34 caracteres
PROJECTS = [
    ("london-fog/", "loja virtual de calçados", "londonfogoficial.com.br"),
    ("apice-contabilidade/", "site institucional do escritório", "apicecontabilidade.cnt.br"),
    ("otto/", "finanças pessoais com IA", "otto-one-snowy.vercel.app"),
    ("attentionguard/", "sonolência e atenção, por webcam", "github.com/zzin742/AttentionGuard"),
    ("meus-bots/", "automação em Python do dia a dia", "github.com/zzin742/meus-bots"),
]
PORTFOLIO = "joseluiz.dev.br/#projetos"

FONT = 13
CHAR_W = FONT * 0.6
LINE_H = 26
X_PERM = PAD
X_NAME = PAD + round(12 * CHAR_W)
X_DESC = X_NAME + round(22 * CHAR_W)
X_URL = X_DESC + round(36 * CHAR_W)
LINE_DUR = 0.45


def esc(s):
    return html.escape(s)


lines = []  # cada linha: lista de (x, texto, cor, peso)
lines.append([(X_PERM, f"total {len(PROJECTS)}", MUTED, "400")])
for name, desc, url in PROJECTS:
    lines.append([(X_PERM, "drwxr-xr-x", MUTED, "400"), (X_NAME, name, CYAN, "700"),
                  (X_DESC, desc, INK, "400"), (X_URL, url, MUTED, "400")])
lines.append([])
lines.append([(X_PERM, "→ todos os projetos em", ACCENT, "400"),
              (X_PERM + round(23 * CHAR_W), PORTFOLIO, ACCENT, "700"),
              (X_PERM + round((23 + len(PORTFOLIO) + 2) * CHAR_W), "(clique aqui no painel)", MUTED, "400")])

H = TITLEBAR_H + 22 + len(lines) * LINE_H + 22

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
    texts = "".join(f'<text xml:space="preserve" x="{x}" y="{base:.1f}" font-size="{FONT}" fill="{c}" font-weight="{w}">{esc(t)}</text>'
                    for x, t, c, w in segs)
    if STATIC:
        parts.append(texts)
        continue
    delay = i * LINE_DUR
    parts.append(
        f'<clipPath id="l{i}"><rect x="{PAD}" y="{top}" height="{LINE_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{W - PAD * 2}" begin="{delay:.2f}s" dur="{LINE_DUR:.2f}s" fill="freeze"/>'
        f'</rect></clipPath><g clip-path="url(#l{i})">{texts}</g>'
    )

# cursor piscando no fim
last_top = y0 + (len(lines) - 1) * LINE_H
cx = X_PERM + round((23 + len(PORTFOLIO) + 2 + len("(clique aqui no painel)") + 1) * CHAR_W)
begin = "" if STATIC else f' begin="{len(lines) * LINE_DUR:.2f}s"'
parts.append(f'<rect x="{cx}" y="{last_top + 5}" width="8" height="15" fill="{INK}" opacity="{1 if STATIC else 0}">'
             + ("" if STATIC else f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"{begin}/>')
             + '</rect>')
parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{W} x {H}")
