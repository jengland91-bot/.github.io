#!/usr/bin/env python3
"""Porta-potty textures — blank body + door + logo."""

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


def plastic(w, h, color):
    r, g, b = color
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 11) ^ (y * 7)) % 9
            # panel lines
            line = -8 if (x % 64) < 2 or (y % 96) < 2 else 0
            px.append(
                (
                    max(0, min(255, r + n - 4 + line)),
                    max(0, min(255, g + n - 4 + line)),
                    max(0, min(255, b + n - 4 + line)),
                    255,
                )
            )
    return px


def solid(w, h, c):
    return [c] * (w * h)


def door(w, h, color):
    px = plastic(w, h, color)
    # vent slits near top
    for y in range(int(h * 0.12), int(h * 0.28)):
        if (y // 5) % 2 == 0:
            for x in range(int(w * 0.25), int(w * 0.75)):
                px[y * w + x] = (40, 40, 42, 255)
    # handle
    for y in range(int(h * 0.48), int(h * 0.56)):
        for x in range(int(w * 0.72), int(w * 0.82)):
            px[y * w + x] = (30, 30, 30, 255)
    # vacant/occupied indicator circle
    cx, cy, rad = int(w * 0.5), int(h * 0.38), 18
    for y in range(cy - rad, cy + rad + 1):
        for x in range(cx - rad, cx + rad + 1):
            if 0 <= x < w and 0 <= y < h and (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad:
                px[y * w + x] = (40, 160, 70, 255)  # vacant green
    return px


def template(w, h, bg, guide):
    px = solid(w, h, bg)

    def setp(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            px[y * w + x] = c

    x0, x1, y0, y1 = int(w * 0.1), int(w * 0.9), int(h * 0.15), int(h * 0.85)
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

    blue = (55, 105, 170)
    gray = (150, 150, 152)
    green = (50, 130, 80)
    orange = (220, 110, 30)
    white = (230, 230, 228)

    write_both("pp_body.png", 512, 512, plastic(512, 512, blue))
    write_both("pp_door.png", 256, 512, door(256, 512, blue))
    write_both("pp_logo.png", 512, 256, solid(512, 256, (200, 200, 205, 255)))
    write_both("pp_roof.png", 256, 256, plastic(256, 256, (40, 40, 42)))

    for name, col in [
        ("pp_body_blue.png", blue),
        ("pp_body_gray.png", gray),
        ("pp_body_green.png", green),
        ("pp_body_orange.png", orange),
        ("pp_body_white.png", white),
    ]:
        write_both(name, 512, 512, plastic(512, 512, col))
        dname = name.replace("body", "door")
        write_both(dname, 256, 512, door(256, 512, col))

    save(
        TEMPLATES / "paint_pp_logo.png",
        512,
        256,
        template(512, 256, (200, 200, 205, 255), (60, 60, 60, 255)),
    )


if __name__ == "__main__":
    main()
