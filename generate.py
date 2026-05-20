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
USER = "Aselori"
BRANCH = "looking-for-j*b"

SECTIONS = [
    {
        "title": "About",
        "color": "blue",
        "lines": [
            ("Role",     "Software Engineer, mostly Web", "peach"),
            ("OS",       "Arch Linux",              "blue"),
            ("Location", "Monterrey, N.L., Mexico", "pink"),
            ("Contact",  "aslopezrivas@gmail.com",  "lavender"),
        ],
    },
    {
        "title": "Main Stack",
        "color": "green",
        "lines": [
            ("Editor",    "Cursor / Neovim",                     "yellow"),
            ("Languages", "TypeScript, JavaScript, Python",      "green"),
            ("Frontend",  "Next.js, React, Tailwind CSS, Astro", "blue"),
            ("Backend",   "Node.js, Express",                    "mauve"),
            ("Database",  "Supabase, PostgreSQL, Prisma",        "sky"),
            ("Deploy",    "Vercel, Docker, GitHub Actions",      "teal"),
            ("Tools",     "Stripe, Figma, Postman, Playwright",  "green"),
            ("",          "",                                    ""),
            ("Interest",  "AWS / Cloud Infrastructure",          "peach"),
        ],
    },
]

PALETTE_COLORS = ["red", "green", "yellow", "blue", "mauve", "teal", "peach", "pink"]

# ── Layout ────────────────────────────────────────────────────
WIDTH = 880
LINE_H = 22
FONT_SIZE = 14
CHAR_W = FONT_SIZE * 0.6
PAD_X = 24
PAD_Y = 20
ART_X = PAD_X + 10
INFO_X = 320

ALL_LABELS = [l for sec in SECTIONS for l, _, _ in sec["lines"] if l]
MAX_LABEL = max(len(l) for l in ALL_LABELS)

# ── Timing (milliseconds) ────────────────────────────────────
PROMPT_BLINK = 500
CHAR_DELAY = 70
TYPE_HOLD = 300
INFO_LINE_DELAY = 80
PALETTE_DELAY = 150


def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_box_lines(title, lines, max_label, border_color_name, box_width=None):
    """Build fastfetch-style bordered section with centered title."""
    content_width = max_label + 3 + max(len(v) for _, v, _ in lines if v)
    box_inner = box_width if box_width else max(content_width, len(title) + 4)

    border_col = COLORS[border_color_name]
    result = []

    # Centered title: ╭──── Title ────╮
    pad_total = box_inner - len(title) - 2
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left
    top = "╭" + "─" * pad_left + " " + title + " " + "─" * pad_right + "╮"
    result.append(("border", top, border_col))

    for label, value, color_name in lines:
        if not label and not value:
            result.append(("blank", "", ""))
            continue
        padded = label + " " * (MAX_LABEL - len(label))
        result.append(("line", (padded, value, color_name), border_col))

    bottom = "╰" + "─" * (box_inner + 2) + "╯"
    result.append(("border", bottom, border_col))

    return result


def generate_svg():
    # Compute shared box width across all sections
    shared_width = 0
    for sec in SECTIONS:
        content_w = MAX_LABEL + 3 + max(len(v) for _, v, _ in sec["lines"] if v)
        title_w = len(sec["title"]) + 4
        shared_width = max(shared_width, content_w, title_w)

    # Build all section rows to compute height
    all_rows = []
    for sec in SECTIONS:
        rows = build_box_lines(sec["title"], sec["lines"], MAX_LABEL, sec["color"], shared_width)
        all_rows.extend(rows)
        all_rows.append(("gap", "", ""))

    total_info_lines = len(all_rows)
    info_h = total_info_lines * LINE_H
    content_bottom = PAD_Y + LINE_H + 16 + info_h + 16 + 18 + 10
    height = content_bottom + 40

    # ── Build timeline ────────────────────────────────────────
    t = 0

    prompt_start = t
    t += PROMPT_BLINK

    command = "fastfetch"
    type_start = t
    t += len(command) * CHAR_DELAY
    t += TYPE_HOLD

    ff_start = t
    art_appear = t

    info_start = t
    t += total_info_lines * INFO_LINE_DELAY

    palette_start = t
    t += PALETTE_DELAY

    # ── SVG output ────────────────────────────────────────────
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">')
    s.append('<style>')
    s.append(f'  @keyframes blink {{ 0%,50% {{ opacity:1 }} 51%,100% {{ opacity:0 }} }}')
    s.append(f'  @keyframes fadeIn {{ from {{ opacity:0 }} to {{ opacity:1 }} }}')
    s.append(f'  .bg {{ fill: {COLORS["bg"]}; }}')
    s.append(f'  .t {{ font-family: ui-monospace, "Cascadia Mono", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: {FONT_SIZE}px; }}')
    s.append(f'  .cursor {{ animation: blink 1s step-end infinite; }}')

    s.append(f'  .main-screen {{ opacity:0; animation: fadeIn 0.01s {prompt_start}ms forwards; }}')
    s.append(f'  .prompt {{ opacity:0; animation: fadeIn 0.01s {prompt_start}ms forwards; }}')

    for i in range(len(command)):
        delay = type_start + i * CHAR_DELAY
        s.append(f'  .char-{i} {{ opacity:0; animation: fadeIn 0.01s {delay}ms forwards; }}')

    s.append(f'  .pixel-art {{ opacity:0; animation: fadeIn 0.15s {art_appear}ms forwards; }}')

    for i in range(total_info_lines):
        delay = info_start + i * INFO_LINE_DELAY
        s.append(f'  .info-{i} {{ opacity:0; animation: fadeIn 0.05s {delay}ms forwards; }}')

    s.append(f'  .palette {{ opacity:0; animation: fadeIn 0.1s {palette_start}ms forwards; }}')

    s.append('</style>')

    # Background
    s.append(f'<rect class="bg" width="{WIDTH}" height="{height}" />')

    # ── Main screen ───────────────────────────────────────────
    s.append('<g class="main-screen">')

    # Prompt: Aselori looking-for-j*b ● ? ❯ fastfetch
    prompt_y = PAD_Y + FONT_SIZE
    prompt_str = f"{USER} {BRANCH}"
    prompt_after = " ) "
    symbols = [
        (len(prompt_str), "●", COLORS["green"]),
        (len(prompt_str) + 2, "?", COLORS["yellow"]),
    ]

    # Render full prompt as one <text> with tspans for coloring
    px = PAD_X
    s.append(
        f'  <text class="t prompt" x="{px}" y="{prompt_y}">'
        f'<tspan fill="{COLORS["teal"]}" font-weight="bold">{USER}</tspan>'
        f'<tspan fill="{COLORS["fg"]}"> </tspan>'
        f'<tspan fill="{COLORS["mauve"]}">{BRANCH}</tspan>'
        f'<tspan fill="{COLORS["fg"]}"> </tspan>'
        f'<tspan fill="{COLORS["green"]}">●</tspan>'
        f'<tspan fill="{COLORS["fg"]}"> </tspan>'
        f'<tspan fill="{COLORS["yellow"]}">?</tspan>'
        f'<tspan fill="{COLORS["fg"]}"> ) </tspan>'
        f'</text>'
    )
    prompt_total_chars = len(USER) + 1 + len(BRANCH) + len(" ● ? ) ")
    px = PAD_X + prompt_total_chars * CHAR_W

    for i, ch in enumerate(command):
        char_x = px + i * CHAR_W
        s.append(f'  <text class="t char-{i}" x="{char_x}" y="{prompt_y}" fill="{COLORS["fg"]}">{ch}</text>')

    # Fastfetch content area
    ff_y_base = PAD_Y + LINE_H + 16

    # Embedded GIF image
    with open("/home/itami/Downloads/puck-wave.gif", "rb") as f:
        gif_b64 = base64.b64encode(f.read()).decode()
    img_w, img_h = 180, 150
    img_x = ART_X
    img_y = ff_y_base + 10
    s.append(f'  <image class="pixel-art" x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}" href="data:image/gif;base64,{gif_b64}" />')

    # Info sections with borders
    info_y_base = ff_y_base
    for i, row in enumerate(all_rows):
        kind, data, color = row
        y = info_y_base + i * LINE_H + FONT_SIZE

        if kind == "border":
            s.append(f'  <text class="t info-{i}" x="{INFO_X}" y="{y}" fill="{color}">{escape_xml(data)}</text>')
        elif kind == "line":
            padded, value, color_name = data
            s.append(
                f'  <text class="t info-{i}" x="{INFO_X}" y="{y}">'
                f'<tspan fill="{color}">│</tspan>'
                f'<tspan fill="{COLORS[color_name]}" font-weight="bold"> {escape_xml(padded)}</tspan>'
                f'<tspan fill="{COLORS["overlay"]}"> : </tspan>'
                f'<tspan fill="{COLORS["fg"]}">{escape_xml(value)}</tspan>'
                f'</text>'
            )
        elif kind == "blank":
            s.append(
                f'  <text class="t info-{i}" x="{INFO_X}" y="{y}">'
                f'<tspan fill="{COLORS["overlay"]}">│</tspan>'
                f'</text>'
            )

    # Color palette
    palette_y = info_y_base + total_info_lines * LINE_H + 8
    s.append('  <g class="palette">')
    block_size = 16
    gap = 6
    for i, color_name in enumerate(PALETTE_COLORS):
        bx = INFO_X + i * (block_size + gap)
        s.append(f'    <rect x="{bx}" y="{palette_y}" width="{block_size}" height="{block_size}" rx="3" fill="{COLORS[color_name]}" />')
    s.append('  </g>')

    s.append('</g>')
    s.append('</svg>')

    output = "/home/itami/Documents/Aselori/terminal.svg"
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    print(f"Generated {output}")


if __name__ == "__main__":
    generate_svg()
