#!/usr/bin/env python3
"""Tent fabric textures — blank/swappable colors + logo panel."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
TEMPLATES = ROOT / "logo_templates"
OUT = ROOT / "export" / "dae"

W, H = 1024, 512


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


def fabric(w, h, color):
    r, g, b, a = color
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 13) ^ (y * 7)) % 7
            # subtle weave
            weave = 2 if ((x // 4) + (y // 4)) % 2 == 0 else 0
            px.append(
                (
                    max(0, min(255, r + n - 3 + weave)),
                    max(0, min(255, g + n - 3 + weave)),
                    max(0, min(255, b + n - 3)),
                    a,
                )
            )
    return px


def solid(w, h, color):
    return [color] * (w * h)


def template(w, h, bg, guide):
    px = solid(w, h, bg)
    x0, x1 = int(w * 0.1), int(w * 0.9)
    y0, y1 = int(h * 0.15), int(h * 0.85)

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

    white = (240, 240, 238, 255)
    orange = (230, 110, 25, 255)
    blue = (40, 90, 170, 255)
    red = (180, 35, 35, 255)
    green = (40, 120, 70, 255)
    black = (25, 25, 25, 255)
    pole = (50, 50, 52, 255)

    # Master swappable fabric for blank tent
    write_both("tent_fabric.png", 512, 512, fabric(512, 512, white))
    write_both("tent_logo.png", W, H, solid(W, H, (200, 200, 200, 255)))
    write_both("tent_pole.png", 128, 128, fabric(128, 128, pole))

    for name, color in [
        ("tent_fabric_white.png", white),
        ("tent_fabric_orange.png", orange),
        ("tent_fabric_blue.png", blue),
        ("tent_fabric_red.png", red),
        ("tent_fabric_green.png", green),
        ("tent_fabric_black.png", black),
    ]:
        write_both(name, 512, 512, fabric(512, 512, color))

    save(TEMPLATES / "paint_tent_fabric.png", 512, 512, template(512, 512, white, (80, 80, 80, 255)))
    save(TEMPLATES / "paint_tent_logo.png", W, H, template(W, H, (200, 200, 200, 255), (60, 60, 60, 255)))


if __name__ == "__main__":
    main()
