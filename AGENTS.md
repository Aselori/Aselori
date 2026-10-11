# Aselori GitHub profile README

Animated fastfetch-style terminal SVG for the github.com/Aselori profile page.

## How it works

- `python3 generate.py` writes `terminal.svg` (desktop) and `terminal-mobile.svg`
  (phones). Standard library only, no `package.json`.
- `README.md` embeds both through `<picture>`; bump the `?v=` query when the SVGs
  change so GitHub's image cache refreshes.
- The GIF (`assets/puck-wave.gif`) and the JetBrains Mono subsets
  (`assets/fonts/`) are embedded as data URIs. See the docstring in
  `generate.py` for how to regenerate the font subsets.

## GitHub SVG constraints

GitHub shows the SVG inside `<img>` and sanitizes it:

- Works: CSS `@keyframes`, `@media` (including `prefers-color-scheme` and
  `prefers-reduced-motion`), `@supports`, and `@font-face` or `<image>` whose
  source is a data URI.
- Blocked or stripped: JavaScript, `@import`, and any external URL (fonts,
  images, stylesheets). Everything the SVG needs must be embedded.

## Ideas and open items

Carried over from the notes of an older local clone (May 2026); recheck each one
against the current SVG before acting on it.

- Confirm the embedded GIF animates on github.com, not only in a local browser.
- Pet or character animation: ASCII pets walk in after the fastfetch output and
  hold a pose.
