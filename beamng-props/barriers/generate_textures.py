#!/usr/bin/env python3
"""Textures for stakes, caution ribbon, and snow fence."""

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

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", ihdr),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def save(path, w, h, pixels):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def wood(w=128, h=512):
    px = []
    for y in range(h):
        for x in range(w):
            s = ((x * 17 + y // 8) % 13) - 6
            wave = ((y // 3 + x * 2) % 29) - 14
            r = 118 + s * 3 + wave // 3
            g = 78 + s * 2 + wave // 4
            b = 42 + s + wave // 5
            edge = min(x, w - 1 - x)
            if edge < 5:
                t = 1 - edge / 5
                r = int(r * (1 - 0.22 * t))
                g = int(g * (1 - 0.22 * t))
                b = int(b * (1 - 0.22 * t))
            px.append(
                (max(25, min(170, r)), max(18, min(130, g)), max(10, min(90, b)), 255)
            )
    return px


def metal(w=128, h=128):
    px = []
    for y in range(h):
        for x in range(w):
            n = ((x * 13) ^ (y * 7)) % 19
            v = 110 + n
            if y % 3 == 0:
                v += 5
            px.append((v, v + 2, v + 4, 255))
    return px


def ribbon_caution(w=1024, h=128):
    """Orange ribbon with repeating black CAUTION chevrons / stripes."""
    orange = (230, 110, 20, 255)
    black = (18, 18, 18, 255)
    px = [orange] * (w * h)
    # diagonal hazard stripes
    stripe_w = 36
    for y in range(h):
        for x in range(w):
            if ((x + y) // stripe_w) % 2 == 0 and (h * 0.15 < y < h * 0.85):
                # only edge bands stay solid orange; center gets stripes lightly
                pass
    # top/bottom black borders
    for y in range(h):
        for x in range(w):
            if y < 10 or y >= h - 10:
                px[y * w + x] = black
            elif ((x + int(y * 0.4)) // 28) % 2 == 0 and 18 <= y < h - 18:
                px[y * w + x] = black
    return px


def ribbon_orange(w=1024, h=128):
    orange = (235, 120, 28, 255)
    dark = (180, 70, 10, 255)
    px = []
    for y in range(h):
        for x in range(w):
            # slight weave
            n = ((x // 8) + (y // 4)) % 3
            c = orange if n else dark
            if y < 6 or y >= h - 6:
                c = (20, 20, 20, 255)
            px.append(c)
    return px


def ribbon_yellow(w=1024, h=128):
    yellow = (240, 200, 40, 255)
    black = (18, 18, 18, 255)
    px = []
    for y in range(h):
        for x in range(w):
            if y < 8 or y >= h - 8:
                px.append(black)
            elif ((x // 40) % 2) == 0:
                px.append(yellow)
            else:
                px.append(black)
    return px


def snowfence_slats(w=512, h=256):
    """Vertical wooden slats with gaps (alpha-ish dark gaps)."""
    wood_c = (160, 110, 55, 255)
    wood_d = (120, 80, 40, 255)
    gap = (40, 55, 35, 255)  # dark greenish void (not real alpha in BeamNG easily)
    wire = (70, 70, 75, 255)
    px = [gap] * (w * h)
    slat_w = 28
    gap_w = 18
    period = slat_w + gap_w
    for y in range(h):
        for x in range(w):
            local = x % period
            if local < slat_w:
                # wood grain
                s = ((local * 3 + y // 6) % 7) - 3
                c = wood_c if (y // 5 + local) % 2 == 0 else wood_d
                px[y * w + x] = (
                    max(40, min(200, c[0] + s * 4)),
                    max(30, min(150, c[1] + s * 3)),
                    max(15, min(100, c[2] + s * 2)),
                    255,
                )
    # horizontal binding wires
    for wy in (int(h * 0.2), int(h * 0.5), int(h * 0.8)):
        for y in range(wy - 2, wy + 3):
            for x in range(w):
                px[y * w + x] = wire
    return px


def snowfence_orange(w=512, h=256):
    """Bright orange plastic snow fence look."""
    orange = (230, 95, 25, 255)
    dark = (150, 50, 10, 255)
    gap = (35, 40, 30, 255)
    px = [gap] * (w * h)
    slat_w = 22
    gap_w = 14
    period = slat_w + gap_w
    for y in range(h):
        for x in range(w):
            if (x % period) < slat_w:
                px[y * w + x] = orange if ((x + y) % 5) else dark
    for wy in (int(h * 0.25), int(h * 0.75)):
        for y in range(wy - 2, wy + 3):
            for x in range(w):
                if px[y * w + x] != gap:
                    px[y * w + x] = (40, 40, 40, 255)
    return px


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    save(TEX / "stake_wood.png", 128, 512, wood())
    save(TEX / "stake_metal.png", 128, 128, metal())
    save(TEX / "ribbon_caution.png", 1024, 128, ribbon_caution())
    save(TEX / "ribbon_orange.png", 1024, 128, ribbon_orange())
    save(TEX / "ribbon_yellow_black.png", 1024, 128, ribbon_yellow())
    save(TEX / "snowfence_wood.png", 512, 256, snowfence_slats())
    save(TEX / "snowfence_orange.png", 512, 256, snowfence_orange())


if __name__ == "__main__":
    main()
