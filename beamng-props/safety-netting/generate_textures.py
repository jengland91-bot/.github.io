#!/usr/bin/env python3
"""Orange plastic safety netting / snow-fence style mesh textures."""

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


def safety_mesh(w, h, color=(230, 95, 25, 255), gap=(35, 40, 30, 255)):
    """Open rectangular plastic mesh."""
    px = [gap] * (w * h)
    cell_x, cell_y = 28, 36
    bar = 5
    for y in range(h):
        for x in range(w):
            if (x % cell_x) < bar or (y % cell_y) < bar:
                n = ((x + y) % 5)
                px[y * w + x] = (
                    max(40, min(255, color[0] - n)),
                    max(20, min(200, color[1] - n)),
                    max(10, min(120, color[2])),
                    255,
                )
    return px


def stake_tex(w=64, h=256):
    px = []
    for y in range(h):
        for x in range(w):
            v = 45 + ((x * 5) % 7)
            px.append((v + 80, v + 30, 20, 255))  # orange plastic stake
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    save(TEX / "safety_orange.png", 512, 512, safety_mesh(512, 512))
    save(
        TEX / "safety_yellow.png",
        512,
        512,
        safety_mesh(512, 512, color=(235, 200, 40, 255)),
    )
    save(TEX / "safety_stake.png", 64, 256, stake_tex())
    # wood stake option
    px = []
    for y in range(256):
        for x in range(64):
            s = ((x * 3 + y // 4) % 7) - 3
            px.append((110 + s * 3, 75 + s * 2, 40 + s, 255))
    save(TEX / "safety_stake_wood.png", 64, 256, px)


if __name__ == "__main__":
    main()
