#!/usr/bin/env python3
"""Generate desert-race mile marker sign textures (no external deps)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"

# 7x9 uppercase + digits — cleaner when supersampled
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
        ".#####.",
        ".....##",
        "......#",
        ".....#.",
        ".####..",
    ],
    "M": [
        "#.....#",
        "##...##",
        "#.#.#.#",
        "#..#..#",
        "#.....#",
        "#.....#",
        "#.....#",
        "#.....#",
        "#.....#",
    ],
    "I": [
        ".#####.",
        "...#...",
        "...#...",
        "...#...",
        "...#...",
        "...#...",
        "...#...",
        "...#...",
        ".#####.",
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
    "E": [
        "#######",
        "#......",
        "#......",
        "#......",
        "######.",
        "#......",
        "#......",
        "#......",
        "#######",
    ],
    "-": [
        ".......",
        ".......",
        ".......",
        ".......",
        "#######",
        ".......",
        ".......",
        ".......",
        ".......",
    ],
}


def png_rgba(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", ihdr),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def mix(c0, c1, t: float):
    return tuple(lerp(c0[i], c1[i], t) for i in range(4))


def make_sign(label_top: str, label_bot: str, path: Path) -> None:
    # Render at 2x then box-filter downsample for softer edges
    sw, sh = 1024, 640
    w, h = 512, 320
    cream = (238, 233, 220, 255)
    border = (22, 22, 22, 255)
    ink = (16, 16, 16, 255)
    orange = (210, 88, 28, 255)
    dirt = (160, 130, 95, 255)

    hi = [cream] * (sw * sh)

    def rect(x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(sh, y1)):
            row = y * sw
            for x in range(max(0, x0), min(sw, x1)):
                hi[row + x] = color

    # Soft outer vignette / dirt
    for y in range(sh):
        for x in range(sw):
            edge = min(x, y, sw - 1 - x, sh - 1 - y)
            if edge < 28:
                t = 1.0 - edge / 28.0
                hi[y * sw + x] = mix(cream, dirt, t * 0.35)
            # subtle noise
            n = ((x * 37 + y * 19) % 23) / 23.0
            if n > 0.92:
                c = hi[y * sw + x]
                hi[y * sw + x] = mix(c, dirt, 0.12)

    margin = 36
    rect(0, 0, sw, margin, border)
    rect(0, sh - margin, sw, sh, border)
    rect(0, 0, margin, sh, border)
    rect(sw - margin, 0, sw, sh, border)

    m2 = 68
    rect(m2, m2, sw - m2, m2 + 6, border)
    rect(m2, sh - m2 - 6, sw - m2, sh - m2, border)
    rect(m2, m2, m2 + 6, sh - m2, border)
    rect(sw - m2 - 6, m2, sw - m2, sh - m2, border)

    rect(margin, margin, sw - margin, margin + 22, orange)

    def draw_text(text: str, cx: int, cy: int, scale: int, color):
        glyphs = [FONT.get(ch, FONT[" "]) for ch in text.upper()]
        gw, gh = 7, 9
        gap = 1
        total_w = len(glyphs) * (gw + gap) * scale - gap * scale
        total_h = gh * scale
        x0 = cx - total_w // 2
        y0 = cy - total_h // 2
        for i, glyph in enumerate(glyphs):
            ox = x0 + i * (gw + gap) * scale
            for gy, row in enumerate(glyph):
                for gx, cell in enumerate(row):
                    if cell != "#":
                        continue
                    # soft block with 1px inset fade
                    for sy in range(scale):
                        for sx in range(scale):
                            x = ox + gx * scale + sx
                            y = y0 + gy * scale + sy
                            if 0 <= x < sw and 0 <= y < sh:
                                edge = min(sx, sy, scale - 1 - sx, scale - 1 - sy)
                                t = 1.0 if edge > 0 else 0.55
                                base = hi[y * sw + x]
                                hi[y * sw + x] = mix(base, color, t)

    draw_text(label_top, sw // 2, int(sh * 0.38), 10, ink)
    draw_text(label_bot, sw // 2, int(sh * 0.68), 16, ink)

    # Downsample 2x2
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


def make_wood(path: Path) -> None:
    w, h = 128, 512
    pixels = []
    for y in range(h):
        for x in range(w):
            stripe = ((x * 17 + y // 8) % 13) - 6
            wave = ((y // 3 + x * 2) % 29) - 14
            r = 108 + stripe * 3 + wave // 3
            g = 72 + stripe * 2 + wave // 4
            b = 40 + stripe + wave // 5
            if (x * 5 + y) % 53 == 0:
                r, g, b = r - 24, g - 16, b - 10
            # edge darkening
            edge = min(x, w - 1 - x)
            if edge < 6:
                t = 1.0 - edge / 6.0
                r = int(r * (1 - 0.25 * t))
                g = int(g * (1 - 0.25 * t))
                b = int(b * (1 - 0.25 * t))
            pixels.append(
                (
                    max(25, min(170, r)),
                    max(18, min(130, g)),
                    max(10, min(90, b)),
                    255,
                )
            )
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def make_metal(path: Path) -> None:
    w = h = 128
    pixels = []
    for y in range(h):
        for x in range(w):
            n = ((x * 13) ^ (y * 7)) % 19
            v = 128 + n
            # brushed horizontal lines
            if y % 3 == 0:
                v += 6
            pixels.append((v, v + 2, v + 5, 255))
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def main() -> None:
    TEX.mkdir(parents=True, exist_ok=True)
    make_wood(TEX / "post_wood.png")
    make_metal(TEX / "sign_metal.png")
    make_sign("MILE", "--", TEX / "sign_blank.png")
    # Full Parker-length set: Mile 1 through Mile 100
    for n in range(1, 101):
        make_sign("MILE", str(n), TEX / f"mile_{n:03d}.png")
        # Keep 2-digit aliases for 1-99 used by older scripts
        if n < 100:
            src = TEX / f"mile_{n:03d}.png"
            dst = TEX / f"mile_{n:02d}.png"
            if src.exists():
                dst.write_bytes(src.read_bytes())


if __name__ == "__main__":
    main()
