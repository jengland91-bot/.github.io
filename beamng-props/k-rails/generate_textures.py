#!/usr/bin/env python3
"""Concrete K-rail / Jersey barrier textures (blank + stripe options)."""

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


def concrete(w, h, base=(175, 172, 165)):
    br, bg, bb = base
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 19) ^ (y * 11)) % 13
            pit = -10 if ((x * 7 + y * 13) % 61) == 0 else 0
            r = br + n - 6 + pit
            g = bg + n - 6 + pit
            b = bb + n - 7 + pit
            px.append(
                (max(40, min(220, r)), max(40, min(220, g)), max(35, min(210, b)), 255)
            )
    return px


def striped(w, h):
    """Concrete with orange/white hazard panels on ends feel — full face stripes."""
    px = concrete(w, h)
    orange = (220, 100, 25, 255)
    white = (235, 235, 230, 255)
    # vertical bands across width (useful on long side UV)
    band = w // 8
    for y in range(h):
        for x in range(w):
            b = (x // band) % 2
            # keep concrete texture faintly under stripe
            base = px[y * w + x]
            stripe = orange if b == 0 else white
            px[y * w + x] = (
                (base[0] + stripe[0]) // 2,
                (base[1] + stripe[1]) // 2,
                (base[2] + stripe[2]) // 2,
                255,
            )
    return px


def blank_tint(w, h, color):
    return concrete(w, h, base=color[:3])


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    # Master swappable texture for blank k-rail
    save(TEX / "krail.png", 512, 512, concrete(512, 512))
    save(TEX / "krail_concrete.png", 512, 512, concrete(512, 512))
    save(TEX / "krail_stripe.png", 512, 512, striped(512, 512))
    save(TEX / "krail_white.png", 512, 512, blank_tint(512, 512, (220, 220, 215, 255)))
    save(TEX / "krail_orange.png", 512, 512, blank_tint(512, 512, (210, 105, 30, 255)))
    save(TEX / "krail_dark.png", 512, 512, blank_tint(512, 512, (70, 70, 72, 255)))


if __name__ == "__main__":
    main()
