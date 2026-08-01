#!/usr/bin/env python3
"""Blank / swappable textures for the inflatable arch (tubes + block + logo)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
TEMPLATES = ROOT / "logo_templates"
OUT_TEX = ROOT / "export" / "dae"

LOGO_W, LOGO_H = 1024, 512
TILE = 256


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


def save(path: Path, w, h, pixels):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def solid(w, h, color):
    return [color] * (w * h)


def vinyl(w, h, color):
    r, g, b, a = color
    px = []
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


def template_box(w, h, bg, guide, label_lines=None):
    px = solid(w, h, bg)
    x0, x1 = int(w * 0.08), int(w * 0.92)
    y0, y1 = int(h * 0.12), int(h * 0.88)

    def setp(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            px[y * w + x] = c

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
    cx, cy = w // 2, h // 2
    for i in range(-40, 41):
        setp(cx + i, cy, guide)
        setp(cx, cy + i, guide)
    return px


def write_pair(name, w, h, pixels):
    """Write into textures/ and export/dae/ so DAE always has locals."""
    save(TEX / name, w, h, pixels)
    save(OUT_TEX / name, w, h, pixels)


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    OUT_TEX.mkdir(parents=True, exist_ok=True)

    # Neutral blanks — recolor these three files to customize the whole arch
    white = (242, 242, 240, 255)
    light_gray = (210, 210, 210, 255)
    mid_gray = (120, 120, 122, 255)
    black = (22, 22, 22, 255)

    # Primary swappable set (used by arch_blank.dae)
    write_pair("arch_tube.png", TILE, TILE, vinyl(TILE, TILE, white))
    write_pair("arch_block.png", TILE, TILE, vinyl(TILE, TILE, light_gray))
    write_pair("arch_logo.png", LOGO_W, LOGO_H, solid(LOGO_W, LOGO_H, mid_gray))

    # Extra blank color bases users can copy over arch_tube.png / arch_block.png
    presets = {
        "arch_tube_white.png": white,
        "arch_tube_yellow.png": (235, 200, 35, 255),
        "arch_tube_orange.png": (230, 110, 25, 255),
        "arch_tube_black.png": black,
        "arch_tube_red.png": (180, 30, 30, 255),
        "arch_tube_blue.png": (30, 70, 160, 255),
        "arch_block_white.png": white,
        "arch_block_black.png": black,
        "arch_block_gray.png": light_gray,
        "arch_logo_white.png": white,
        "arch_logo_black.png": black,
        "arch_logo_gray.png": mid_gray,
    }
    for name, color in presets.items():
        if "logo" in name:
            write_pair(name, LOGO_W, LOGO_H, solid(LOGO_W, LOGO_H, color))
        else:
            write_pair(name, TILE, TILE, vinyl(TILE, TILE, color))

    # Paint templates
    save(
        TEMPLATES / "paint_tube_color.png",
        TILE,
        TILE,
        template_box(TILE, TILE, white, (80, 80, 80, 255)),
    )
    save(
        TEMPLATES / "paint_block_color.png",
        TILE,
        TILE,
        template_box(TILE, TILE, light_gray, (60, 60, 60, 255)),
    )
    save(
        TEMPLATES / "paint_logo.png",
        LOGO_W,
        LOGO_H,
        template_box(LOGO_W, LOGO_H, mid_gray, (220, 220, 220, 255)),
    )
    print("blank arch texture set ready")


if __name__ == "__main__":
    main()
