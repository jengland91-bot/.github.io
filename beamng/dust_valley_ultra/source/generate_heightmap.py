#!/usr/bin/env python3
"""Generate Dust Valley Ultra heightmap + layout overview for BeamNG World Editor import.

Outputs (16-bit PNG heightmap recommended by BeamNG docs):
  - heightmap_2048.png  (16-bit grayscale)
  - layout_overview.png (color-coded design map)
  - heightmap_preview.png (8-bit shaded preview)
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 2048  # resolution (power of two)
WORLD_M = 4096.0  # map size in meters (mid-big Ultra 4 park)
SQUARE_SIZE = WORLD_M / SIZE  # 2 m per sample
MAX_HEIGHT_M = 180.0  # BeamNG TerrainBlock maxHeight target


def hash2(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    s = np.sin(x * 127.1 + y * 311.7) * 43758.5453
    return s - np.floor(s)


def value_noise(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    x0 = np.floor(x)
    y0 = np.floor(y)
    fx = x - x0
    fy = y - y0
    ux = fx * fx * (3.0 - 2.0 * fx)
    uy = fy * fy * (3.0 - 2.0 * fy)

    n00 = hash2(x0, y0)
    n10 = hash2(x0 + 1, y0)
    n01 = hash2(x0, y0 + 1)
    n11 = hash2(x0 + 1, y0 + 1)
    nx0 = n00 * (1 - ux) + n10 * ux
    nx1 = n01 * (1 - ux) + n11 * ux
    return nx0 * (1 - uy) + nx1 * uy


def fbm(x: np.ndarray, y: np.ndarray, octaves: int = 5, lac: float = 2.0, gain: float = 0.5) -> np.ndarray:
    amp = 1.0
    freq = 1.0
    total = np.zeros_like(x, dtype=np.float64)
    norm = 0.0
    for _ in range(octaves):
        total += amp * value_noise(x * freq, y * freq)
        norm += amp
        amp *= gain
        freq *= lac
    return total / max(norm, 1e-9)


def smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def gaussian_blob(x: np.ndarray, y: np.ndarray, cx: float, cy: float, sx: float, sy: float) -> np.ndarray:
    return np.exp(-(((x - cx) ** 2) / (2 * sx * sx) + ((y - cy) ** 2) / (2 * sy * sy)))


def polyline_distance(px: np.ndarray, py: np.ndarray, points: list[tuple[float, float]]) -> np.ndarray:
    """Approximate distance to a polyline in normalized 0..1 coords."""
    best = np.full_like(px, 1e9, dtype=np.float64)
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dx = x1 - x0
        dy = y1 - y0
        len2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((px - x0) * dx + (py - y0) * dy) / len2, 0.0, 1.0)
        qx = x0 + t * dx
        qy = y0 + t * dy
        dist = np.hypot(px - qx, py - qy)
        best = np.minimum(best, dist)
    return best


def build_height() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    u = xs / (SIZE - 1)
    v = ys / (SIZE - 1)

    # Base desert: broad dunes + gentle valleys
    base = 0.34 + 0.10 * fbm(u * 3.5, v * 3.5, octaves=4)
    base += 0.045 * fbm(u * 9.0 + 20, v * 9.0 - 7, octaves=3)
    base += 0.02 * np.sin(u * math.pi * 2.2) * np.cos(v * math.pi * 1.6)

    masks: dict[str, np.ndarray] = {}

    # Main Ultra 4 desert loop (fast sandy corridor)
    loop = [
        (0.22, 0.72),
        (0.38, 0.82),
        (0.58, 0.84),
        (0.76, 0.74),
        (0.82, 0.58),
        (0.78, 0.42),
        (0.62, 0.30),
        (0.42, 0.26),
        (0.26, 0.34),
        (0.18, 0.50),
        (0.20, 0.64),
        (0.22, 0.72),
    ]
    d_loop = polyline_distance(u, v, loop)
    race_w = 0.055
    race_mask = 1.0 - smoothstep(race_w * 0.55, race_w * 1.35, d_loop)
    masks["race"] = race_mask

    # Flatten race surface slightly above dune floor, with soft berms
    race_height = 0.36 + 0.01 * fbm(u * 14, v * 14, octaves=2)
    berm = smoothstep(race_w * 0.7, race_w * 1.15, d_loop) * (1.0 - smoothstep(race_w * 1.15, race_w * 1.7, d_loop))
    race_height = race_height + berm * 0.035
    h = base * (1.0 - race_mask) + race_height * race_mask

    # Whoops field — west/southwest of the loop
    whoops_center = gaussian_blob(u, v, 0.28, 0.62, 0.10, 0.14)
    along = (u - 0.18) * 0.6 + (v - 0.55) * 0.8
    whoops = whoops_center * (0.028 * np.sin(along * 55.0) ** 2 + 0.012 * np.sin(along * 28.0))
    h += whoops
    masks["whoops"] = whoops_center

    # Long valley cut — north-central speed section
    valley_line = [(0.30, 0.18), (0.48, 0.22), (0.66, 0.20), (0.80, 0.28)]
    d_valley = polyline_distance(u, v, valley_line)
    valley_mask = 1.0 - smoothstep(0.02, 0.075, d_valley)
    h -= valley_mask * 0.09
    # Valley walls
    wall = smoothstep(0.02, 0.045, d_valley) * (1.0 - smoothstep(0.045, 0.10, d_valley))
    h += wall * 0.05
    masks["valley"] = valley_mask

    # Jump line / tabletops — south arc
    jump_line = [(0.40, 0.88), (0.52, 0.90), (0.64, 0.88), (0.74, 0.82)]
    d_jump = polyline_distance(u, v, jump_line)
    jump_band = 1.0 - smoothstep(0.012, 0.05, d_jump)
    # Series of ramp/tabletop pulses along the line
    jump_phase = u * 38.0 + v * 6.0
    tablets = np.clip(np.sin(jump_phase), 0.0, 1.0) ** 1.6
    lips = np.clip(np.sin(jump_phase + 0.8), 0.0, 1.0) ** 3
    h += jump_band * (0.045 * tablets + 0.02 * lips)
    masks["jumps"] = jump_band

    # Rock trails off to the sides (east ridge + NW technical)
    rock_east = gaussian_blob(u, v, 0.88, 0.48, 0.08, 0.16)
    rock_nw = gaussian_blob(u, v, 0.18, 0.22, 0.09, 0.10)
    rock_se = gaussian_blob(u, v, 0.86, 0.78, 0.07, 0.08)
    rock_mask = np.clip(rock_east + rock_nw + rock_se, 0.0, 1.0)
    rock_detail = fbm(u * 28.0, v * 28.0, octaves=5, lac=2.1, gain=0.55)
    rock_ridges = np.abs(fbm(u * 18.0 + 3, v * 18.0 - 2, octaves=4) * 2.0 - 1.0)
    h += rock_mask * (0.07 + 0.08 * rock_detail + 0.05 * rock_ridges)
    # Keep a narrow trailable trough through rock zones
    rock_trail_e = polyline_distance(u, v, [(0.84, 0.68), (0.90, 0.55), (0.88, 0.40), (0.82, 0.32)])
    rock_trail_nw = polyline_distance(u, v, [(0.10, 0.30), (0.16, 0.22), (0.24, 0.16), (0.32, 0.20)])
    # Carve a readable trough through the rock noise
    trail_carve = rock_mask * (1.0 - smoothstep(0.008, 0.028, np.minimum(rock_trail_e, rock_trail_nw)))
    h -= trail_carve * 0.035
    masks["rocks"] = rock_mask

    # Staging / pits — flat pad SW
    pits = gaussian_blob(u, v, 0.18, 0.82, 0.07, 0.05)
    h = h * (1.0 - pits * 0.85) + 0.33 * pits
    masks["pits"] = pits

    # Soft rim mountains so the world feels enclosed without blocking the park
    edge = np.minimum.reduce([u, v, 1 - u, 1 - v])
    rim = 1.0 - smoothstep(0.02, 0.12, edge)
    h += rim * (0.08 + 0.04 * fbm(u * 6, v * 6, octaves=3))

    h = np.clip(h, 0.05, 0.95)
    return h.astype(np.float64), masks


def save_heightmap(h: np.ndarray, path: Path) -> None:
    # 16-bit PNG for World Editor heightmap import
    data = (h * 65535.0).astype(np.uint16)
    Image.fromarray(data).save(path)


def save_preview(h: np.ndarray, path: Path) -> None:
    data = (h * 255.0).astype(np.uint8)
    Image.fromarray(data, mode="L").save(path)


def save_layout(h: np.ndarray, masks: dict[str, np.ndarray], path: Path) -> None:
    # Colored overview for the design doc
    rgb = np.zeros((SIZE, SIZE, 3), dtype=np.float64)
    # Shade from height
    shade = (h - h.min()) / (h.max() - h.min() + 1e-9)
    rgb[..., 0] = 0.45 + 0.40 * shade
    rgb[..., 1] = 0.32 + 0.28 * shade
    rgb[..., 2] = 0.16 + 0.12 * shade

    def tint(mask: np.ndarray, color: tuple[float, float, float], strength: float = 0.55) -> None:
        m = np.clip(mask, 0, 1)[..., None]
        c = np.array(color)[None, None, :]
        rgb[:] = rgb * (1 - m * strength) + c * (m * strength)

    tint(masks["race"], (0.95, 0.78, 0.28), 0.45)  # gold race line
    tint(masks["whoops"], (0.95, 0.45, 0.15), 0.50)  # orange whoops
    tint(masks["valley"], (0.25, 0.45, 0.75), 0.45)  # blue valley
    tint(masks["jumps"], (0.95, 0.20, 0.25), 0.55)  # red jumps
    tint(masks["rocks"], (0.45, 0.40, 0.38), 0.55)  # rock gray
    tint(masks["pits"], (0.20, 0.75, 0.45), 0.55)  # green pits

    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), mode="RGB")
    # Downscale for docs + draw legend
    preview = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1024, 1180), (18, 16, 14))
    canvas.paste(preview, (0, 0))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    draw.text((24, 1040), "Dust Valley Ultra — 4 km desert park", fill=(245, 235, 210), font=font)
    legend = [
        ((242, 199, 71), "Main Ultra 4 desert loop"),
        ((242, 115, 38), "Whoops field"),
        ((64, 115, 191), "Valley speed cut"),
        ((242, 51, 64), "Jump / tabletop line"),
        ((115, 102, 97), "Side rock trails"),
        ((51, 191, 115), "Pits / staging"),
    ]
    x = 24
    y = 1080
    for color, label in legend:
        draw.rectangle([x, y, x + 16, y + 16], fill=color)
        draw.text((x + 24, y - 2), label, fill=(220, 210, 195), font=font_sm)
        x += 170
        if x > 850:
            x = 24
            y += 28
    canvas.save(path)


def main() -> None:
    out = Path(__file__).resolve().parent
    print(f"Generating {SIZE}x{SIZE} heightmap ({WORLD_M:.0f} m, squareSize={SQUARE_SIZE:.2f} m)...")
    h, masks = build_height()
    save_heightmap(h, out / "heightmap_2048.png")
    save_preview(h, out / "heightmap_preview.png")
    save_layout(h, masks, out / "layout_overview.png")

    meta = out / "heightmap_meta.json"
    meta.write_text(
        "{\n"
        f'  "resolution": {SIZE},\n'
        f'  "worldSizeMeters": {WORLD_M},\n'
        f'  "squareSize": {SQUARE_SIZE},\n'
        f'  "recommendedMaxHeight": {MAX_HEIGHT_M},\n'
        f'  "format": "16-bit PNG grayscale",\n'
        f'  "importNotes": "In World Editor: Terrain > Heightmap Import. Use squareSize={SQUARE_SIZE} and maxHeight around {MAX_HEIGHT_M}."\n'
        "}\n",
        encoding="utf-8",
    )
    print("Wrote:")
    for name in ("heightmap_2048.png", "heightmap_preview.png", "layout_overview.png", "heightmap_meta.json"):
        print(" -", out / name)


if __name__ == "__main__":
    main()
