#!/usr/bin/env python3
"""Textures for portable light towers (blank body + logo)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
TEMPLATES = ROOT / "logo_templates"
OUT = ROOT / "export" / "dae"


def png_rgba(w, h, pixels):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw.extend(pixels[y * w + x])

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def save(path, w, h, pixels):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def solid(w, h, c):
    return [c] * (w * h)


def metal(w, h, base):
    br, bg, bb = base
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 13) ^ (y * 7)) % 11
            line = 4 if y % 5 == 0 else 0
            px.append(
                (
                    max(0, min(255, br + n - 5 + line)),
                    max(0, min(255, bg + n - 5 + line)),
                    max(0, min(255, bb + n - 5)),
                    255,
                )
            )
    return px


def vents(w, h, base):
    px = metal(w, h, base)
    # horizontal vent slots
    for y in range(h // 3, 2 * h // 3):
        if (y // 6) % 2 == 0:
            for x in range(w // 5, 4 * w // 5):
                v = 30
                px[y * w + x] = (v, v, v + 2, 255)
    return px


def lens(w, h):
    """Bright floodlight face."""
    px = []
    for y in range(h):
        for x in range(w):
            # hot center
            cx, cy = w / 2, h / 2
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / (w * 0.6)
            t = max(0.0, 1.0 - d)
            r = int(255 * (0.85 + 0.15 * t))
            g = int(245 * (0.8 + 0.2 * t))
            b = int(210 * (0.55 + 0.45 * t))
            px.append((r, g, b, 255))
    return px


def template(w, h, bg, guide):
    px = solid(w, h, bg)
    x0, x1 = int(w * 0.12), int(w * 0.88)
    y0, y1 = int(h * 0.2), int(h * 0.8)

    def setp(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            px[y * w + x] = c

    for x in range(x0, x1):
        if (x // 10) % 2 == 0:
            for t in range(2):
                setp(x, y0 + t, guide)
                setp(x, y1 - t, guide)
    for y in range(y0, y1):
        if (y // 10) % 2 == 0:
            for t in range(2):
                setp(x0 + t, y, guide)
                setp(x1 - t, y, guide)
    return px


def write_both(name, w, h, pixels):
    save(TEX / name, w, h, pixels)
    save(OUT / name, w, h, pixels)


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    white = (230, 230, 228)
    gray = (170, 170, 172)
    black = (28, 28, 30)
    yellow = (235, 200, 40)

    # Master swappable body + logo
    write_both("lt_body.png", 512, 512, vents(512, 512, white))
    write_both("lt_logo.png", 512, 256, solid(512, 256, (210, 210, 210, 255)))
    write_both("lt_metal_black.png", 256, 256, metal(256, 256, black))
    write_both("lt_metal_gray.png", 256, 256, metal(256, 256, gray))
    write_both("lt_lens.png", 256, 256, lens(256, 256))
    write_both("lt_tire.png", 256, 256, metal(256, 256, (20, 20, 20)))

    # Body color presets to copy over lt_body.png
    for name, col in [
        ("lt_body_white.png", white),
        ("lt_body_yellow.png", yellow),
        ("lt_body_gray.png", gray),
        ("lt_body_orange.png", (220, 110, 30)),
    ]:
        write_both(name, 512, 512, vents(512, 512, col))

    save(
        TEMPLATES / "paint_lt_logo.png",
        512,
        256,
        template(512, 256, (210, 210, 210, 255), (60, 60, 60, 255)),
    )
    save(
        TEMPLATES / "paint_lt_body.png",
        512,
        512,
        template(512, 512, (*white, 255), (80, 80, 80, 255)),
    )


if __name__ == "__main__":
    main()
