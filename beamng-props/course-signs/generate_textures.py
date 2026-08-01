#!/usr/bin/env python3
"""Generate Parker 400 course sign textures (arrows, wrong way, danger)."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"

# Compact 5x7 font for labels
FONT: dict[str, list[str]] = {
    " ": ["....."] * 7,
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
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

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", ihdr),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c0, c1, t):
    return tuple(lerp(c0[i], c1[i], t) for i in range(4))


def new_canvas(w, h, color):
    return [color] * (w * h)


def setp(px, w, h, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        px[y * w + x] = c


def blendp(px, w, h, x, y, c, a=1.0):
    if not (0 <= x < w and 0 <= y < h):
        return
    i = y * w + x
    px[i] = mix(px[i], c, a)


def fill_rect(px, w, h, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(h, y1)):
        for x in range(max(0, x0), min(w, x1)):
            px[y * w + x] = c


def fill_circle(px, w, h, cx, cy, r, c):
    r2 = r * r
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                setp(px, w, h, x, y, c)


def draw_line(px, w, h, x0, y0, x1, y1, c, thickness=8):
    steps = max(1, int(math.hypot(x1 - x0, y1 - y0)))
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        fill_circle(px, w, h, x, y, thickness / 2, c)


def draw_poly(px, w, h, points, c):
    """Fill convex polygon via scanline."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = max(0, int(min(ys)))
    y_max = min(h - 1, int(max(ys)))
    n = len(points)
    for y in range(y_min, y_max + 1):
        xs = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                if y1 != y0:
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x_a = int(xs[i])
            x_b = int(xs[i + 1])
            if x_a > x_b:
                x_a, x_b = x_b, x_a
            for x in range(max(0, x_a), min(w, x_b + 1)):
                px[y * w + x] = c


def draw_text(px, w, h, text, cx, cy, scale, color):
    glyphs = [FONT.get(ch, FONT[" "]) for ch in text.upper()]
    gw, gh = 5, 7
    gap = 1
    total_w = len(glyphs) * (gw + gap) * scale - gap * scale
    total_h = gh * scale
    x0 = int(cx - total_w / 2)
    y0 = int(cy - total_h / 2)
    for i, glyph in enumerate(glyphs):
        ox = x0 + i * (gw + gap) * scale
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell != "#":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        setp(px, w, h, ox + gx * scale + sx, y0 + gy * scale + sy, color)


def plate_bg(w, h, face="arrow"):
    if face == "arrow":
        base = (245, 168, 42, 255)  # desert race orange
        border = (20, 20, 20, 255)
        ink = (15, 15, 15, 255)
    elif face == "wrong":
        base = (190, 28, 28, 255)
        border = (255, 255, 255, 255)
        ink = (255, 255, 255, 255)
    elif face == "danger":
        base = (240, 200, 40, 255)
        border = (20, 20, 20, 255)
        ink = (15, 15, 15, 255)
    else:
        base = (236, 232, 220, 255)
        border = (20, 20, 20, 255)
        ink = (15, 15, 15, 255)

    px = new_canvas(w, h, base)
    m = 18
    fill_rect(px, w, h, 0, 0, w, m, border)
    fill_rect(px, w, h, 0, h - m, w, h, border)
    fill_rect(px, w, h, 0, 0, m, h, border)
    fill_rect(px, w, h, w - m, 0, w, h, border)
    # subtle dirt
    for y in range(h):
        for x in range(w):
            if ((x * 37 + y * 19) % 29) == 0:
                px[y * w + x] = mix(px[y * w + x], (120, 90, 60, 255), 0.12)
    return px, border, ink


def arrow_head(cx, cy, angle_deg, size, ink):
    """Triangle head pointing along angle (0=right, 90=up in image space? y increases down).
    In image coords: 0 deg = +X (right), 90 deg = +Y (down).
    For 'up the course' we use angle=-90 (pointing up / -Y).
    """
    ang = math.radians(angle_deg)
    tip = (cx + math.cos(ang) * size, cy + math.sin(ang) * size)
    left = (
        cx + math.cos(ang + 2.5) * size * 0.15 + math.cos(ang + math.pi / 2) * size * 0.55,
        cy + math.sin(ang + 2.5) * size * 0.15 + math.sin(ang + math.pi / 2) * size * 0.55,
    )
    # Better head geometry
    back = size * 0.55
    spread = size * 0.62
    tip = (cx + math.cos(ang) * size * 0.05, cy + math.sin(ang) * size * 0.05)
    # Actually tip at far end
    tip = (cx + math.cos(ang) * size, cy + math.sin(ang) * size)
    p1 = (
        cx + math.cos(ang) * (size - back) + math.cos(ang + math.pi / 2) * spread,
        cy + math.sin(ang) * (size - back) + math.sin(ang + math.pi / 2) * spread,
    )
    p2 = (
        cx + math.cos(ang) * (size - back) + math.cos(ang - math.pi / 2) * spread,
        cy + math.sin(ang) * (size - back) + math.sin(ang - math.pi / 2) * spread,
    )
    return [tip, p1, p2]


def draw_straight_arrow(px, w, h, ink):
    cx, cy = w / 2, h / 2 + 10
    # shaft
    draw_line(px, w, h, cx, cy + 110, cx, cy - 40, ink, thickness=28)
    head = arrow_head(cx, cy - 40, -90, 95, ink)
    # shift head so tip is above
    draw_poly(px, w, h, [(cx, cy - 145), (cx - 70, cy - 40), (cx + 70, cy - 40)], ink)


def draw_bent_arrow(px, w, h, ink, direction: str, slight: bool):
    """direction: left|right. slight=True ~35 bend, False ~90."""
    mirror = -1 if direction == "left" else 1
    cx, cy = w / 2, h / 2 + 30
    draw_line(px, w, h, cx, cy + 105, cx, cy + 5, ink, thickness=26)
    if slight:
        x1 = cx + mirror * 100
        y1 = cy - 100
        draw_line(px, w, h, cx, cy + 5, x1, y1, ink, thickness=26)
        tip_x = x1 + mirror * 58
        tip_y = y1 - 58
        draw_poly(
            px,
            w,
            h,
            [
                (tip_x, tip_y),
                (x1 - mirror * 28, y1 - 52),
                (x1 + mirror * 52, y1 + 28),
            ],
            ink,
        )
    else:
        x1 = cx + mirror * 105
        y1 = cy + 5
        draw_line(px, w, h, cx, cy + 5, x1, y1, ink, thickness=26)
        tip_x = x1 + mirror * 78
        draw_poly(
            px,
            w,
            h,
            [
                (tip_x, y1),
                (x1 - mirror * 8, y1 - 58),
                (x1 - mirror * 8, y1 + 58),
            ],
            ink,
        )


def draw_chevrons(px, w, h, ink, direction: str, count: int):
    mirror = -1 if direction == "left" else 1
    cx = w / 2
    # Distinct stacked chevrons (not a continuous zigzag)
    size = 72
    thick = 18
    spacing = 145
    start_y = h / 2 + (count - 1) * spacing / 2
    for i in range(count):
        cy = start_y - i * spacing
        tip_x = cx + mirror * (size + 18)
        tip_y = cy
        back_x = cx - mirror * 8
        arm = size * 0.55
        for t in range(0, 101):
            u = t / 100
            x = tip_x + (back_x - tip_x) * u
            y = tip_y - arm * u
            fill_circle(px, w, h, x, y, thick / 2, ink)
        for t in range(0, 101):
            u = t / 100
            x = tip_x + (back_x - tip_x) * u
            y = tip_y + arm * u
            fill_circle(px, w, h, x, y, thick / 2, ink)


def draw_wrong_way_face(px, w, h, ink, border):
    # white stripe band look
    fill_rect(px, w, h, 40, int(h * 0.28), w - 40, int(h * 0.72), (255, 255, 255, 255))
    draw_text(px, w, h, "WRONG", w / 2, h * 0.40, 10, (190, 28, 28, 255))
    draw_text(px, w, h, "WAY", w / 2, h * 0.58, 12, (190, 28, 28, 255))


def draw_danger_x(px, w, h, ink):
    # big X
    m = 70
    draw_line(px, w, h, m, m, w - m, h - m, ink, thickness=36)
    draw_line(px, w, h, w - m, m, m, h - m, ink, thickness=36)
    draw_text(px, w, h, "DANGER", w / 2, h - 48, 6, ink)


def downsample(hi, sw, sh, w, h):
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
    return out


def save_sign(name: str, drawer, face="arrow"):
    sw, sh = 768, 768
    w, h = 384, 384
    hi, border, ink = plate_bg(sw, sh, face=face)
    drawer(hi, sw, sh, ink, border)
    out = downsample(hi, sw, sh, w, h)
    path = TEX / f"{name}.png"
    path.write_bytes(png_rgba(w, h, out))
    print(f"wrote {path}")


def main():
    TEX.mkdir(parents=True, exist_ok=True)

    # Arrow fronts
    save_sign(
        "arrow_straight",
        lambda px, w, h, ink, border: draw_straight_arrow(px, w, h, ink),
    )
    for d in ("left", "right"):
        save_sign(
            f"arrow_slight_{d}",
            lambda px, w, h, ink, border, d=d: draw_bent_arrow(px, w, h, ink, d, True),
        )
        save_sign(
            f"arrow_turn_{d}",
            lambda px, w, h, ink, border, d=d: draw_bent_arrow(px, w, h, ink, d, False),
        )
        save_sign(
            f"arrow_double_{d}",
            lambda px, w, h, ink, border, d=d: draw_chevrons(px, w, h, ink, d, 2),
        )
        save_sign(
            f"arrow_triple_{d}",
            lambda px, w, h, ink, border, d=d: draw_chevrons(px, w, h, ink, d, 3),
        )

    # Back face for all arrow signs
    save_sign(
        "arrow_back_wrong_way",
        lambda px, w, h, ink, border: draw_wrong_way_face(px, w, h, ink, border),
        face="wrong",
    )

    # Standalone wrong way (taller rectangle style — still square canvas OK)
    save_sign(
        "sign_wrong_way",
        lambda px, w, h, ink, border: draw_wrong_way_face(px, w, h, ink, border),
        face="wrong",
    )

    # Danger X
    save_sign(
        "sign_danger_x",
        lambda px, w, h, ink, border: draw_danger_x(px, w, h, ink),
        face="danger",
    )

    # Shared post materials (reuse style)
    # simple wood / metal copies if missing
    wood = TEX / "post_wood.png"
    if not wood.exists():
        # minimal wood
        ww, wh = 128, 512
        px = []
        for y in range(wh):
            for x in range(ww):
                s = ((x * 17 + y // 8) % 13) - 6
                px.append((108 + s * 3, 72 + s * 2, 40 + s, 255))
        wood.write_bytes(png_rgba(ww, wh, px))
        print(f"wrote {wood}")


if __name__ == "__main__":
    main()
