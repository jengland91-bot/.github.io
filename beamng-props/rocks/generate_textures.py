#!/usr/bin/env python3
"""Desert rock textures for Parker 400."""

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


def rock_tex(w, h, base):
    br, bg, bb = base
    px = []
    for y in range(h):
        for x in range(w):
            n1 = ((x * 13) ^ (y * 7)) % 17
            n2 = ((x * 3 + y * 5) % 23) - 11
            n3 = ((x // 8) * 17 + (y // 6) * 9) % 13
            # speckles / mineral flecks
            fleck = 18 if ((x * 29 + y * 17) % 47) == 0 else 0
            r = br + n1 - 8 + n2 + fleck // 2
            g = bg + n1 - 8 + n2 // 2 + n3 - 6
            b = bb + n1 - 10 + n2 // 3
            px.append(
                (
                    max(20, min(220, r)),
                    max(15, min(200, g)),
                    max(10, min(180, b)),
                    255,
                )
            )
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    # Tan / sandstone
    save(TEX / "rock_tan.png", 512, 512, rock_tex(512, 512, (168, 140, 100)))
    # Red desert
    save(TEX / "rock_red.png", 512, 512, rock_tex(512, 512, (150, 85, 55)))
    # Gray granite
    save(TEX / "rock_gray.png", 512, 512, rock_tex(512, 512, (110, 110, 112)))
    # Dark basalt
    save(TEX / "rock_dark.png", 512, 512, rock_tex(512, 512, (55, 55, 58)))


if __name__ == "__main__":
    main()
