#!/usr/bin/env python3
"""
Card estilo neofetch pro perfil: um painel de terminal com pares chave/valor
(quem sou, stack, o que estou fazendo), os quadradinhos de paleta do neofetch e
um prompt com cursor piscando.

Canvas 840x880, igual ao retrato ASCII, pra que larguras iguais no README deem
alturas iguais lado a lado. Cada linha entra com fade + deslize em sequência
(CSS keyframes, que o GitHub roda dentro de <img>; JS nunca).

    python scripts/make_info_card.py [saida.svg]
    STATIC=1 python scripts/make_info_card.py   # quadro congelado pra preview
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 840, 880
PAD = 40
TITLEBAR_H = 30

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK = "#7d8590", "#e6edf3"
KEY = "#22d3ee"
USER_C, HOST_C = "#39d353", "#f2cc60"
SWATCHES = ["#ff5f56", "#ffbd2e", "#27c93f", "#22d3ee", "#58a6ff", "#bc8cff", "#f778ba", "#e6edf3"]

TITLE = "jose@jztech: ~$ neofetch"
USER, HOST = "jose", "jztech"

# (chave, valor). Chave vazia = continuação da linha anterior.
ROWS = [
    ("Nome",      "José Luiz"),
    ("Função",    "Full Stack Dev · TI & Infra"),
    ("Empresa",   "JZ TECH"),
    ("Curso",     "ADS · UniFAAT · 2º ano"),
    ("Stack",     "Next.js · React · TypeScript"),
    ("",          "Supabase · PostgreSQL · Python"),
    ("Infra",     "Docker · Nginx · Linux"),
    ("",          "Vercel · Cloudflare"),
    ("Automação", "Playwright · Bash · GitHub Actions"),
    ("Fazendo",   "Ápice Hub · Otto · Jarvis"),
    ("Uptime",    "19 anos · Brasil"),
    ("Shell",     "zsh · VS Code · Git"),
]

FONT = 26        # px no canvas de 840 -> ~13px exibido a 420 de largura
LINE_H = 48
KEY_W = 230      # largura da coluna das chaves
STAGGER = 0.11
DUR = 0.45


def esc(s):
    return html.escape(s)


def group(delay):
    if STATIC:
        return '<g>'
    return f'<g class="l" style="animation-delay:{delay:.2f}s">'


css = (
    f'.l{{opacity:0;animation:in {DUR}s ease-out both}}'
    '@keyframes in{0%{opacity:0;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}'
    '@media (prefers-reduced-motion: reduce){.l{opacity:1;animation:none}}'
)

parts = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f'<style>{css}</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{20 + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{esc(TITLE)}</text>')

y = TITLEBAR_H + PAD + FONT
n = 0

# cabeçalho user@host + régua
parts.append(group(n * STAGGER))
parts.append(f'<text x="{PAD}" y="{y}" font-size="{FONT}" font-weight="700">'
             f'<tspan fill="{USER_C}">{USER}</tspan><tspan fill="{MUTED}">@</tspan>'
             f'<tspan fill="{HOST_C}">{HOST}</tspan></text>')
parts.append('</g>')
n += 1
y += LINE_H * 0.8
parts.append(group(n * STAGGER))
parts.append(f'<line x1="{PAD}" y1="{y - FONT*0.35:.1f}" x2="{PAD + (len(USER)+1+len(HOST)) * FONT * 0.6:.1f}" '
             f'y2="{y - FONT*0.35:.1f}" stroke="{MUTED}" stroke-width="2"/>')
parts.append('</g>')
n += 1
y += LINE_H * 0.9

# pares chave/valor
for key, val in ROWS:
    parts.append(group(n * STAGGER))
    if key:
        parts.append(f'<text x="{PAD}" y="{y:.1f}" font-size="{FONT}" font-weight="700" fill="{KEY}">{esc(key)}</text>')
    parts.append(f'<text x="{PAD + KEY_W}" y="{y:.1f}" font-size="{FONT}" fill="{INK}" xml:space="preserve">{esc(val)}</text>')
    parts.append('</g>')
    n += 1
    y += LINE_H

# paleta do neofetch
y += LINE_H * 0.25
sw = 36
parts.append(group(n * STAGGER))
for i, color in enumerate(SWATCHES):
    parts.append(f'<rect x="{PAD + i*(sw+6)}" y="{y - sw:.1f}" width="{sw}" height="{sw}" rx="4" fill="{color}"/>')
parts.append('</g>')
n += 1
y += LINE_H * 1.3

# prompt final com cursor piscando
parts.append(group(n * STAGGER))
prompt = f"{USER}@{HOST}:~$ "
parts.append(f'<text x="{PAD}" y="{y:.1f}" font-size="{FONT}" fill="{MUTED}" xml:space="preserve">'
             f'<tspan fill="{USER_C}">{USER}</tspan>@<tspan fill="{HOST_C}">{HOST}</tspan>:~$ </text>')
cx = PAD + len(prompt) * FONT * 0.6
parts.append(f'<rect x="{cx:.1f}" y="{y - FONT*0.85:.1f}" width="{FONT*0.6:.1f}" height="{FONT*1.05:.1f}" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')
parts.append('</g>')

parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{W} x {H};", "última linha em y =", round(y))
