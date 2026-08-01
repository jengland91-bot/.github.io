#!/usr/bin/env python3
"""Textures for inflatable drive-through arch (blank logo panel)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
TEMPLATES = ROOT / "logo_templates"

# Wide banner on center block
LOGO_W, LOGO_H = 1024, 512


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


def solid(w, h, color):
    return [color] * (w * h)


def vinyl(w, h, color, shade=12):
    """Slight wrinkle/noise so inflatable plastic doesn't look flat."""
    px = []
    r, g, b, a = color
    for y in range(h):
        for x in range(w):
            n = ((x * 17) ^ (y * 11)) % 9
            px.append(
                (
                    max(0, min(255, r + n - 4)),
                    max(0, min(255, g + n - 4)),
                    max(0, min(255, b + n - 4)),
                    a,
                )
            )
    return px


def logo_blank(bg):
    return solid(LOGO_W, LOGO_H, bg)


def logo_template(bg, guide):
    px = solid(LOGO_W, LOGO_H, bg)
    x0, x1 = int(LOGO_W * 0.1), int(LOGO_W * 0.9)
    y0, y1 = int(LOGO_H * 0.15), int(LOGO_H * 0.85)

    def setp(x, y, c):
        if 0 <= x < LOGO_W and 0 <= y < LOGO_H:
            px[y * LOGO_W + x] = c

    dash = 12
    for x in range(x0, x1):
        if (x // dash) % 2 == 0:
            for t in range(2):
                setp(x, y0 + t, guide)
                setp(x, y1 - t, guide)
    for y in range(y0, y1):
        if (y // dash) % 2 == 0:
            for t in range(2):
                setp(x0 + t, y, guide)
                setp(x1 - t, y, guide)
    cx, cy = LOGO_W // 2, LOGO_H // 2
    for i in range(-50, 51):
        setp(cx + i, cy, guide)
        setp(cx, cy + i, guide)
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)

    yellow = (235, 200, 35, 255)
    orange = (230, 110, 25, 255)
    black = (18, 18, 18, 255)
    white = (240, 240, 238, 255)
    navy = (20, 35, 70, 255)

    # Tube vinyl colors
    save(TEX / "arch_tube_yellow.png", 256, 256, vinyl(256, 256, yellow))
    save(TEX / "arch_tube_orange.png", 256, 256, vinyl(256, 256, orange))
    save(TEX / "arch_tube_white.png", 256, 256, vinyl(256, 256, white))

    # Center block base (under logo) + blank logo faces
    save(TEX / "arch_block_black.png", 256, 256, vinyl(256, 256, black))
    save(TEX / "arch_logo_blank_black.png", LOGO_W, LOGO_H, logo_blank(black))
    save(TEX / "arch_logo_blank_white.png", LOGO_W, LOGO_H, logo_blank(white))
    save(TEX / "arch_logo_blank_navy.png", LOGO_W, LOGO_H, logo_blank(navy))

    # Templates for painting logos
    save(
        TEMPLATES / "logo_template_black.png",
        LOGO_W,
        LOGO_H,
        logo_template(black, (180, 180, 180, 255)),
    )
    save(
        TEMPLATES / "logo_template_white.png",
        LOGO_W,
        LOGO_H,
        logo_template(white, (60, 60, 60, 255)),
    )
    save(
        TEMPLATES / "logo_template_navy.png",
        LOGO_W,
        LOGO_H,
        logo_template(navy, (180, 180, 200, 255)),
    )


if __name__ == "__main__":
    main()
