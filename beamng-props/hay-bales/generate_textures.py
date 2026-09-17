#!/usr/bin/env python3
"""Hay bale textures."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"


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


def straw(w, h, base=(200, 170, 70)):
    br, bg, bb = base
    px = []
    for y in range(h):
        for x in range(w):
            # vertical straw strands
            strand = ((x * 3 + y // 2) % 7) - 3
            n = ((x * 17) ^ (y * 5)) % 9
            r = br + strand * 4 + n - 4
            g = bg + strand * 3 + n - 4
            b = bb + strand + n - 6
            # twine bands
            if 90 < (y % 128) < 102 or 28 < (y % 128) < 38:
                r, g, b = 90, 70, 35
            px.append(
                (max(40, min(240, r)), max(35, min(220, g)), max(15, min(160, b)), 255)
            )
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    save(TEX / "hay_gold.png", 512, 512, straw(512, 512, (205, 175, 75)))
    save(TEX / "hay_dry.png", 512, 512, straw(512, 512, (180, 155, 85)))
    save(TEX / "hay_green.png", 512, 512, straw(512, 512, (150, 160, 70)))


if __name__ == "__main__":
    main()
