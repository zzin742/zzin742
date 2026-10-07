#!/usr/bin/env python3
"""
Painel de terminal com a stack: a saída de `cat stack.txt`, com cada seção como um
comentário e cada tecnologia como um chip escuro. Os chips entram em cascata (CSS
keyframes, que o GitHub roda dentro de <img>). Mesma largura do heatmap, pra alinhar.

    python scripts/make_stack_svg.py [saida.svg]
    STATIC=1 python scripts/make_stack_svg.py   # quadro congelado pra preview
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "stack.svg")
STATIC = bool(os.environ.get("STATIC"))

W = 869
PAD = 22
TITLEBAR_H = 30
TITLE = "jose@jztech: ~$ cat stack.txt"

BG, BG2, FRAME = "#0a0e14", "#0d1420", "#1f6feb"
CHIP, CHIP_LINE = "#161b22", "#30363d"
MUTED, INK, ACCENT = "#7d8590", "#e6edf3", "#d2ff00"

SECTIONS = [
    ("front-end", ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "Sass"]),
    ("back-end e dados", ["Node.js", "Python", "Supabase", "PostgreSQL", "Prisma", "Redis"]),
    ("automação e infra", ["Playwright", "Linux", "Docker", "Nginx", "Bash", "Vercel", "Cloudflare", "GitHub Actions", "Redes e servidores"]),
    ("ferramentas", ["Git", "GitHub", "VS Code", "Figma", "Notion", "Postman"]),
]

FONT = 13
CHAR_W = FONT * 0.6
CHIP_H = 26
CHIP_PAD = 11
GAP = 8
ROW_H = 34
LABEL_H = 24
SECTION_GAP = 10
STAGGER = 0.035


def esc(s):
    return html.escape(s)


body = []
y = TITLEBAR_H + 26
n = 0
max_x = W - PAD
for label, items in SECTIONS:
    delay = n * STAGGER
    cls = '' if STATIC else f' class="l" style="animation-delay:{delay:.2f}s"'
    body.append(f'<text{cls} x="{PAD}" y="{y + 12}" font-size="12.5" fill="{ACCENT}">{esc("# " + label)}</text>')
    n += 1
    y += LABEL_H
    x = PAD
    for item in items:
        w = round(len(item) * CHAR_W + CHIP_PAD * 2)
        if x + w > max_x:
            x = PAD
            y += ROW_H
        delay = n * STAGGER
        cls = '' if STATIC else f' class="c" style="animation-delay:{delay:.2f}s"'
        body.append(
            f'<g{cls}><rect x="{x}" y="{y}" width="{w}" height="{CHIP_H}" rx="6" fill="{CHIP}" stroke="{CHIP_LINE}"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + CHIP_H * 0.68:.1f}" font-size="{FONT}" fill="{INK}" text-anchor="middle">{esc(item)}</text></g>'
        )
        x += w + GAP
        n += 1
    y += ROW_H + SECTION_GAP

H = y + 4

css = (
    '.l{opacity:0;animation:in .4s ease-out both}'
    '.c{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,.8,.2,1) both}'
    '@keyframes in{to{opacity:1}}'
    '@keyframes pop{0%{opacity:0;transform:scale(.85) translateY(4px)}100%{opacity:1;transform:none}}'
    '@media (prefers-reduced-motion: reduce){.l,.c{opacity:1;animation:none}}'
)

parts = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f'<style>{css}</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.55"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(TITLE)}</text>')
parts.extend(body)
parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("gravado", OUT, len(svg), "bytes;", f"{W} x {H}")
