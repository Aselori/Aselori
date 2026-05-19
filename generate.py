#!/usr/bin/env python3
"""Generate an animated SVG terminal for GitHub profile README."""

import base64

# ── Catppuccin Mocha palette ─────────────────────────────────
COLORS = {
    "bg":       "#1e1e2e",
    "fg":       "#cdd6f4",
    "overlay":  "#6c7086",
    "red":      "#f38ba8",
    "green":    "#a6e3a1",
    "yellow":   "#f9e2af",
    "blue":     "#89b4fa",
    "mauve":    "#cba6f7",
    "teal":     "#94e2d5",
    "peach":    "#fab387",
    "pink":     "#f5c2e7",
    "lavender": "#b4befe",
    "sky":      "#89dceb",
}

# ── User info ─────────────────────────────────────────────────
USER = "aselori"
HOST = "archlinux"

INFO_LINES = [
    ("Role",      "Web Developer",                    "peach"),
    ("Location",  "Monterrey, N.L., Mexico",          "pink"),
    ("Contact",   "aslopezrivas@gmail.com",           "lavender"),
    ("OS",        "Arch Linux",                       "blue"),
    ("Editor",    "Cursor / Neovim",                  "yellow"),
    ("Languages", "TypeScript, JavaScript, Python",   "green"),
    ("Frontend",  "Next.js, React, Tailwind CSS, Astro", "blue"),
    ("Backend",   "Node.js, Supabase, PostgreSQL",    "mauve"),
    ("Deploy",    "Vercel, Docker, GitHub Actions",   "teal"),
    ("Tools",     "Stripe, Figma, Postman, Playwright", "green"),
    ("Interest",  "AWS / Cloud Infrastructure",       "peach"),
]

# Pixel-art "AS" logo — each 1 = filled pixel
PIXEL_ART_A = [
    [0,1,1,1,0],
    [1,0,0,0,1],
    [1,0,0,0,1],
    [1,1,1,1,1],
    [1,0,0,0,1],
    [1,0,0,0,1],
    [1,0,0,0,1],
]
PIXEL_ART_S = [
    [0,1,1,1,1],
    [1,0,0,0,0],
    [1,0,0,0,0],
    [0,1,1,1,0],
    [0,0,0,0,1],
    [0,0,0,0,1],
    [1,1,1,1,0],
]
PIXEL_SIZE = 8
PIXEL_GAP = 2
LETTER_GAP = 14

PALETTE_COLORS = ["red", "green", "yellow", "blue", "mauve", "teal", "peach", "pink"]

# ── Layout ────────────────────────────────────────────────────
WIDTH = 880
LINE_H = 26
FONT_SIZE = 16
PAD_X = 24
PAD_Y = 20
ART_X = PAD_X + 10
INFO_X = 320
MAX_LABEL = max(len(label) for label, _, _ in INFO_LINES)

# ── Timing (milliseconds) ────────────────────────────────────
PROMPT_BLINK = 500
CHAR_DELAY = 70
TYPE_HOLD = 300
ART_DELAY = 80
INFO_HEADER_DELAY = 150
INFO_LINE_DELAY = 100
PALETTE_DELAY = 200


def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_svg():
    # Height: content + empty terminal space below (like a real terminal)
    info_lines_count = 2 + len(INFO_LINES)
    art_pixel_h = len(PIXEL_ART_A) * (PIXEL_SIZE + PIXEL_GAP)
    info_h = info_lines_count * LINE_H
    content_h = max(art_pixel_h, info_h)
    content_bottom = PAD_Y + LINE_H + 16 + content_h + 16 + 18 + 10
    height = content_bottom + 60  # content + some empty terminal space

    # ── Build timeline ────────────────────────────────────────
    t = 0

    # Prompt appears + cursor blink
    prompt_start = t
    t += PROMPT_BLINK

    # Typing "fastfetch"
    command = "fastfetch"
    type_start = t
    t += len(command) * CHAR_DELAY
    t += TYPE_HOLD

    # Fastfetch output
    ff_start = t

    # Header + separator
    header_start = t
    t += INFO_HEADER_DELAY

    # Info lines
    info_start = t
    t += len(INFO_LINES) * INFO_LINE_DELAY

    # Palette
    palette_start = t
    t += PALETTE_DELAY

    # Pixel art appears after all fastfetch output
    art_appear = t
    t += ART_DELAY

    total_duration = t

    # ── SVG output ────────────────────────────────────────────
    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">
<style>
  @keyframes blink {{ 0%,50% {{ opacity:1 }} 51%,100% {{ opacity:0 }} }}
  @keyframes fadeIn {{ from {{ opacity:0 }} to {{ opacity:1 }} }}

  .bg {{ fill: {COLORS["bg"]}; }}
  .t {{ font-family: ui-monospace, "Cascadia Mono", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: {FONT_SIZE}px; }}
  .cursor {{ animation: blink 1s step-end infinite; }}
''')

    # Main screen appears
    svg_parts.append(f'  .main-screen {{ opacity:0; animation: fadeIn 0.01s {prompt_start}ms forwards; }}')

    # Prompt
    svg_parts.append(f'  .prompt {{ opacity:0; animation: fadeIn 0.01s {prompt_start}ms forwards; }}')

    # Typed characters
    for i in range(len(command)):
        delay = type_start + i * CHAR_DELAY
        svg_parts.append(f'  .char-{i} {{ opacity:0; animation: fadeIn 0.01s {delay}ms forwards; }}')

    # Pixel art
    svg_parts.append(f'  .pixel-art {{ opacity:0; animation: fadeIn 0.15s {art_appear}ms forwards; }}')

    # Header + separator
    svg_parts.append(f'  .ff-header {{ opacity:0; animation: fadeIn 0.05s {header_start}ms forwards; }}')

    # Info lines
    for i in range(len(INFO_LINES)):
        delay = info_start + i * INFO_LINE_DELAY
        svg_parts.append(f'  .info-{i} {{ opacity:0; animation: fadeIn 0.05s {delay}ms forwards; }}')

    # Palette
    svg_parts.append(f'  .palette {{ opacity:0; animation: fadeIn 0.1s {palette_start}ms forwards; }}')

    svg_parts.append('</style>')

    # Background
    svg_parts.append(f'<rect class="bg" width="{WIDTH}" height="{height}" />')

    # ── Main screen ───────────────────────────────────────────
    svg_parts.append('<g class="main-screen">')

    # Prompt
    prompt_y = PAD_Y + FONT_SIZE
    svg_parts.append(f'  <text class="t prompt" x="{PAD_X}" y="{prompt_y}" fill="{COLORS["green"]}" font-weight="bold">❯ </text>')

    # Typed command
    prompt_w = 3  # "❯ " is ~3 chars wide
    for i, ch in enumerate(command):
        char_x = PAD_X + (prompt_w + i) * (FONT_SIZE * 0.6)
        svg_parts.append(f'  <text class="t char-{i}" x="{char_x}" y="{prompt_y}" fill="{COLORS["fg"]}">{ch}</text>')

    # Fastfetch content area
    ff_y_base = PAD_Y + LINE_H + 16

    # Embedded GIF image
    with open("/home/itami/Downloads/puck-wave.gif", "rb") as f:
        gif_b64 = base64.b64encode(f.read()).decode()
    img_w, img_h = 180, 150  # display size (scaled up from 120x100)
    img_x = ART_X
    img_y = ff_y_base + 10
    svg_parts.append(f'  <image class="pixel-art" x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}" href="data:image/gif;base64,{gif_b64}" />')

    # Header: user@host
    header_y = ff_y_base + FONT_SIZE
    svg_parts.append(f'  <text class="t ff-header" x="{INFO_X}" y="{header_y}">'
                     f'<tspan fill="{COLORS["blue"]}" font-weight="bold">{USER}</tspan>'
                     f'<tspan fill="{COLORS["fg"]}">@</tspan>'
                     f'<tspan fill="{COLORS["blue"]}" font-weight="bold">{HOST}</tspan>'
                     f'</text>')

    # Separator
    sep_y = ff_y_base + LINE_H + FONT_SIZE
    separator = "─" * 22
    svg_parts.append(f'  <text class="t ff-header" x="{INFO_X}" y="{sep_y}" fill="{COLORS["overlay"]}">{separator}</text>')

    # Info lines
    info_y_base = ff_y_base + LINE_H * 2
    for i, (label, value, color_name) in enumerate(INFO_LINES):
        y = info_y_base + i * LINE_H + FONT_SIZE
        color = COLORS[color_name]
        padded = label + " " * (MAX_LABEL - len(label))
        svg_parts.append(
            f'  <text class="t info-{i}" x="{INFO_X}" y="{y}">'
            f'<tspan fill="{color}" font-weight="bold">{escape_xml(padded)}</tspan>'
            f'<tspan fill="{COLORS["overlay"]}"> ~ </tspan>'
            f'<tspan fill="{COLORS["fg"]}">{escape_xml(value)}</tspan>'
            f'</text>'
        )

    # Color palette
    palette_y = info_y_base + len(INFO_LINES) * LINE_H + 16
    svg_parts.append('  <g class="palette">')
    block_size = 18
    gap = 8
    for i, color_name in enumerate(PALETTE_COLORS):
        bx = INFO_X + i * (block_size + gap)
        svg_parts.append(f'    <rect x="{bx}" y="{palette_y}" width="{block_size}" height="{block_size}" rx="3" fill="{COLORS[color_name]}" />')
    svg_parts.append('  </g>')

    svg_parts.append('</g>')
    svg_parts.append('</svg>')

    output = "/home/itami/Documents/Aselori/terminal.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"Generated {output}")


if __name__ == "__main__":
    generate_svg()
