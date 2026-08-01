#!/usr/bin/env python3
"""
Parker 400 course signs — lime-green turn arrows, yellow straight / TURN AHEAD.
Portrait plates matching desert race marker references.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
sys.path.insert(0, str(ROOT.parent / "_shared"))
from sign_draw import (  # noqa: E402
    arrow_straight_up,
    arrow_turn,
    canvas,
    downsample2,
    draw_header,
    draw_logo_row,
    draw_text,
    fill_rect,
    save_png,
    thick_line,
    fill_circle,
)


INK = (10, 10, 10, 255)
LIME = (140, 220, 40, 255)  # neon course green
YELLOW = (250, 210, 20, 255)
WHITE = (250, 250, 250, 255)
RED = (210, 30, 30, 255)


def plate(bg, draw_fn, path: Path):
    sw, sh = 640, 1120
    px = canvas(sw, sh, bg)
    for t in range(3):
        for x in range(sw):
            px[t * sw + x] = INK
            px[(sh - 1 - t) * sw + x] = INK
        for y in range(sh):
            px[y * sw + t] = INK
            px[y * sw + (sw - 1 - t)] = INK
    draw_header(px, sw, sh, INK)
    draw_fn(px, sw, sh)
    draw_logo_row(px, sw, sh, int(sh * 0.90), INK, bg)
    w, h, out = downsample2(sw, sh, px)
    save_png(path, w, h, out)


def make_turn_arrow(direction: str, path: Path):
    def draw(px, w, h):
        y0, y1 = int(h * 0.12), int(h * 0.78)
        arrow_turn(px, w, h, INK, direction, y0, y1, thickness=max(18, w // 14))

    plate(LIME, draw, path)


def make_straight(path: Path):
    def draw(px, w, h):
        y0, y1 = int(h * 0.14), int(h * 0.78)
        arrow_straight_up(px, w, h, INK, y0, y1, thickness=max(22, w // 12))

    plate(YELLOW, draw, path)


def make_turn_ahead(path: Path):
    def draw(px, w, h):
        draw_text(px, w, h, "TURN", w // 2, int(h * 0.38), 16, INK)
        draw_text(px, w, h, "AHEAD", w // 2, int(h * 0.55), 14, INK)

    plate(YELLOW, draw, path)


def make_slight(direction: str, path: Path):
    def draw(px, w, h):
        # Shallower curve = slight
        y0, y1 = int(h * 0.14), int(h * 0.78)
        cx = w // 2
        thick = max(16, w // 16)
        # Shaft
        thick_line(px, w, h, cx, y1 - 6, cx, int(h * 0.45), thick, INK)
        # Diagonal
        side = -1 if direction == "left" else 1
        thick_line(
            px,
            w,
            h,
            cx,
            int(h * 0.45),
            cx + side * int(w * 0.28),
            int(h * 0.22),
            thick,
            INK,
        )
        # Head
        hx = cx + side * int(w * 0.28)
        hy = int(h * 0.22)
        tip = hx + side * int(thick * 2.2)
        for dy in range(-int(thick * 1.6), int(thick * 1.6) + 1):
            if direction == "right":
                fill_rect(px, w, h, hx, hy + dy, tip, hy + dy + 1, INK)
            else:
                fill_rect(px, w, h, tip, hy + dy, hx, hy + dy + 1, INK)

    plate(LIME, draw, path)


def make_wrong_way(path: Path):
    def draw(px, w, h):
        draw_text(px, w, h, "WRONG", w // 2, int(h * 0.38), 14, WHITE)
        draw_text(px, w, h, "WAY", w // 2, int(h * 0.55), 16, WHITE)

    plate(RED, draw, path)


def make_danger(path: Path):
    def draw(px, w, h):
        # Big X
        thick = max(16, w // 14)
        thick_line(px, w, h, int(w * 0.2), int(h * 0.22), int(w * 0.8), int(h * 0.7), thick, INK)
        thick_line(px, w, h, int(w * 0.8), int(h * 0.22), int(w * 0.2), int(h * 0.7), thick, INK)

    plate(YELLOW, draw, path)


def make_double(direction: str, path: Path):
    def draw(px, w, h):
        y0, y1 = int(h * 0.14), int(h * 0.72)
        arrow_turn(px, w, h, INK, direction, y0, y1, thickness=max(14, w // 18))
        # Second chevron hint
        draw_text(px, w, h, "<<", w // 2 if direction == "left" else w // 2, int(h * 0.18), 6, INK)

    plate(LIME, draw, path)


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    make_straight(TEX / "arrow_straight.png")
    make_turn_arrow("left", TEX / "arrow_turn_left.png")
    make_turn_arrow("right", TEX / "arrow_turn_right.png")
    make_slight("left", TEX / "arrow_slight_left.png")
    make_slight("right", TEX / "arrow_slight_right.png")
    make_double("left", TEX / "arrow_double_left.png")
    make_double("right", TEX / "arrow_double_right.png")
    # Triple = same as double for now with extra mark
    make_double("left", TEX / "arrow_triple_left.png")
    make_double("right", TEX / "arrow_triple_right.png")
    make_turn_ahead(TEX / "turn_ahead.png")
    make_wrong_way(TEX / "sign_wrong_way.png")
    make_danger(TEX / "sign_danger_x.png")
    # Backing used on some props
    make_wrong_way(TEX / "arrow_back_wrong_way.png")
    print("DONE course signs")


if __name__ == "__main__":
    main()
