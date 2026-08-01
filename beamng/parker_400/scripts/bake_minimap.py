#!/usr/bin/env python3
"""Bake a clean Parker 400 minimap with an anti-aliased race trail."""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
LEVEL_MINIMAP = ROOT / "levels" / "parker_400" / "minimap"
SAT = ROOT / "levels" / "parker_400" / "art" / "terrains" / "parker400_base_color.jpg"
IMPORT = ROOT / "import"

MINIMAP = 2048  # sharper than old 1024 nearest-neighbor dump
SUPERSAMPLE = 2  # draw at 2× then area-downsample for clean AA
# Widths are in final minimap pixels (scaled up while drawing)
TRAIL_HALF_PX = 2.0
OUTLINE_HALF_PX = 3.2
TRAIL_COLOR = np.array([250, 250, 248], dtype=np.float32)
OUTLINE_COLOR = np.array([28, 22, 14], dtype=np.float32)
TRAIL_EDGE = np.array([200, 160, 70], dtype=np.float32)


def load_jpg_rgb(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    )
    arr = np.frombuffer(raw, dtype=np.uint8)
    n = arr.size // 3
    side = int(math.sqrt(n))
    return arr.reshape(side, side, 3)


def downsample_box(rgb: np.ndarray, out: int) -> np.ndarray:
    """Average-pool to out×out. Fast path when dimensions divide evenly."""
    h, w, _ = rgb.shape
    if h % out == 0 and w % out == 0:
        fy, fx = h // out, w // out
        return (
            rgb.reshape(out, fy, out, fx, 3)
            .mean(axis=(1, 3))
            .astype(np.float32)
        )
    # ffmpeg scale is much faster than nested Python for odd sizes
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{w}x{h}",
            "-i",
            "-",
            "-vf",
            f"scale={out}:{out}:flags=area",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        input=np.ascontiguousarray(rgb).tobytes(),
    )
    return np.frombuffer(raw, dtype=np.uint8).reshape(out, out, 3).astype(np.float32)


def _stamp_distance(aa: np.ndarray, pts: np.ndarray, half_px: float) -> None:
    """Max-blend soft coverage for distance-to-segment into aa mask."""
    h, w = aa.shape
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        pad = half_px + 1.5
        xmin = max(0, int(math.floor(min(x0, x1) - pad)))
        xmax = min(w - 1, int(math.ceil(max(x0, x1) + pad)))
        ymin = max(0, int(math.floor(min(y0, y1) - pad)))
        ymax = min(h - 1, int(math.ceil(max(y0, y1) + pad)))
        if xmin >= xmax or ymin >= ymax:
            continue
        yy, xx = np.mgrid[ymin : ymax + 1, xmin : xmax + 1]
        vx, vy = x1 - x0, y1 - y0
        seg2 = vx * vx + vy * vy
        if seg2 < 1e-6:
            d = np.hypot(xx - x0, yy - y0)
        else:
            t = np.clip(((xx - x0) * vx + (yy - y0) * vy) / seg2, 0.0, 1.0)
            d = np.hypot(xx - (x0 + t * vx), yy - (y0 + t * vy))
        cover = np.clip(half_px + 0.75 - d, 0.0, 1.0)
        aa[ymin : ymax + 1, xmin : xmax + 1] = np.maximum(
            aa[ymin : ymax + 1, xmin : xmax + 1], cover.astype(np.float32)
        )


def draw_aa_polyline(canvas: np.ndarray, uvs: list[list[float]], half_px: float, outline_px: float) -> None:
    """Distance-to-segment AA trail with dark outline. UV: u→x, v=0 south → flip."""
    h, w, _ = canvas.shape
    if len(uvs) < 2:
        return
    pts = np.array(
        [[u * (w - 1), (1.0 - v) * (h - 1)] for u, v in uvs],
        dtype=np.float64,
    )

    outline = np.zeros((h, w), dtype=np.float32)
    core = np.zeros((h, w), dtype=np.float32)
    _stamp_distance(outline, pts, outline_px)
    _stamp_distance(core, pts, half_px)

    # Soft gold under-glow, dark outline, then white core
    glow = np.clip(outline * 0.55, 0, 1)[..., None]
    ink = outline[..., None]
    white = core[..., None]
    canvas[:] = canvas * (1 - glow * 0.4) + TRAIL_EDGE * (glow * 0.4)
    canvas[:] = canvas * (1 - ink * 0.85) + OUTLINE_COLOR * (ink * 0.85)
    canvas[:] = canvas * (1 - white * 0.98) + TRAIL_COLOR * (white * 0.98)


def main() -> None:
    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    uvs = course.get("longCourseUv") or []

    draw_res = MINIMAP * SUPERSAMPLE
    if SAT.exists():
        print(f"Loading sat background from {SAT.name}...")
        sat = load_jpg_rgb(SAT)
        # BeamNG sat bake: row0 = south. Flip to north-up for minimap.
        sat_nu = np.flipud(sat)
        bg = downsample_box(sat_nu, draw_res)
        # Slightly mute so trail pops
        bg = bg * 0.90 + np.array([40, 32, 18], dtype=np.float32) * 0.10
    else:
        print("No sat — flat desert background")
        bg = np.zeros((draw_res, draw_res, 3), dtype=np.float32)
        bg[..., 0] = 120
        bg[..., 1] = 95
        bg[..., 2] = 62

    canvas = bg.astype(np.float32)
    print(f"Drawing AA trail ({len(uvs)} nodes) at {draw_res}px...")
    draw_aa_polyline(
        canvas,
        uvs,
        TRAIL_HALF_PX * SUPERSAMPLE,
        OUTLINE_HALF_PX * SUPERSAMPLE,
    )
    if SUPERSAMPLE > 1:
        canvas = downsample_box(np.clip(canvas, 0, 255).astype(np.uint8), MINIMAP)

    out = np.clip(canvas, 0, 255).astype(np.uint8)
    LEVEL_MINIMAP.mkdir(parents=True, exist_ok=True)
    dest = LEVEL_MINIMAP / "terrain.png"
    write_png8(dest, out)
    write_png8(IMPORT / "minimap_2048.png", out)
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_minimap.png", out)
    print(f"wrote {dest} ({dest.stat().st_size / 1e6:.2f} MB, {MINIMAP}x{MINIMAP})")


if __name__ == "__main__":
    main()
