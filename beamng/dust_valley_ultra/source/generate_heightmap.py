#!/usr/bin/env python3
"""Generate Dust Valley Ultra heightmap, colored minimap, and layout overview.

CA300-focused desert park:
  - World ~16.4 km across (squareSize 4 m @ 4096)
  - Course from 2024 CA300 Race Ready GPX (~74 mi, nearly 1:1 fit)
  - Pit row from the same GPX
  - Danger markers from CA300 (g-outs, rocks, washouts, etc.)

Outputs:
  - heightmap_4096.png      (16-bit grayscale for World Editor)
  - heightmap_preview.png   (8-bit shaded preview)
  - layout_overview.png     (design map + legend)
  - minimap_terrain.png     (in-game minimap with each trail a unique color)
  - trail_colors.json       (color key for docs / UI)
  - course_lengths.json     (measured polyline lengths)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 4096  # resolution (power of two)
WORLD_M = 16384.0  # ~10.2 miles across — fits CA300 footprint nearly 1:1
SQUARE_SIZE = WORLD_M / SIZE  # 4 m per sample
MAX_HEIGHT_M = 280.0  # more vertical room on the bigger park
ROOT = Path(__file__).resolve().parent
CA300_COURSE_JSON = ROOT / "reference" / "ca300" / "ca300_map_course.json"
CA300_DANGERS_JSON = ROOT / "reference" / "ca300" / "ca300_map_dangers.json"


def _loop(n: int, r0: float, amp3: float, amp5: float, sx: float, sy: float) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = r0 + amp3 * math.sin(3 * t) + amp5 * math.cos(5 * t)
        x = 0.5 + r * math.cos(t) * sx
        y = 0.5 + r * math.sin(t) * sy
        pts.append((round(x, 4), round(y, 4)))
    pts.append(pts[0])
    return pts


def _load_ca300_course() -> tuple[list[tuple[float, float]], list[tuple[float, float]], float]:
    """Return (course_uv, pit_row_uv, course_miles). Falls back to synthetic loop."""
    if CA300_COURSE_JSON.exists():
        data = json.loads(CA300_COURSE_JSON.read_text(encoding="utf-8"))
        course_uv = [(float(u), float(v)) for u, v in data["longCourseUv"]]
        pit_uv = [(float(u), float(v)) for u, v in data.get("pitRowUv", [])]
        return course_uv, pit_uv, float(data.get("courseMiles", 0))
    return _loop(40, 0.30, 0.035, 0.02, 1.08, 0.95), [], 20.5


def _load_ca300_dangers() -> list[dict]:
    if not CA300_DANGERS_JSON.exists():
        return []
    data = json.loads(CA300_DANGERS_JSON.read_text(encoding="utf-8"))
    return list(data.get("markers", []))


COURSE, PIT_ROW, CA300_MILES = _load_ca300_course()
CA300_DANGERS = _load_ca300_dangers()

# Minimap / terrain ribbons — CA300 only (no short course).
TRAILS: dict[str, dict] = {
    "course": {
        "label": f"CA300 course (~{CA300_MILES:.0f} mi)" if CA300_MILES else "CA300 course",
        "color": (242, 199, 71),  # gold
        "width": 0.012,
        "points": COURSE,
    },
    "pit_row": {
        "label": "Pit row",
        "color": (50, 200, 110),  # green
        "width": 0.010,
        "points": PIT_ROW if PIT_ROW else [(0.34, 0.84), (0.36, 0.83), (0.38, 0.83)],
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
    total = np.zeros_like(x, dtype=np.float32)
    norm = 0.0
    for _ in range(octaves):
        total += np.float32(amp) * value_noise(x * freq, y * freq).astype(np.float32)
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
    best = np.full(px.shape, np.float32(1e9), dtype=np.float32)
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dx = np.float32(x1 - x0)
        dy = np.float32(y1 - y0)
        len2 = dx * dx + dy * dy + np.float32(1e-12)
        t = np.clip(((px - x0) * dx + (py - y0) * dy) / len2, 0.0, 1.0)
        qx = x0 + t * dx
        qy = y0 + t * dy
        dist = np.hypot(px - qx, py - qy).astype(np.float32)
        best = np.minimum(best, dist)
    return best


def polyline_length_m(points: list[tuple[float, float]], world_m: float = WORLD_M) -> float:
    total = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        total += math.hypot(x1 - x0, y1 - y0) * world_m
    return total


def trail_mask(u: np.ndarray, v: np.ndarray, key: str) -> np.ndarray:
    trail = TRAILS[key]
    dist = polyline_distance(u, v, trail["points"])
    w = trail["width"]
    return 1.0 - smoothstep(w * 0.45, w * 1.25, dist)


def build_height() -> np.ndarray:
    ys, xs = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    u = xs / np.float32(SIZE - 1)
    v = ys / np.float32(SIZE - 1)

    base = 0.34 + 0.10 * fbm(u * 3.2, v * 3.2, octaves=4)
    base += 0.045 * fbm(u * 8.0 + 20, v * 8.0 - 7, octaves=3)
    base += 0.02 * np.sin(u * math.pi * 2.0) * np.cos(v * math.pi * 1.5)

    # CA300 race corridor
    d_course = polyline_distance(u, v, COURSE)
    course_w = TRAILS["course"]["width"]
    course_mask = trail_mask(u, v, "course")
    race_height = 0.36 + 0.01 * fbm(u * 12, v * 12, octaves=2)
    berm = smoothstep(course_w * 0.7, course_w * 1.15, d_course) * (
        1.0 - smoothstep(course_w * 1.15, course_w * 1.8, d_course)
    )
    race_height = race_height + berm * 0.025
    h = base * (1.0 - course_mask) + race_height * course_mask

    # Pit row flattened pad
    if TRAILS["pit_row"]["points"] and len(TRAILS["pit_row"]["points"]) >= 2:
        pit_mask = trail_mask(u, v, "pit_row")
        h = h * (1.0 - pit_mask * 0.7) + 0.34 * (pit_mask * 0.7)

    # CA300 danger-inspired terrain hits (g-outs, rocks, washouts)
    for marker in CA300_DANGERS:
        cu, cv = marker["uv"]
        name = marker.get("name", "")
        severity = marker.get("severity", "danger")
        sx = 0.012 if severity == "extreme" else 0.009
        blob = gaussian_blob(u, v, cu, cv, sx, sx)
        if "Rock" in name or "Boulder" in name:
            h += blob * (0.035 if severity == "extreme" else 0.022)
        elif "Wash" in name:
            h -= blob * 0.025
        elif "G Out" in name or "G Puts" in name or "Drop" in name:
            h -= blob * 0.03
            lip = gaussian_blob(u, v, cu, cv, sx * 1.6, sx * 1.6) - blob
            h += np.clip(lip, 0, None) * 0.02
        elif "Face" in name or "Ledge" in name:
            h += blob * 0.028
        else:
            h += blob * (0.012 * fbm(u * 30, v * 30, octaves=2))

    # Mild whoops flavor along the race line
    along = d_course * 80.0
    whoops = (1.0 - smoothstep(0.0, course_w * 1.1, d_course)) * (0.012 * np.sin(along) ** 2)
    h += whoops

    # Soft desert rim — freeroam desert remains around the course
    edge = np.minimum.reduce([u, v, 1 - u, 1 - v])
    rim = 1.0 - smoothstep(0.015, 0.09, edge)
    h += rim * (0.07 + 0.035 * fbm(u * 5, v * 5, octaves=3))

    return np.clip(h, 0.05, 0.95).astype(np.float32)


def save_heightmap(h: np.ndarray, path: Path) -> None:
    data = (h * 65535.0).astype(np.uint16)
    Image.fromarray(data).save(path)


def save_preview(h: np.ndarray, path: Path) -> None:
    data = (h * 255.0).astype(np.uint8)
    Image.fromarray(data, mode="L").save(path)


def _desert_base(h: np.ndarray) -> np.ndarray:
    shade = (h - h.min()) / (h.max() - h.min() + 1e-9)
    rgb = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    rgb[..., 0] = 0.42 + 0.38 * shade
    rgb[..., 1] = 0.30 + 0.26 * shade
    rgb[..., 2] = 0.15 + 0.12 * shade
    return rgb


def _draw_trail_strokes(draw: ImageDraw.ImageDraw, size: int, outline: bool = True) -> None:
    order = ["course", "pit_row"]
    for key in order:
        trail = TRAILS[key]
        if len(trail["points"]) < 2:
            continue
        pts = [(int(x * (size - 1)), int(y * (size - 1))) for x, y in trail["points"]]
        width = max(2, int(trail["width"] * size * 0.9))
        if key == "course":
            width = max(2, int(size * 0.0035))
        if outline:
            draw.line(pts, fill=(20, 16, 12), width=width + 4, joint="curve")
        draw.line(pts, fill=trail["color"], width=width, joint="curve")

    # Danger markers from CA300 (same UV space as trail strokes)
    for marker in CA300_DANGERS:
        u, v = marker["uv"]
        x = int(u * (size - 1))
        y = int(v * (size - 1))
        extreme = marker.get("severity") == "extreme"
        col = (230, 55, 70) if extreme else (242, 115, 38)
        r = 4 if extreme else 3
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)


def save_minimap(h: np.ndarray, path: Path, out_size: int = 2048) -> None:
    rgb = _desert_base(h)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), mode="RGB")
    if out_size != SIZE:
        img = img.resize((out_size, out_size), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    _draw_trail_strokes(draw, out_size, outline=True)
    img.save(path)


def save_layout(h: np.ndarray, path: Path) -> None:
    tmp = Path(path).with_name("_tmp_minimap_layout.png")
    save_minimap(h, tmp, out_size=1024)
    preview = Image.open(tmp).convert("RGB")
    canvas = Image.new("RGB", (1024, 1220), (18, 16, 14))
    canvas.paste(preview, (0, 0))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    course_mi = polyline_length_m(COURSE) / 1609.34
    draw.text(
        (24, 1040),
        f"Dust Valley Ultra — CA300 focus  |  course ~{course_mi:.1f} mi",
        fill=(245, 235, 210),
        font=font,
    )
    x, y = 24, 1074
    legend = list(TRAILS.items()) + [
        ("danger", {"label": "CA300 dangers", "color": (242, 115, 38)}),
        ("extreme", {"label": "Extreme dangers", "color": (230, 55, 70)}),
    ]
    for _key, trail in legend:
        draw.rectangle([x, y, x + 12, y + 12], fill=trail["color"])
        draw.text((x + 18, y - 1), trail["label"], fill=(220, 210, 195), font=font_sm)
        x += 240
        if x > 780:
            x = 24
            y += 24
    canvas.save(path)
    tmp.unlink(missing_ok=True)


def save_trail_colors(path: Path) -> None:
    payload = {
        "description": "Minimap color key — CA300-focused Dust Valley Ultra",
        "worldSizeMeters": WORLD_M,
        "ca300Miles": CA300_MILES,
        "dangerCount": len(CA300_DANGERS),
        "trails": {
            key: {
                "label": meta["label"],
                "rgb": list(meta["color"]),
                "hex": "#{:02X}{:02X}{:02X}".format(*meta["color"]),
                "lengthMeters": round(polyline_length_m(meta["points"]), 1) if len(meta["points"]) > 1 else 0,
                "lengthMiles": round(polyline_length_m(meta["points"]) / 1609.34, 2) if len(meta["points"]) > 1 else 0,
            }
            for key, meta in TRAILS.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def save_course_lengths(path: Path) -> None:
    payload = {
        "worldSizeMeters": WORLD_M,
        "worldSizeMiles": round(WORLD_M / 1609.34, 2),
        "squareSize": SQUARE_SIZE,
        "resolution": SIZE,
        "source": "2024 CA300 C_T_U Course - Race Ready GPX" if CA300_COURSE_JSON.exists() else "synthetic",
        "focus": "california_300_only",
        "courseMiles": round(polyline_length_m(COURSE) / 1609.34, 2),
        "courseMeters": round(polyline_length_m(COURSE), 1),
        "pitRowMiles": round(polyline_length_m(PIT_ROW) / 1609.34, 2) if len(PIT_ROW) > 1 else 0,
        "ca300SourceMiles": CA300_MILES,
        "dangerMarkers": len(CA300_DANGERS),
        "note": "Map is focused on the CA300 race path only (short course removed).",
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    out = Path(__file__).resolve().parent
    level_minimap = out.parent / "levels" / "dust_valley_ultra" / "minimap"
    level_minimap.mkdir(parents=True, exist_ok=True)

    # Remove old smaller heightmap if present
    old = out / "heightmap_2048.png"
    if old.exists():
        old.unlink()

    print(
        f"Generating {SIZE}x{SIZE} heightmap "
        f"({WORLD_M:.0f} m / {WORLD_M/1609.34:.1f} mi across, squareSize={SQUARE_SIZE:.2f} m)..."
    )
    print(
        f"  CA300 course ~{polyline_length_m(COURSE)/1609.34:.1f} mi | "
        f"{len(CA300_DANGERS)} danger markers"
    )
    h = build_height()
    save_heightmap(h, out / "heightmap_4096.png")
    save_preview(h, out / "heightmap_preview.png")
    save_layout(h, out / "layout_overview.png")
    # Full-res minimap for the game; keep file reasonable via 2048 export
    save_minimap(h, out / "minimap_terrain.png", out_size=2048)
    save_minimap(h, level_minimap / "terrain.png", out_size=2048)
    save_trail_colors(out / "trail_colors.json")
    save_course_lengths(out / "course_lengths.json")

    preview_src = out / "layout_overview.png"
    preview_dst = out.parent / "levels" / "dust_valley_ultra" / "preview.png"
    Image.open(preview_src).convert("RGB").save(preview_dst)

    meta = {
        "resolution": SIZE,
        "worldSizeMeters": WORLD_M,
        "worldSizeMiles": round(WORLD_M / 1609.34, 2),
        "squareSize": SQUARE_SIZE,
        "recommendedMaxHeight": MAX_HEIGHT_M,
        "format": "16-bit PNG grayscale",
        "focus": "california_300_only",
        "courseMiles": round(polyline_length_m(COURSE) / 1609.34, 2),
        "ca300SourceMiles": CA300_MILES,
        "dangerMarkers": len(CA300_DANGERS),
        "minimap": "CA300 course + pit row + danger markers — see trail_colors.json",
        "importNotes": (
            f"In World Editor: Terrain > Heightmap Import. "
            f"Use squareSize={SQUARE_SIZE} and maxHeight around {MAX_HEIGHT_M}."
        ),
    }
    (out / "heightmap_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print("Wrote:")
    for name in (
        "heightmap_4096.png",
        "heightmap_preview.png",
        "layout_overview.png",
        "minimap_terrain.png",
        "trail_colors.json",
        "course_lengths.json",
        "heightmap_meta.json",
    ):
        print(" -", out / name)
    print(" -", level_minimap / "terrain.png")


if __name__ == "__main__":
    main()
