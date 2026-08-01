"""Shared drawing helpers for Parker 400 race-style signs (portrait plates)."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


# 5x7 uppercase + digits + punctuation
FONT: dict[str, list[str]] = {
    " ": ["....."] * 7,
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
}


def png_rgba(w: int, h: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        row = y * w
        for x in range(w):
            raw.extend(pixels[row + x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 6)),
            chunk(b"IEND", b""),
        ]
    )


def save_png(path: Path, w: int, h: int, pixels) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote {path}")


def canvas(w, h, color):
    return [color] * (w * h)


def fill_rect(px, w, h, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(h, y1)):
        row = y * w
        for x in range(max(0, x0), min(w, x1)):
            px[row + x] = c


def fill_circle(px, w, h, cx, cy, r, c):
    r2 = r * r
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if 0 <= x < w and 0 <= y < h and (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                px[y * w + x] = c


def draw_text(px, w, h, text: str, cx: int, cy: int, scale: int, color):
    glyphs = [FONT.get(ch, FONT[" "]) for ch in text.upper()]
    gw, gh, gap = 5, 7, 1
    total_w = len(glyphs) * (gw + gap) * scale - gap * scale
    total_h = gh * scale
    x0 = cx - total_w // 2
    y0 = cy - total_h // 2
    for i, glyph in enumerate(glyphs):
        ox = x0 + i * (gw + gap) * scale
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell != "#":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        x = ox + gx * scale + sx
                        y = y0 + gy * scale + sy
                        if 0 <= x < w and 0 <= y < h:
                            px[y * w + x] = color


def draw_shield(px, w, h, cx: int, cy: int, bw: int, bh: int, ink, lines: list[str]):
    """Simple championship-style shield logo (layout stand-in)."""
    x0, x1 = cx - bw // 2, cx + bw // 2
    y0, y1 = cy - bh // 2, cy + bh // 2
    # Shield outline
    for y in range(y0, y1):
        t = (y - y0) / max(1, bh - 1)
        # tapers in lower third
        inset = int(bw * 0.35 * max(0.0, (t - 0.55) / 0.45)) if t > 0.55 else 0
        fill_rect(px, w, h, x0 + inset, y, x1 - inset, y + 1, ink)
    # Hollow interior
    pad = max(2, bw // 12)
    for y in range(y0 + pad, y1 - pad):
        t = (y - y0) / max(1, bh - 1)
        inset = int(bw * 0.35 * max(0.0, (t - 0.55) / 0.45)) if t > 0.55 else 0
        fill_rect(px, w, h, x0 + inset + pad, y, x1 - inset - pad, y + 1, (255, 255, 255, 255))
    # Restore bg color via caller after — actually fill with white then text; for colored
    # backgrounds we need bg color. Pass bg.
    return


def draw_shield_on(px, w, h, cx, cy, bw, bh, ink, bg, lines: list[str]):
    x0, x1 = cx - bw // 2, cx + bw // 2
    y0, y1 = cy - bh // 2, cy + bh // 2
    for y in range(y0, y1):
        t = (y - y0) / max(1, max(1, bh - 1))
        inset = int(bw * 0.38 * max(0.0, (t - 0.55) / 0.45)) if t > 0.55 else 0
        fill_rect(px, w, h, x0 + inset, y, x1 - inset, y + 1, ink)
    pad = max(2, bw // 14)
    for y in range(y0 + pad, y1 - pad - 2):
        t = (y - y0) / max(1, bh - 1)
        inset = int(bw * 0.38 * max(0.0, (t - 0.55) / 0.45)) if t > 0.55 else 0
        fill_rect(px, w, h, x0 + inset + pad, y, x1 - inset - pad, y + 1, bg)
    # Text lines inside shield
    scales = [max(1, bw // 42), max(1, bw // 55), max(1, bw // 55)]
    for i, line in enumerate(lines[:3]):
        draw_text(px, w, h, line, cx, y0 + pad + 8 + i * (bh // 5), scales[min(i, 2)], ink)
    # Stars near point
    star_y = y1 - pad - 4
    for dx in (-bw // 6, 0, bw // 6):
        fill_circle(px, w, h, cx + dx, star_y, max(1, bw // 40), ink)


def draw_logo_row(px, w, h, cy: int, ink, bg):
    """Bottom sponsor row with clear spacing (layout placeholders)."""
    draw_text(px, w, h, "DESERT", w // 6, cy - 10, max(1, w // 100), ink)
    draw_text(px, w, h, "SERIES", w // 6, cy + 6, max(1, w // 100), ink)
    draw_shield_on(
        px,
        w,
        h,
        w // 2,
        cy,
        max(40, w // 4),
        max(28, h // 11),
        ink,
        bg,
        ["AMERICAN", "OFF-ROAD", "RACING"],
    )
    draw_text(px, w, h, "RACE", (5 * w) // 6, cy - 10, max(1, w // 100), ink)
    draw_text(px, w, h, "MARK", (5 * w) // 6, cy + 6, max(1, w // 100), ink)


def draw_header(px, w, h, ink):
    # Two lines with enough vertical gap for 5x7 glyphs at this scale
    sc = max(1, w // 70)
    draw_text(px, w, h, "ILLEGAL TO", w // 2, int(h * 0.050), sc, ink)
    draw_text(px, w, h, "REMOVE !", w // 2, int(h * 0.118), sc, ink)


def thick_line(px, w, h, x0, y0, x1, y1, thickness, c):
    steps = max(1, int(math.hypot(x1 - x0, y1 - y0)))
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        fill_circle(px, w, h, x, y, thickness / 2, c)


def arrow_straight_up(px, w, h, ink, y0, y1, thickness):
    """Classic thick up-arrow: shaft + triangular head at top."""
    cx = w // 2
    head_h = int((y1 - y0) * 0.28)
    tip_y = y0
    head_base = y0 + head_h
    shaft_top = head_base - thickness // 3
    fill_rect(px, w, h, cx - thickness // 2, shaft_top, cx + thickness // 2, y1, ink)
    half_base = int(thickness * 1.85)
    for y in range(tip_y, head_base):
        t = (y - tip_y) / max(1, head_base - tip_y)
        half = int(half_base * t) + 1
        fill_rect(px, w, h, cx - half, y, cx + half, y + 1, ink)


def arrow_turn(px, w, h, ink, direction: str, y0, y1, thickness):
    """Clean 90° turn: vertical shaft, quarter curve, horizontal to side + head."""
    cx = w // 2
    bend_y = y0 + int((y1 - y0) * 0.38)
    fill_rect(px, w, h, cx - thickness // 2, bend_y, cx + thickness // 2, y1 - 4, ink)

    side = -1 if direction == "left" else 1
    r = int(w * 0.26)
    steps = 56
    for i in range(steps + 1):
        ang = (math.pi / 2) * (i / steps)
        if direction == "right":
            x = cx + r * (1 - math.cos(ang))
            y = bend_y - r * math.sin(ang)
        else:
            x = cx - r * (1 - math.cos(ang))
            y = bend_y - r * math.sin(ang)
        fill_circle(px, w, h, x, y, thickness / 2, ink)

    end_x = cx + side * int(w * 0.36)
    run_y = bend_y - r
    fill_rect(
        px,
        w,
        h,
        min(cx, end_x),
        run_y - thickness // 2,
        max(cx, end_x),
        run_y + thickness // 2,
        ink,
    )

    # Triangular arrowhead pointing outward
    tip_x = end_x + side * int(thickness * 2.2)
    half = int(thickness * 1.7)
    head_len = abs(tip_x - end_x)
    for i in range(head_len + 1):
        t = i / max(1, head_len)
        half_now = int(half * (1.0 - t)) + 1
        x = end_x + side * i
        fill_rect(px, w, h, x, run_y - half_now, x + 1, run_y + half_now + 1, ink)


def downsample2(sw, sh, hi):
    w, h = sw // 2, sh // 2
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
    return w, h, out
