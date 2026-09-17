#!/usr/bin/env python3
"""
Parker 400 mile markers — vertical race plates.
Layout from BITD/AORC-style refs: header, MILE + big number, logo row.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
sys.path.insert(0, str(ROOT.parent / "_shared"))
from sign_draw import (  # noqa: E402
    canvas,
    downsample2,
    draw_header,
    draw_logo_row,
    draw_text,
    save_png,
)


INK = (12, 12, 12, 255)
WHITE = (250, 250, 250, 255)


def make_mile(n: int | None, path: Path) -> None:
    # Higher-res portrait plate
    sw, sh = 640, 1120
    px = canvas(sw, sh, WHITE)

    # Border first so header/logo stay clear of the frame
    for t in range(4):
        for x in range(sw):
            px[t * sw + x] = INK
            px[(sh - 1 - t) * sw + x] = INK
        for y in range(sh):
            px[y * sw + t] = INK
            px[y * sw + (sw - 1 - t)] = INK

    draw_header(px, sw, sh, INK)

    draw_text(px, sw, sh, "MILE", sw // 2, int(sh * 0.24), 10, INK)

    label = "--" if n is None else str(n)
    scale = 34 if len(label) <= 2 else 26
    draw_text(px, sw, sh, label, sw // 2, int(sh * 0.52), scale, INK)

    draw_logo_row(px, sw, sh, int(sh * 0.88), INK, WHITE)

    w, h, out = downsample2(sw, sh, px)
    save_png(path, w, h, out)


def make_wood(path: Path) -> None:
    w, h = 128, 512
    pixels = []
    for y in range(h):
        for x in range(w):
            stripe = ((x * 17 + y // 8) % 13) - 6
            wave = ((y // 3 + x * 2) % 29) - 14
            r = 108 + stripe * 3 + wave // 3
            g = 72 + stripe * 2 + wave // 4
            b = 40 + stripe + wave // 5
            pixels.append(
                (max(25, min(170, r)), max(18, min(130, g)), max(10, min(90, b)), 255)
            )
    save_png(path, w, h, pixels)


def make_metal(path: Path) -> None:
    w = h = 128
    pixels = []
    for y in range(h):
        for x in range(w):
            n = ((x * 13) ^ (y * 7)) % 19
            v = 128 + n
            if y % 3 == 0:
                v += 6
            pixels.append((v, v + 2, v + 5, 255))
    save_png(path, w, h, pixels)


def main() -> None:
    TEX.mkdir(parents=True, exist_ok=True)
    make_wood(TEX / "post_wood.png")
    make_metal(TEX / "sign_metal.png")
    make_mile(None, TEX / "sign_blank.png")
    for n in range(1, 101):
        make_mile(n, TEX / f"mile_{n:03d}.png")
        if n < 100:
            (TEX / f"mile_{n:02d}.png").write_bytes((TEX / f"mile_{n:03d}.png").read_bytes())


if __name__ == "__main__":
    main()
