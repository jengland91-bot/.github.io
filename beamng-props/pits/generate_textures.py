#!/usr/bin/env python3
"""Textures for EXIT signs and pit mats."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"

FONT: dict[str, list[str]] = {
    " ": ["....."] * 7,
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
}


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


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c0, c1, t):
    return tuple(lerp(c0[i], c1[i], t) for i in range(4))


def fill(px, w, h, c):
    for i in range(w * h):
        px[i] = c


def rect(px, w, h, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(h, y1)):
        for x in range(max(0, x0), min(w, x1)):
            px[y * w + x] = c


def draw_text(px, w, h, text, cx, cy, scale, color):
    glyphs = [FONT.get(ch, FONT[" "]) for ch in text.upper()]
    gw, gh, gap = 5, 7, 1
    tw = len(glyphs) * (gw + gap) * scale - gap * scale
    th = gh * scale
    x0 = int(cx - tw / 2)
    y0 = int(cy - th / 2)
    for i, glyph in enumerate(glyphs):
        ox = x0 + i * (gw + gap) * scale
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell != "#":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        x, y = ox + gx * scale + sx, y0 + gy * scale + sy
                        if 0 <= x < w and 0 <= y < h:
                            px[y * w + x] = color


def fill_circle(px, w, h, cx, cy, r, c):
    r2 = r * r
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if 0 <= x < w and 0 <= y < h and (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                px[y * w + x] = c


def draw_arrow(px, w, h, direction, ink):
    """direction: left|right|up"""
    cx, cy = w / 2, h / 2
    if direction == "up":
        # shaft
        for y in range(int(cy - 20), int(cy + 90)):
            for x in range(int(cx - 14), int(cx + 15)):
                if 0 <= x < w and 0 <= y < h:
                    px[y * w + x] = ink
        # head
        for i in range(70):
            half = int(70 - i)
            y = int(cy - 20 - i)
            for x in range(int(cx - half), int(cx + half + 1)):
                if 0 <= x < w and 0 <= y < h:
                    px[y * w + x] = ink
    else:
        mirror = -1 if direction == "left" else 1
        # shaft
        for x in range(int(cx - mirror * 20), int(cx - mirror * 100), -mirror):
            for y in range(int(cy - 14), int(cy + 15)):
                if 0 <= x < w and 0 <= y < h:
                    px[y * w + x] = ink
        tip_x = cx + mirror * 110
        for i in range(70):
            half = 70 - i
            x = int(tip_x - mirror * i)
            for y in range(int(cy - half), int(cy + half + 1)):
                if 0 <= x < w and 0 <= y < h:
                    px[y * w + x] = ink


def make_exit(name, arrow=None):
    sw, sh = 768, 512
    w, h = 384, 256
    green = (20, 128, 72, 255)
    white = (245, 245, 245, 255)
    border = (245, 245, 245, 255)
    hi = [green] * (sw * sh)
    m = 28
    rect(hi, sw, sh, 0, 0, sw, m, border)
    rect(hi, sw, sh, 0, sh - m, sw, sh, border)
    rect(hi, sw, sh, 0, 0, m, sh, border)
    rect(hi, sw, sh, sw - m, 0, sw, sh, border)

    if arrow:
        draw_text(hi, sw, sh, "EXIT", sw / 2, sh * 0.32, 12, white)
        # draw arrow in lower half on a temp then downsample — reuse by drawing into hi
        # simplified: draw into full-res via helper using image coords
        ink = white
        cx, cy = sw / 2, sh * 0.68
        if arrow == "up":
            for y in range(int(cy - 10), int(cy + 70)):
                for x in range(int(cx - 12), int(cx + 13)):
                    hi[y * sw + x] = ink
            for i in range(55):
                half = 55 - i
                y = int(cy - 10 - i)
                for x in range(int(cx - half), int(cx + half + 1)):
                    if 0 <= x < sw and 0 <= y < sh:
                        hi[y * sw + x] = ink
        else:
            mirror = -1 if arrow == "left" else 1
            x0, x1 = int(cx - mirror * 15), int(cx + mirror * 80)
            step = 1 if x1 > x0 else -1
            for x in range(x0, x1, step):
                for y in range(int(cy - 12), int(cy + 13)):
                    hi[y * sw + x] = ink
            tip = cx + mirror * 95
            for i in range(50):
                half = 50 - i
                x = int(tip - mirror * i)
                for y in range(int(cy - half), int(cy + half + 1)):
                    if 0 <= x < sw and 0 <= y < sh:
                        hi[y * sw + x] = ink
    else:
        draw_text(hi, sw, sh, "EXIT", sw / 2, sh / 2, 16, white)

    out = []
    for y in range(h):
        for x in range(w):
            acc = [0, 0, 0, 0]
            for oy in (0, 1):
                for ox in (0, 1):
                    p = hi[(y * 2 + oy) * sw + (x * 2 + ox)]
                    for i in range(4):
                        acc[i] += p[i]
            out.append(tuple(v // 4 for v in acc))
    save(TEX / name, w, h, out)


def make_mat_rubber(name, w=1024, h=512):
    """Dark rubber pit mat with subtle tread."""
    px = []
    base = (28, 28, 30, 255)
    for y in range(h):
        for x in range(w):
            n = ((x // 6) ^ (y // 6)) % 5
            v = 26 + n * 2
            # border
            edge = min(x, y, w - 1 - x, h - 1 - y)
            if edge < 18:
                v = 18
            elif edge < 28:
                v = 40
            px.append((v, v, v + 2, 255))
    save(TEX / name, w, h, px)


def make_mat_checkered(name, w=1024, h=512):
    a = (22, 22, 24, 255)
    b = (210, 210, 210, 255)
    cell = 64
    px = []
    for y in range(h):
        for x in range(w):
            c = a if ((x // cell) + (y // cell)) % 2 == 0 else b
            edge = min(x, y, w - 1 - x, h - 1 - y)
            if edge < 16:
                c = (15, 15, 15, 255)
            px.append(c)
    save(TEX / name, w, h, px)


def make_mat_orange_trim(name, w=1024, h=512):
    px = []
    for y in range(h):
        for x in range(w):
            edge = min(x, y, w - 1 - x, h - 1 - y)
            if edge < 22:
                c = (220, 95, 25, 255)
            elif edge < 32:
                c = (20, 20, 20, 255)
            else:
                n = ((x // 8) + (y // 8)) % 4
                v = 30 + n
                c = (v, v, v + 2, 255)
            px.append(c)
    save(TEX / name, w, h, px)


def make_mat_pitstall(name, w=1024, h=512):
    """Dark mat with faint PIT word watermark area (blank-ish for logos)."""
    px = []
    for y in range(h):
        for x in range(w):
            edge = min(x, y, w - 1 - x, h - 1 - y)
            n = ((x * 13) ^ (y * 7)) % 7
            v = 32 + n
            if edge < 20:
                v = 16
            px.append((v, v + 1, v + 3, 255))
    # very faint center guide box
    x0, x1 = int(w * 0.2), int(w * 0.8)
    y0, y1 = int(h * 0.25), int(h * 0.75)
    guide = (55, 55, 60, 255)
    for x in range(x0, x1):
        if (x // 8) % 2 == 0:
            for t in range(2):
                px[(y0 + t) * w + x] = guide
                px[(y1 - t) * w + x] = guide
    for y in range(y0, y1):
        if (y // 8) % 2 == 0:
            for t in range(2):
                px[y * w + x0 + t] = guide
                px[y * w + x1 - t] = guide
    save(TEX / name, w, h, px)


def wood_post():
    w, h = 128, 512
    px = []
    for y in range(h):
        for x in range(w):
            s = ((x * 17 + y // 8) % 13) - 6
            r = 110 + s * 3
            g = 72 + s * 2
            b = 40 + s
            px.append((max(25, min(160, r)), max(18, min(120, g)), max(10, min(80, b)), 255))
    save(TEX / "post_wood.png", w, h, px)


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    make_exit("exit.png", arrow=None)
    make_exit("exit_up.png", arrow="up")
    make_exit("exit_left.png", arrow="left")
    make_exit("exit_right.png", arrow="right")
    make_mat_rubber("mat_rubber.png")
    make_mat_checkered("mat_checkered.png")
    make_mat_orange_trim("mat_orange_trim.png")
    make_mat_pitstall("mat_pitstall.png")
    wood_post()


if __name__ == "__main__":
    main()
