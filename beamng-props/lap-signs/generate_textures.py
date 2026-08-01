#!/usr/bin/env python3
"""Generate LAP 1–10 sign textures for Parker 400."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"

FONT: dict[str, list[str]] = {
    " ": ["......."] * 9,
    "0": [
        ".#####.",
        "#.....#",
        "#....##",
        "#...#.#",
        "#..#..#",
        "#.#...#",
        "##....#",
        "#.....#",
        ".#####.",
    ],
    "1": [
        "...#...",
        "..##...",
        ".#.#...",
        "...#...",
        "...#...",
        "...#...",
        "...#...",
        "...#...",
        ".#####.",
    ],
    "2": [
        ".#####.",
        "#.....#",
        "......#",
        ".....#.",
        "....#..",
        "...#...",
        "..#....",
        ".#.....",
        "#######",
    ],
    "3": [
        ".#####.",
        "#.....#",
        "......#",
        "......#",
        "..####.",
        "......#",
        "......#",
        "#.....#",
        ".#####.",
    ],
    "4": [
        "....#..",
        "...##..",
        "..#.#..",
        ".#..#..",
        "#...#..",
        "#######",
        "....#..",
        "....#..",
        "....#..",
    ],
    "5": [
        "#######",
        "#......",
        "#......",
        "######.",
        "......#",
        "......#",
        "......#",
        "#.....#",
        ".#####.",
    ],
    "6": [
        "..####.",
        ".#.....",
        "#......",
        "#.####.",
        "##....#",
        "#.....#",
        "#.....#",
        "#.....#",
        ".#####.",
    ],
    "7": [
        "#######",
        "......#",
        ".....#.",
        "....#..",
        "...#...",
        "..#....",
        "..#....",
        "..#....",
        "..#....",
    ],
    "8": [
        ".#####.",
        "#.....#",
        "#.....#",
        "#.....#",
        ".#####.",
        "#.....#",
        "#.....#",
        "#.....#",
        ".#####.",
    ],
    "9": [
        ".#####.",
        "#.....#",
        "#.....#",
        "#.....#",
        ".######",
        ".....##",
        "......#",
        ".....#.",
        ".####..",
    ],
    "A": [
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
    ],
    "L": [
        "#......",
        "#......",
        "#......",
        "#......",
        "#......",
        "#......",
        "#......",
        "#......",
        "#######",
    ],
    "P": [
        "######.",
        "#.....#",
        "#.....#",
        "#.....#",
        "######.",
        "#......",
        "#......",
        "#......",
        "#......",
    ],
}

# Normalize A to 7-wide like others
FONT["A"] = [
    "...#...",
    "..#.#..",
    ".#...#.",
    "#.....#",
    "#######",
    "#.....#",
    "#.....#",
    "#.....#",
    "#.....#",
]


def png_rgba(w, h, pixels):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        row = y * w
        for x in range(w):
            raw.extend(pixels[row + x])

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", ihdr),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c0, c1, t):
    return tuple(lerp(c0[i], c1[i], t) for i in range(4))


def fill(px, w, h, c):
    for i in range(w * h):
        px[i] = c


def rect(px, w, h, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(h, y1)):
        for x in range(max(0, x0), min(w, x1)):
            px[y * w + x] = c


def draw_text(px, w, h, text, cx, cy, scale, color):
    glyphs = [FONT.get(ch, FONT[" "]) for ch in text.upper()]
    gw, gh = 7, 9
    gap = 1
    total_w = len(glyphs) * (gw + gap) * scale - gap * scale
    total_h = gh * scale
    x0 = int(cx - total_w / 2)
    y0 = int(cy - total_h / 2)
    for i, glyph in enumerate(glyphs):
        ox = x0 + i * (gw + gap) * scale
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell != "#":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        x = ox + gx * scale + sx
                        y = y0 + gy * scale + sy
                        if 0 <= x < w and 0 <= y < h:
                            edge = min(sx, sy, scale - 1 - sx, scale - 1 - sy)
                            t = 1.0 if edge > 0 else 0.55
                            px[y * w + x] = mix(px[y * w + x], color, t)


def make_lap(n: int, path: Path):
    sw, sh = 1024, 640
    w, h = 512, 320
    cream = (236, 238, 232, 255)
    border = (18, 18, 18, 255)
    ink = (14, 14, 14, 255)
    accent = (28, 128, 92, 255)  # green — distinct from mile orange
    dirt = (150, 140, 110, 255)

    hi = [cream] * (sw * sh)
    for y in range(sh):
        for x in range(sw):
            edge = min(x, y, sw - 1 - x, sh - 1 - y)
            if edge < 28:
                hi[y * sw + x] = mix(cream, dirt, (1 - edge / 28) * 0.3)
            if ((x * 37 + y * 19) % 31) == 0:
                hi[y * sw + x] = mix(hi[y * sw + x], dirt, 0.1)

    m = 36
    rect(hi, sw, sh, 0, 0, sw, m, border)
    rect(hi, sw, sh, 0, sh - m, sw, sh, border)
    rect(hi, sw, sh, 0, 0, m, sh, border)
    rect(hi, sw, sh, sw - m, 0, sw, sh, border)

    m2 = 68
    rect(hi, sw, sh, m2, m2, sw - m2, m2 + 6, border)
    rect(hi, sw, sh, m2, sh - m2 - 6, sw - m2, sh - m2, border)
    rect(hi, sw, sh, m2, m2, m2 + 6, sh - m2, border)
    rect(hi, sw, sh, sw - m2 - 6, m2, sw - m2, sh - m2, border)

    rect(hi, sw, sh, m, m, sw - m, m + 22, accent)

    draw_text(hi, sw, sh, "LAP", sw / 2, sh * 0.38, 11, ink)
    draw_text(hi, sw, sh, str(n), sw / 2, sh * 0.68, 16, ink)

    out = []
    for y in range(h):
        for x in range(w):
            acc = [0, 0, 0, 0]
            for oy in (0, 1):
                for ox in (0, 1):
                    p = hi[(y * 2 + oy) * sw + (x * 2 + ox)]
                    for i in range(4):
                        acc[i] += p[i]
            out.append(tuple(v // 4 for v in acc))
    path.write_bytes(png_rgba(w, h, out))
    print(f"wrote {path}")


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    for n in range(1, 11):
        make_lap(n, TEX / f"lap_{n:02d}.png")
    # copy shared materials from mile kit if present
    for name in ("post_wood.png", "sign_metal.png"):
        src = ROOT.parent / "mile-marker" / "textures" / name
        dst = TEX / name
        if src.exists() and not dst.exists():
            dst.write_bytes(src.read_bytes())
            print(f"copied {dst}")


if __name__ == "__main__":
    main()
