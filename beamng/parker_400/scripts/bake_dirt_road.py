#!/usr/bin/env python3
"""Bake a rutted off-road dirt DecalRoad texture (diffuse/normal/spec).

Parker desert two-track: pale silt shoulders, darker packed ruts, washboard
chatter, and sparse gravel — tuned to sit on the wash-silt terrain paint.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

ROAD = ROOT / "levels" / "parker_400" / "art" / "road"
SIZE = 1024


def fbm(h: int, w: int, octaves: int = 5, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        gh = max(2, h >> (octaves - o))
        gw = max(2, w >> (octaves - o))
        grid = rng.random((gh + 1, gw + 1), dtype=np.float32)
        ys = np.linspace(0, gh - 1e-6, h)
        xs = np.linspace(0, gw - 1e-6, w)
        y0 = np.floor(ys).astype(np.int32)
        x0 = np.floor(xs).astype(np.int32)
        fy = (ys - y0).astype(np.float32)[:, None]
        fx = (xs - x0).astype(np.float32)[None, :]
        y1 = np.minimum(y0 + 1, gh)
        x1 = np.minimum(x0 + 1, gw)
        g00 = grid[y0[:, None], x0[None, :]]
        g10 = grid[y1[:, None], x0[None, :]]
        g01 = grid[y0[:, None], x1[None, :]]
        g11 = grid[y1[:, None], x1[None, :]]
        tile = (
            g00 * (1 - fy) * (1 - fx)
            + g10 * fy * (1 - fx)
            + g01 * (1 - fy) * fx
            + g11 * fy * fx
        )
        out += tile * amp
        total += amp
        amp *= 0.5
    return out / total


def height_to_normal(height: np.ndarray, strength: float = 6.2) -> np.ndarray:
    dy, dx = np.gradient(height.astype(np.float32))
    nx = -dx * strength
    ny = -dy * strength
    nz = np.ones_like(height, dtype=np.float32)
    nlen = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nlen, ny / nlen, nz / nlen
    rgb = np.stack(
        [(nx * 0.5 + 0.5) * 255.0, (ny * 0.5 + 0.5) * 255.0, (nz * 0.5 + 0.5) * 255.0],
        axis=-1,
    )
    return np.clip(rgb, 0, 255).astype(np.uint8)


def main() -> None:
    ROAD.mkdir(parents=True, exist_ok=True)
    h = w = SIZE
    x = np.linspace(0.0, 1.0, w, dtype=np.float32)
    y = np.linspace(0.0, 1.0, h, dtype=np.float32)
    xs, ys = np.meshgrid(x, y)

    n = fbm(h, w, 6, seed=42)
    grain = fbm(h, w, 8, seed=99)
    fine = fbm(h, w, 9, seed=17)

    # Soft feather into silt shoulder (wider fade = less hard road edge)
    edge = np.minimum(xs, 1.0 - xs) * 2.0
    alpha = np.clip((edge - 0.015) / 0.22, 0.0, 1.0)
    alpha = np.clip(alpha * (0.82 + 0.18 * grain), 0.0, 1.0)

    def rut(cx: float, width: float, depth: float) -> np.ndarray:
        d = np.abs(xs - cx) / width
        return (depth * np.exp(-0.5 * (d**2) * 7.5)).astype(np.float32)

    # Dual tire tracks + faint center pack + outer berms
    ruts = (
        rut(0.30, 0.075, 1.15)
        + rut(0.70, 0.075, 1.12)
        + rut(0.50, 0.11, 0.22)
    )
    washboard = (
        0.42 * np.sin(ys * 92.0 + n * 10.0) * (ruts * 0.85 + 0.15)
    ).astype(np.float32)
    berm = (
        0.32 * np.exp(-0.5 * ((np.abs(xs - 0.5) - 0.44) / 0.055) ** 2)
    ).astype(np.float32)
    # Lateral sand drifts across tracks
    drifts = (
        0.12 * np.sin(xs * 18.0 + ys * 3.0 + grain * 4.0) * (1.0 - ruts * 0.5)
    ).astype(np.float32)

    height = np.clip(
        0.52
        + 0.11 * n
        + 0.07 * grain
        + 0.03 * fine
        - 0.28 * ruts
        + 0.07 * washboard
        + berm
        + drifts,
        0,
        1,
    )

    # Parker wash palette — pale silt vs packed brown two-track
    base = np.array([168.0, 138.0, 98.0], dtype=np.float32)
    dust = np.array([204.0, 178.0, 138.0], dtype=np.float32)
    rut_col = np.array([118.0, 92.0, 64.0], dtype=np.float32)
    wet = np.array([98.0, 78.0, 56.0], dtype=np.float32)

    t = np.clip(0.35 + 0.45 * n + 0.25 * grain, 0.0, 1.0)
    rgb = np.empty((h, w, 3), dtype=np.float32)
    for c in range(3):
        rgb[..., c] = base[c] * (1.0 - t) + dust[c] * t
        rgb[..., c] = rgb[..., c] * (1.0 - ruts * 0.62) + rut_col[c] * (ruts * 0.62)
        # Slightly darker packed bottoms in deepest ruts
        deep = np.clip(ruts - 0.55, 0, 1)
        rgb[..., c] = rgb[..., c] * (1.0 - deep * 0.35) + wet[c] * (deep * 0.35)

    rng = np.random.default_rng(7)
    # Gravel / pebble flecks
    pebble_mask = (rng.random((h, w)) > 0.988) & (alpha > 0.3)
    rgb[pebble_mask, 0] = 168.0
    rgb[pebble_mask, 1] = 152.0
    rgb[pebble_mask, 2] = 128.0
    # Pale silt flecks on shoulders
    silt_mask = (rng.random((h, w)) > 0.985) & (alpha > 0.2) & (ruts < 0.25)
    rgb[silt_mask, 0] = 220.0
    rgb[silt_mask, 1] = 205.0
    rgb[silt_mask, 2] = 178.0

    streak = 0.90 + 0.10 * np.sin(ys * 48.0 + xs * 2.5 + fine * 6.0)
    for c in range(3):
        rgb[..., c] *= streak

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    rgba[..., 3] = (alpha * 255.0).astype(np.uint8)

    normal = height_to_normal(height, strength=6.4)
    spec = np.clip(0.14 + 0.10 * (1.0 - ruts) + 0.06 * grain - 0.04 * fine, 0.0, 1.0)
    spec8 = (spec * 255.0).astype(np.uint8)

    write_png8(ROAD / "p400_dirt_d.png", rgba)
    write_png8(ROAD / "p400_dirt_n.png", normal)
    write_png8(ROAD / "p400_dirt_s.png", spec8)

    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_dirt_road_preview.png", rgba[..., :3].copy())
    print(f"wrote off-road dirt textures to {ROAD}")


if __name__ == "__main__":
    main()
