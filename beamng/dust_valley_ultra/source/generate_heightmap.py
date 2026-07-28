#!/usr/bin/env python3
"""Generate Dust Valley Ultra heightmap, colored minimap, and layout overview.

Outputs:
  - heightmap_2048.png      (16-bit grayscale for World Editor)
  - heightmap_preview.png   (8-bit shaded preview)
  - layout_overview.png     (design map + legend)
  - minimap_terrain.png     (in-game minimap with each trail a unique color)
  - trail_colors.json       (color key for docs / UI)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 2048  # resolution (power of two)
WORLD_M = 4096.0  # map size in meters (mid-big Ultra 4 park)
SQUARE_SIZE = WORLD_M / SIZE  # 2 m per sample
MAX_HEIGHT_M = 180.0  # BeamNG TerrainBlock maxHeight target

# Each trail gets a unique minimap color (RGB 0-255).
TRAILS: dict[str, dict] = {
    "race": {
        "label": "Main Ultra 4 loop",
        "color": (242, 199, 71),  # gold
        "width": 0.055,
        "points": [
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
        ],
    },
    "whoops": {
        "label": "Whoops field",
        "color": (242, 115, 38),  # orange
        "width": 0.04,
        "points": [
            (0.18, 0.70),
            (0.22, 0.64),
            (0.26, 0.58),
            (0.30, 0.52),
            (0.34, 0.48),
        ],
    },
    "valley": {
        "label": "Valley speed cut",
        "color": (64, 140, 220),  # blue
        "width": 0.035,
        "points": [
            (0.30, 0.18),
            (0.48, 0.22),
            (0.66, 0.20),
            (0.80, 0.28),
        ],
    },
    "jumps": {
        "label": "Jump / tabletop line",
        "color": (230, 55, 70),  # red
        "width": 0.028,
        "points": [
            (0.40, 0.88),
            (0.52, 0.90),
            (0.64, 0.88),
            (0.74, 0.82),
        ],
    },
    "rocks_east": {
        "label": "East rock trail",
        "color": (168, 92, 220),  # purple
        "width": 0.018,
        "points": [
            (0.84, 0.68),
            (0.90, 0.55),
            (0.88, 0.40),
            (0.82, 0.32),
        ],
    },
    "rocks_nw": {
        "label": "NW rock trail",
        "color": (40, 190, 175),  # teal
        "width": 0.018,
        "points": [
            (0.10, 0.30),
            (0.16, 0.22),
            (0.24, 0.16),
            (0.32, 0.20),
        ],
    },
    "pits": {
        "label": "Pits / staging",
        "color": (50, 200, 110),  # green
        "width": 0.03,
        "points": [
            (0.14, 0.84),
            (0.18, 0.82),
            (0.22, 0.80),
        ],
    },
}


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


def trail_mask(u: np.ndarray, v: np.ndarray, key: str) -> np.ndarray:
    trail = TRAILS[key]
    dist = polyline_distance(u, v, trail["points"])
    w = trail["width"]
    return 1.0 - smoothstep(w * 0.45, w * 1.25, dist)


def build_height() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    u = xs / (SIZE - 1)
    v = ys / (SIZE - 1)

    # Base desert: broad dunes + gentle valleys
    base = 0.34 + 0.10 * fbm(u * 3.5, v * 3.5, octaves=4)
    base += 0.045 * fbm(u * 9.0 + 20, v * 9.0 - 7, octaves=3)
    base += 0.02 * np.sin(u * math.pi * 2.2) * np.cos(v * math.pi * 1.6)

    masks: dict[str, np.ndarray] = {}

    loop = TRAILS["race"]["points"]
    d_loop = polyline_distance(u, v, loop)
    race_w = TRAILS["race"]["width"]
    race_mask = trail_mask(u, v, "race")
    masks["race"] = race_mask

    race_height = 0.36 + 0.01 * fbm(u * 14, v * 14, octaves=2)
    berm = smoothstep(race_w * 0.7, race_w * 1.15, d_loop) * (1.0 - smoothstep(race_w * 1.15, race_w * 1.7, d_loop))
    race_height = race_height + berm * 0.035
    h = base * (1.0 - race_mask) + race_height * race_mask

    # Whoops field — west/southwest of the loop
    whoops_center = gaussian_blob(u, v, 0.28, 0.62, 0.10, 0.14)
    along = (u - 0.18) * 0.6 + (v - 0.55) * 0.8
    whoops = whoops_center * (0.028 * np.sin(along * 55.0) ** 2 + 0.012 * np.sin(along * 28.0))
    h += whoops
    masks["whoops"] = np.maximum(whoops_center, trail_mask(u, v, "whoops"))

    valley_mask = trail_mask(u, v, "valley")
    d_valley = polyline_distance(u, v, TRAILS["valley"]["points"])
    h -= valley_mask * 0.09
    wall = smoothstep(0.02, 0.045, d_valley) * (1.0 - smoothstep(0.045, 0.10, d_valley))
    h += wall * 0.05
    masks["valley"] = valley_mask

    jump_band = trail_mask(u, v, "jumps")
    jump_phase = u * 38.0 + v * 6.0
    tablets = np.clip(np.sin(jump_phase), 0.0, 1.0) ** 1.6
    lips = np.clip(np.sin(jump_phase + 0.8), 0.0, 1.0) ** 3
    h += jump_band * (0.045 * tablets + 0.02 * lips)
    masks["jumps"] = jump_band

    rock_east = gaussian_blob(u, v, 0.88, 0.48, 0.08, 0.16)
    rock_nw = gaussian_blob(u, v, 0.18, 0.22, 0.09, 0.10)
    rock_se = gaussian_blob(u, v, 0.86, 0.78, 0.07, 0.08)
    rock_mask = np.clip(rock_east + rock_nw + rock_se, 0.0, 1.0)
    rock_detail = fbm(u * 28.0, v * 28.0, octaves=5, lac=2.1, gain=0.55)
    rock_ridges = np.abs(fbm(u * 18.0 + 3, v * 18.0 - 2, octaves=4) * 2.0 - 1.0)
    h += rock_mask * (0.07 + 0.08 * rock_detail + 0.05 * rock_ridges)

    rocks_east_m = trail_mask(u, v, "rocks_east")
    rocks_nw_m = trail_mask(u, v, "rocks_nw")
    h -= rock_mask * np.maximum(rocks_east_m, rocks_nw_m) * 0.035
    masks["rocks_east"] = np.maximum(rock_east, rocks_east_m)
    masks["rocks_nw"] = np.maximum(rock_nw, rocks_nw_m)
    masks["rocks"] = rock_mask

    pits = gaussian_blob(u, v, 0.18, 0.82, 0.07, 0.05)
    h = h * (1.0 - pits * 0.85) + 0.33 * pits
    masks["pits"] = pits

    edge = np.minimum.reduce([u, v, 1 - u, 1 - v])
    rim = 1.0 - smoothstep(0.02, 0.12, edge)
    h += rim * (0.08 + 0.04 * fbm(u * 6, v * 6, octaves=3))

    h = np.clip(h, 0.05, 0.95)
    return h.astype(np.float64), masks


def save_heightmap(h: np.ndarray, path: Path) -> None:
    data = (h * 65535.0).astype(np.uint16)
    Image.fromarray(data).save(path)


def save_preview(h: np.ndarray, path: Path) -> None:
    data = (h * 255.0).astype(np.uint8)
    Image.fromarray(data, mode="L").save(path)


def _desert_base(h: np.ndarray) -> np.ndarray:
    shade = (h - h.min()) / (h.max() - h.min() + 1e-9)
    rgb = np.zeros((SIZE, SIZE, 3), dtype=np.float64)
    rgb[..., 0] = 0.42 + 0.38 * shade
    rgb[..., 1] = 0.30 + 0.26 * shade
    rgb[..., 2] = 0.15 + 0.12 * shade
    return rgb


def _draw_trail_strokes(draw: ImageDraw.ImageDraw, size: int, outline: bool = True) -> None:
    """Draw each trail as a solid colored stroke on a PIL image."""
    for trail in TRAILS.values():
        pts = [(int(x * (size - 1)), int(y * (size - 1))) for x, y in trail["points"]]
        # Stroke width scales with trail design width
        width = max(4, int(trail["width"] * size * 0.85))
        if outline:
            draw.line(pts, fill=(20, 16, 12), width=width + 6, joint="curve")
        draw.line(pts, fill=trail["color"], width=width, joint="curve")
        # End caps so short trails read clearly
        r = max(3, width // 2)
        for x, y in (pts[0], pts[-1]):
            if outline:
                draw.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=(20, 16, 12))
            draw.ellipse([x - r, y - r, x + r, y + r], fill=trail["color"])


def save_minimap(h: np.ndarray, path: Path) -> None:
    """In-game BeamNG minimap: desert shade + every trail a different color."""
    rgb = _desert_base(h)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(img)
    _draw_trail_strokes(draw, SIZE, outline=True)
    img.save(path)


def save_layout(h: np.ndarray, path: Path) -> None:
    rgb = _desert_base(h)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(img)
    _draw_trail_strokes(draw, SIZE, outline=True)

    preview = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1024, 1220), (18, 16, 14))
    canvas.paste(preview, (0, 0))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    draw.text((24, 1040), "Dust Valley Ultra — colored trail minimap", fill=(245, 235, 210), font=font)
    x, y = 24, 1078
    for trail in TRAILS.values():
        draw.rectangle([x, y, x + 16, y + 16], fill=trail["color"])
        draw.text((x + 24, y - 1), trail["label"], fill=(220, 210, 195), font=font_sm)
        x += 240
        if x > 780:
            x = 24
            y += 28
    canvas.save(path)


def save_trail_colors(path: Path) -> None:
    payload = {
        "description": "Minimap trail color key for Dust Valley Ultra",
        "trails": {
            key: {
                "label": meta["label"],
                "rgb": list(meta["color"]),
                "hex": "#{:02X}{:02X}{:02X}".format(*meta["color"]),
            }
            for key, meta in TRAILS.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    out = Path(__file__).resolve().parent
    level_minimap = out.parent / "levels" / "dust_valley_ultra" / "minimap"
    level_minimap.mkdir(parents=True, exist_ok=True)

    print(f"Generating {SIZE}x{SIZE} heightmap ({WORLD_M:.0f} m, squareSize={SQUARE_SIZE:.2f} m)...")
    h, _masks = build_height()
    save_heightmap(h, out / "heightmap_2048.png")
    save_preview(h, out / "heightmap_preview.png")
    save_layout(h, out / "layout_overview.png")
    save_minimap(h, out / "minimap_terrain.png")
    save_minimap(h, level_minimap / "terrain.png")
    save_trail_colors(out / "trail_colors.json")

    # Keep level preview in sync with the colored trail map
    preview_src = out / "layout_overview.png"
    preview_dst = out.parent / "levels" / "dust_valley_ultra" / "preview.png"
    Image.open(preview_src).convert("RGB").save(preview_dst)

    meta = {
        "resolution": SIZE,
        "worldSizeMeters": WORLD_M,
        "squareSize": SQUARE_SIZE,
        "recommendedMaxHeight": MAX_HEIGHT_M,
        "format": "16-bit PNG grayscale",
        "minimap": "Each trail uses a unique color — see trail_colors.json",
        "importNotes": (
            f"In World Editor: Terrain > Heightmap Import. "
            f"Use squareSize={SQUARE_SIZE} and maxHeight around {MAX_HEIGHT_M}."
        ),
    }
    (out / "heightmap_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print("Wrote:")
    for name in (
        "heightmap_2048.png",
        "heightmap_preview.png",
        "layout_overview.png",
        "minimap_terrain.png",
        "trail_colors.json",
        "heightmap_meta.json",
    ):
        print(" -", out / name)
    print(" -", level_minimap / "terrain.png")


if __name__ == "__main__":
    main()
