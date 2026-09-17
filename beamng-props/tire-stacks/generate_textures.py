#!/usr/bin/env python3
"""Tire rubber textures."""

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


def tire(w=512, h=512):
    px = []
    for y in range(h):
        for x in range(w):
            # tread grooves horizontal-ish
            groove = 8 if (y % 18) < 4 else 0
            n = ((x * 11) ^ (y * 5)) % 9
            v = 22 + n - groove
            # sidewall lettering band
            if 40 < (x % 128) < 90 and abs((y % 64) - 32) < 10:
                v += 6
            px.append((max(5, v), max(5, v), max(5, v + 2), 255))
    return px


def rim(w=256, h=256):
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 7) ^ (y * 3)) % 11
            v = 90 + n
            px.append((v, v + 2, v + 4, 255))
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    save(TEX / "tire_rubber.png", 512, 512, tire())
    save(TEX / "tire_rim.png", 256, 256, rim())


if __name__ == "__main__":
    main()
