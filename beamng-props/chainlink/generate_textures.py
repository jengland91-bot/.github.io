#!/usr/bin/env python3
"""Chain-link fence textures."""

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


def chainlink(w=512, h=512, wire=(90, 95, 100, 255), gap=(40, 55, 40, 255)):
    """Diamond mesh pattern."""
    px = [gap] * (w * h)
    spacing = 18
    thick = 2
    for y in range(h):
        for x in range(w):
            # two diagonal families
            d1 = (x + y) % spacing
            d2 = (x - y) % spacing
            if d1 < thick or d2 < thick:
                n = ((x * 3) ^ (y * 5)) % 5
                px[y * w + x] = (
                    max(40, min(160, wire[0] + n)),
                    max(40, min(160, wire[1] + n)),
                    max(40, min(160, wire[2] + n)),
                    255,
                )
    return px


def post_metal(w=128, h=512):
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 7) ^ (y * 3)) % 9
            v = 70 + n
            if x < 8 or x > w - 9:
                v -= 15
            px.append((v, v + 2, v + 4, 255))
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    save(TEX / "chainlink.png", 512, 512, chainlink())
    save(TEX / "chainlink_green.png", 512, 512, chainlink(wire=(55, 90, 55, 255)))
    save(TEX / "chainlink_dark.png", 512, 512, chainlink(wire=(50, 50, 52, 255), gap=(30, 35, 30, 255)))
    save(TEX / "fence_post.png", 128, 512, post_metal())


if __name__ == "__main__":
    main()
