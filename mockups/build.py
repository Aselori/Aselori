#!/usr/bin/env python3
"""Build mockup assets: inline the GIF into mockup A and write the STL for mockup C."""

import base64
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent


def build_terminal():
    gif = base64.b64encode((ROOT / "assets/puck-wave.gif").read_bytes()).decode()
    src = (HERE / "a-terminal.src.svg").read_text(encoding="utf-8")
    (HERE / "a-terminal.svg").write_text(src.replace("__GIF__", f"data:image/gif;base64,{gif}"), encoding="utf-8")


def box(x0, y0, z0, x1, y1, z1):
    """12 triangles of an axis-aligned box, outward normals."""
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [((0, 0, -1), (0, 2, 1), (0, 3, 2)), ((0, 0, 1), (4, 5, 6), (4, 6, 7)),
             ((0, -1, 0), (0, 1, 5), (0, 5, 4)), ((0, 1, 0), (3, 7, 6), (3, 6, 2)),
             ((-1, 0, 0), (0, 4, 7), (0, 7, 3)), ((1, 0, 0), (1, 2, 6), (1, 6, 5))]
    for n, *tris in faces:
        for t in tris:
            yield n, [v[i] for i in t]


def build_rack():
    # x: width, y: depth (front at y=0), z: height. Units in mm-like scale.
    parts = [
        box(0, 0, 0, 4, 60, 100), box(56, 0, 0, 60, 60, 100),   # side rails
        box(0, 0, 96, 60, 60, 100), box(0, 0, 0, 60, 60, 4),    # top, bottom
        box(4, 56, 4, 56, 60, 96),                               # back panel
    ]
    for i in range(5):                                          # five 1U servers
        z = 8 + i * 17
        parts.append(box(5, 2, z, 55, 54, z + 14))
        parts.append(box(46, 0.5, z + 5, 50, 2, z + 9))          # status LED
        for j in range(4):                                      # drive bays
            parts.append(box(9 + j * 8, 1, z + 3, 15 + j * 8, 2, z + 11))
    lines = ["solid rack"]
    for part in parts:
        for n, tri in part:
            lines.append(f"  facet normal {n[0]} {n[1]} {n[2]}\n    outer loop")
            lines += [f"      vertex {x} {y} {z}" for x, y, z in tri]
            lines.append("    endloop\n  endfacet")
    lines.append("endsolid rack")
    (HERE / "c-rack.stl").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    build_terminal()
    build_rack()
    print("built a-terminal.svg, c-rack.stl")
