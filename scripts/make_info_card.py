#!/usr/bin/env python3
"""
Card estilo neofetch pro perfil: logo "JZ" em pixels (no lugar do logo da distro), cabeçalho
user@host com tagline, pares chave/valor, a paleta de cores do neofetch e um prompt com cursor
piscando. A linha "GitHub" é viva: lê data/contributions.json (gerado todo dia pelo workflow).

Canvas 840x878, igual ao retrato ASCII, pra que larguras iguais no README deem alturas iguais.
Tudo anima com CSS keyframes, que o GitHub roda dentro de <img> (JS nunca).

    python scripts/make_info_card.py [saida.svg]
    STATIC=1 python scripts/make_info_card.py   # quadro congelado pra preview
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
DATA = os.path.join(HERE, "..", "data", "contributions.json")
STATIC = bool(os.environ.get("STATIC"))

W, H = 840, 878
PAD = 40
TITLEBAR_H = 30

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK = "#7d8590", "#e6edf3"
ACCENT = "#d2ff00"          # o verde-limão da marca JZ TECH
SWATCHES = ["#ff5f56", "#ffbd2e", "#27c93f", "#22d3ee", "#58a6ff", "#bc8cff", "#f778ba", "#e6edf3"]

TITLE = "jose@jztech: ~$ neofetch"
USER, HOST = "jose", "jztech"
TAGLINE = "Full Stack Dev · TI & Infra"
TAGLINE2 = "Sites, apps, sistemas e automação."

# logo em pixels (5x7)
J = ["#####", "....#", "....#", "....#", "#...#", "#...#", ".###."]
Z = ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"]
PX, PX_GAP, LETTER_GAP = 24, 3, 30


def br_num(n):
    return f"{n:,}".replace(",", ".")


# linha viva do GitHub
github_row = None
try:
    d = json.load(open(DATA, encoding="utf-8"))
    partes = []
    if d.get("public_repos"):
        partes.append(f'{d["public_repos"]} repos')
    if d.get("total_contributions"):
        partes.append(f'{br_num(d["total_contributions"])} contribuições')
    if partes:
        github_row = " · ".join(partes)
except Exception as e:
    print(f"sem dados do GitHub pro card ({e})", file=sys.stderr)

ROWS = [
    ("Nome", "José Luiz"),
    ("Empresa", "JZ TECH"),
    ("Curso", "ADS · UniFAAT · 2º ano"),
    ("Stack", "Next.js · React · TypeScript"),
    ("", "Supabase · PostgreSQL · Python"),
    ("Infra", "Docker · Nginx · Linux · Vercel"),
    ("Automação", "Playwright · Bash · GitHub Actions"),
    ("Fazendo", "Ápice Hub · Otto · Jarvis"),
]
if github_row:
    ROWS.append(("GitHub", github_row))
ROWS += [
    ("Uptime", "19 anos · Brasil"),
    ("Shell", "zsh · VS Code · Git"),
]

FONT = 24
LINE_H = 42
KEY_W = 200
ROW_START = 0.55     # segundos: quando as linhas começam
ROW_STAGGER = 0.09


def esc(s):
    return html.escape(s)


def g(cls, delay):
    if STATIC:
        return '<g>'
    return f'<g class="{cls}" style="animation-delay:{delay:.2f}s">'


css = (
    '.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s cubic-bezier(.2,.8,.2,1) both}'
    '.l{opacity:0;animation:in .45s ease-out both}'
    '@keyframes pop{0%{opacity:0;transform:scale(.3)}100%{opacity:1;transform:scale(1)}}'
    '@keyframes in{0%{opacity:0;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}'
    '@media (prefers-reduced-motion: reduce){.p,.l{opacity:1;animation:none}}'
)

parts = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f'<style>{css}</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{20 + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(TITLE)}</text>')

# ---- logo em pixels --------------------------------------------------------
cell = PX + PX_GAP
logo_x, logo_y = PAD, TITLEBAR_H + 28
x0 = logo_x
for letter in (J, Z):
    for r, row in enumerate(letter):
        for c, ch in enumerate(row):
            if ch != "#":
                continue
            x = x0 + c * cell
            y = logo_y + r * cell
            parts.append(g("p", 0.08 + (c + r) * 0.035))
            parts.append(f'<rect x="{x}" y="{y}" width="{PX}" height="{PX}" rx="4" fill="{ACCENT}"/>')
            parts.append('</g>')
    x0 += 5 * cell - PX_GAP + LETTER_GAP
logo_w = x0 - LETTER_GAP - logo_x
logo_h = 7 * cell - PX_GAP

# ---- cabeçalho ao lado do logo ---------------------------------------------
hx = logo_x + logo_w + 36
parts.append(g("l", 0.45))
parts.append(f'<text x="{hx}" y="{logo_y + 60}" font-size="34" font-weight="700">'
             f'<tspan fill="{ACCENT}">{USER}</tspan><tspan fill="{MUTED}">@</tspan><tspan fill="{INK}">{HOST}</tspan></text>')
parts.append(f'<text x="{hx}" y="{logo_y + 102}" font-size="22" fill="{INK}">{esc(TAGLINE)}</text>')
parts.append(f'<text x="{hx}" y="{logo_y + 136}" font-size="20" fill="{MUTED}">{esc(TAGLINE2)}</text>')
parts.append('</g>')

rule_y = logo_y + logo_h + 24
parts.append(g("l", 0.5))
parts.append(f'<line x1="{PAD}" y1="{rule_y}" x2="{W - PAD}" y2="{rule_y}" stroke="{FRAME}" stroke-width="2"/>')
parts.append('</g>')

# ---- pares chave/valor -------------------------------------------------------
y = rule_y + 44
for i, (key, val) in enumerate(ROWS):
    parts.append(g("l", ROW_START + i * ROW_STAGGER))
    if key:
        parts.append(f'<text x="{PAD}" y="{y}" font-size="{FONT}" font-weight="700" fill="{ACCENT}">{esc(key)}</text>')
    parts.append(f'<text x="{PAD + KEY_W}" y="{y}" font-size="{FONT}" fill="{INK}" xml:space="preserve">{esc(val)}</text>')
    parts.append('</g>')
    y += LINE_H

# ---- paleta -------------------------------------------------------------------
y += 2
sw = 34
parts.append(g("l", ROW_START + len(ROWS) * ROW_STAGGER))
for i, color in enumerate(SWATCHES):
    parts.append(f'<rect x="{PAD + i * (sw + 6)}" y="{y}" width="{sw}" height="{sw}" rx="4" fill="{color}"/>')
parts.append('</g>')
y += sw + 44

# ---- prompt com cursor ----------------------------------------------------
parts.append(g("l", ROW_START + (len(ROWS) + 1) * ROW_STAGGER))
prompt = f"{USER}@{HOST}:~$ "
parts.append(f'<text x="{PAD}" y="{y}" font-size="{FONT}" fill="{MUTED}" xml:space="preserve">'
             f'<tspan fill="{ACCENT}">{USER}</tspan>@<tspan fill="{INK}">{HOST}</tspan>:~$ </text>')
cx = PAD + len(prompt) * FONT * 0.6
parts.append(f'<rect x="{cx:.1f}" y="{y - FONT * 0.85:.1f}" width="{FONT * 0.6:.1f}" height="{FONT * 1.05:.1f}" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')
parts.append('</g>')

parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{W} x {H};", "última linha em y =", round(y), "| GitHub:", github_row)
