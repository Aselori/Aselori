#!/usr/bin/env python3
"""Generate the animated terminal SVGs for the GitHub profile README.

Writes terminal.svg (desktop) and terminal-mobile.svg (phones) next to this file.
Standard library only: the GIF and the font subsets are read from assets/ and embedded,
because GitHub shows the SVG inside <img>, where external files never load.

The fonts are JetBrains Mono subsets (ASCII + U+276F), regenerated only if new characters are needed:
  pyftsubset JetBrainsMono-Regular.ttf --unicodes="U+0020-007E,U+276F" --no-hinting \
    --layout-features='' --desubroutinize --name-IDs='0,1,2,13,14' --flavor=woff \
    --output-file=assets/fonts/jetbrains-mono-regular.woff
"""

import base64
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── Profile ───────────────────────────────────────────────────
USER = "aselori"
BRANCH = "open-to-internships"
COMMAND = "fastfetch"

# (title, border color, dashed, rows); a row is (label, label color, value)
SECTIONS = [
    ("about", "blue", False, [
        ("role", "peach", "full-stack developer, moving into backend and cloud"),
        ("location", "pink", "Monterrey, MX"),
        ("os", "blue", "Arch Linux"),
    ]),
    ("stack", "green", False, [
        ("api", "mauve", "Node.js, Express, Fastify, REST"),
        ("data", "blue", "PostgreSQL, Prisma"),
        ("platform", "teal", "Docker, Linux, GitHub Actions"),
        ("client", "yellow", "Next.js"),
        ("langs", "green", "TypeScript, Python, SQL, Bash"),
    ]),
    # Dashed: the part still being learned.
    ("learning", "peach", True, [
        ("cloud", "peach", "AWS (EC2, S3), networking"),
    ]),
]

PALETTE = ["red", "green", "yellow", "blue", "mauve", "teal", "peach", "pink"]

# ── Catppuccin Latte (light) / Mocha (dark) ───────────────────
LATTE = {"bg": "#eff1f5", "fg": "#4c4f69", "sub": "#6c6f85", "teal": "#179299", "mauve": "#8839ef",
         "blue": "#1e66f5", "green": "#40a02b", "peach": "#fe640b", "yellow": "#df8e1d",
         "red": "#d20f39", "pink": "#ea76cb"}
MOCHA = {"bg": "#1e1e2e", "fg": "#cdd6f4", "sub": "#a6adc8", "teal": "#94e2d5", "mauve": "#cba6f7",
         "blue": "#89b4fa", "green": "#a6e3a1", "peach": "#fab387", "yellow": "#f9e2af",
         "red": "#f38ba8", "pink": "#f5c2e7"}

# ── Metrics ───────────────────────────────────────────────────
FONT_SIZE = 14
CHAR_W = FONT_SIZE * 0.6   # JetBrains Mono advance is exactly 600/1000 em
ROW_H = 24
BOX_PAD_X = 20             # box edge to text
BOX_GAP = 22               # between boxes
LABEL_COLS = max(len(label) for *_, rows in SECTIONS for label, _, _ in rows) + 1

# ── Timing (seconds) ──────────────────────────────────────────
TYPE_START = 0.30
CHAR_DELAY = 0.07
OUTPUT_AT = TYPE_START + len(COMMAND) * CHAR_DELAY + 0.35

DESKTOP = {
    "width": 840, "pad": 28, "prompt_lines": 1,
    "gif": (28, 76, 190), "palette": (28, 290, 8),     # x, y, squares per row
    "box_x": 250, "box_y": 72,
}
MOBILE = {
    "width": 360, "pad": 18, "prompt_lines": 2,
    "gif": (18, 76, 120), "palette": (166, 112, 4),
    "box_x": 18, "box_y": 226,
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def data_uri(path, mime):
    return f"data:{mime};base64,{base64.b64encode((ROOT / path).read_bytes()).decode()}"


def style():
    def tokens(theme):
        return " ".join(f"--{k}:{v};" for k, v in theme.items())

    regular = data_uri("assets/fonts/jetbrains-mono-regular.woff", "font/woff")
    bold = data_uri("assets/fonts/jetbrains-mono-bold.woff", "font/woff")
    return f"""<style>
  @font-face {{ font-family: "JBM"; font-weight: 400; src: url({regular}) format("woff"); }}
  @font-face {{ font-family: "JBM"; font-weight: 700; src: url({bold}) format("woff"); }}
  :root {{ {tokens(LATTE)} }}
  @media (prefers-color-scheme: dark) {{ :root {{ {tokens(MOCHA)} }} }}
  text {{ font-family: "JBM", ui-monospace, monospace; font-size: {FONT_SIZE}px; fill: var(--fg); white-space: pre; }}
  .win {{ fill: var(--bg); }}
  .sub {{ fill: var(--sub); }}
  .b {{ font-weight: 700; }}
  .box {{ fill: none; stroke-width: 1.5; }}
  .knock {{ fill: var(--bg); }}
  .c {{ fill: transparent; animation: type .01s forwards; }}
  @keyframes type {{ to {{ fill: var(--fg); }} }}
  .out {{ opacity: 0; animation: show .2s ease-out {OUTPUT_AT:.2f}s forwards; }}
  @keyframes show {{ to {{ opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .c {{ animation: none; fill: var(--fg); }}
    .out {{ animation: none; opacity: 1; }}
  }}
</style>"""


def prompt(layout):
    pad = layout["pad"]
    who = (f'<tspan class="b" fill="var(--teal)">{USER}</tspan> on '
           f'<tspan fill="var(--mauve)">{BRANCH}</tspan>')
    arrow = '<tspan fill="var(--green)">❯</tspan> '
    typed = "".join(f'<tspan class="c" style="animation-delay:{TYPE_START + i * CHAR_DELAY:.2f}s">{ch}</tspan>'
                    for i, ch in enumerate(COMMAND))
    if layout["prompt_lines"] == 1:
        return [f'<text x="{pad}" y="40">{who} {arrow}{typed}</text>']
    return [f'<text x="{pad}" y="34">{who}</text>', f'<text x="{pad}" y="58">{arrow}{typed}</text>']


def section(title, color, dashed, rows, x, y, width):
    """One bordered box; returns (svg lines, height). Long values wrap under the value column."""
    text_x = x + BOX_PAD_X
    # Columns get explicit x positions: browsers round glyph advances differently,
    # so padding with spaces drifts by a few pixels per row.
    colon_x = text_x + LABEL_COLS * CHAR_W
    value_x = text_x + (LABEL_COLS + 2) * CHAR_W
    value_cols = int((width - 2 * BOX_PAD_X) // CHAR_W) - LABEL_COLS - 2
    lines = []
    for label, label_color, value in rows:
        for i, part in enumerate(textwrap.wrap(value, value_cols)):
            head = ""
            if i == 0:
                head = (f'<tspan class="b" fill="var(--{label_color})">{esc(label)}</tspan>'
                        f'<tspan class="sub" x="{colon_x:.1f}">:</tspan>')
            lines.append(f'{head}<tspan x="{value_x:.1f}">{esc(part)}</tspan>')

    height = len(lines) * ROW_H + ROW_H
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    title_w = (len(title) + 2) * CHAR_W
    out = [
        f'<rect class="box" x="{x}" y="{y}" width="{width}" height="{height}" rx="6" stroke="var(--{color})"{dash}/>',
        f'<rect class="knock" x="{text_x - CHAR_W}" y="{y - 8}" width="{title_w:.1f}" height="16"/>',
        f'<text class="b" x="{text_x}" y="{y + 4}" fill="var(--{color})">{esc(title)}</text>',
    ]
    for i, line in enumerate(lines):
        out.append(f'<text x="{text_x}" y="{y + 30 + i * ROW_H}">{line}</text>')
    return out, height


def render(layout, gif_uri):
    width, pad = layout["width"], layout["pad"]
    box_x, box_w = layout["box_x"], width - layout["box_x"] - pad

    body, y = [], layout["box_y"]
    for title, color, dashed, rows in SECTIONS:
        lines, h = section(title, color, dashed, rows, box_x, y, box_w)
        body += lines
        y += h + BOX_GAP
    height = y - BOX_GAP + 26

    gx, gy, gsize = layout["gif"]
    px, py, per_row = layout["palette"]
    swatches = [f'<rect x="{px + (i % per_row) * 22}" y="{py + (i // per_row) * 22}" width="16" height="16" rx="3" fill="var(--{c})"/>'
                for i, c in enumerate(PALETTE)]

    stack = "; ".join(f"{label}: {value}" for _, _, _, rows in SECTIONS for label, _, value in rows)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d">',
        f'<title id="t">{USER} {COMMAND}</title>',
        f'<desc id="d">{esc(stack)}</desc>',
        style(),
        f'<rect class="win" width="{width}" height="{height}" rx="10"/>',
        *prompt(layout),
        '<g class="out">',
        f'<image x="{gx}" y="{gy}" width="{gsize}" height="{gsize}" href="{gif_uri}"/>',
        *swatches,
        *body,
        '</g>',
        '</svg>',
    ]) + "\n"


def main():
    gif = data_uri("assets/puck-wave.gif", "image/gif")
    for name, layout in (("terminal.svg", DESKTOP), ("terminal-mobile.svg", MOBILE)):
        svg = render(layout, gif)
        (ROOT / name).write_text(svg, encoding="utf-8")
        print(f"{name}: {len(svg) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
