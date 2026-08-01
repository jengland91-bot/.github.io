#!/usr/bin/env python3
"""Blank feather-flag textures + logo placement templates."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
TEMPLATES = ROOT / "logo_templates"

W, H = 512, 2048  # tall flag UV space


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


def solid(color):
    return [color] * (W * H)


def save(path: Path, pixels, w=W, h=H):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def make_template(bg, guide):
    """Blank with faint logo safe-area guides (for Photoshop/GIMP)."""
    px = solid(bg)
    x0, x1 = int(W * 0.12), int(W * 0.88)
    y0, y1 = int(H * 0.12), int(H * 0.88)

    def setp(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            px[y * W + x] = c

    dash = 10
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

    cx, cy = W // 2, H // 2
    for i in range(-40, 41):
        setp(cx + i, cy, guide)
        setp(cx, cy + i, guide)
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)

    orange = (232, 98, 28, 255)
    black = (18, 18, 18, 255)
    white = (242, 242, 240, 255)
    navy = (18, 32, 64, 255)

    save(TEX / "flag_blank_orange.png", solid(orange))
    save(TEX / "flag_blank_black.png", solid(black))
    save(TEX / "flag_blank_white.png", solid(white))
    save(TEX / "flag_blank_navy.png", solid(navy))

    guide_dark = (40, 40, 40, 255)
    guide_light = (200, 200, 200, 255)
    save(TEMPLATES / "logo_template_orange.png", make_template(orange, guide_dark))
    save(TEMPLATES / "logo_template_black.png", make_template(black, guide_light))
    save(TEMPLATES / "logo_template_white.png", make_template(white, guide_dark))
    save(TEMPLATES / "logo_template_navy.png", make_template(navy, guide_light))

    pw, ph = 64, 512
    pole_px = []
    for y in range(ph):
        for x in range(pw):
            v = 28 + (x % 5) + (y % 3)
            pole_px.append((v, v, v + 2, 255))
    save(TEX / "flag_pole.png", pole_px, w=pw, h=ph)


if __name__ == "__main__":
    main()
