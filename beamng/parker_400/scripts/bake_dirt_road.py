#!/usr/bin/env python3
"""Bake a rutted off-road dirt DecalRoad texture (diffuse/normal/spec).

Tuned from desert reference snapshots: pale tan two-track, dark packed tire
ruts, gravel flecks, soft fade into wash silt.
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


def height_to_normal(height: np.ndarray, strength: float = 7.0) -> np.ndarray:
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
    pebble_n = fbm(h, w, 7, seed=201)

    # Soft feather into silt — refs show road blending into gravel shoulder
    edge = np.minimum(xs, 1.0 - xs) * 2.0
    alpha = np.clip((edge - 0.01) / 0.26, 0.0, 1.0)
    alpha = np.clip(alpha * (0.78 + 0.22 * grain), 0.0, 1.0)

    def rut(cx: float, width: float, depth: float) -> np.ndarray:
        d = np.abs(xs - cx) / width
        return (depth * np.exp(-0.5 * (d**2) * 7.2)).astype(np.float32)

    # Dual tire tracks like Ben refs — deep dark grooves, slight center pack
    ruts = (
        rut(0.31, 0.08, 1.25)
        + rut(0.69, 0.08, 1.22)
        + rut(0.50, 0.12, 0.18)
    )
    # Striated tire compression along track (refs show layered groove bottoms)
    tire_striate = (
        0.22 * np.sin(ys * 140.0 + n * 6.0) * np.clip(ruts, 0, 1)
    ).astype(np.float32)
    washboard = (
        0.38 * np.sin(ys * 88.0 + n * 10.0) * (ruts * 0.8 + 0.2)
    ).astype(np.float32)
    berm = (
        0.28 * np.exp(-0.5 * ((np.abs(xs - 0.5) - 0.43) / 0.05) ** 2)
    ).astype(np.float32)
    drifts = (
        0.10 * np.sin(xs * 16.0 + ys * 2.5 + grain * 4.0) * (1.0 - ruts * 0.55)
    ).astype(np.float32)

    height = np.clip(
        0.50
        + 0.10 * n
        + 0.07 * grain
        + 0.04 * fine
        + 0.03 * pebble_n
        - 0.32 * ruts
        - 0.06 * tire_striate
        + 0.06 * washboard
        + berm
        + drifts,
        0,
        1,
    )

    # Snapshot palette: pale tan surface, dark moist rut bottoms, warm dust
    base = np.array([186.0, 152.0, 108.0], dtype=np.float32)
    dust = np.array([214.0, 186.0, 142.0], dtype=np.float32)
    rut_col = np.array([96.0, 74.0, 52.0], dtype=np.float32)
    wet = np.array([58.0, 48.0, 40.0], dtype=np.float32)  # near-black packed ruts

    t = np.clip(0.30 + 0.45 * n + 0.28 * grain, 0.0, 1.0)
    rgb = np.empty((h, w, 3), dtype=np.float32)
    for c in range(3):
        rgb[..., c] = base[c] * (1.0 - t) + dust[c] * t
        rgb[..., c] = rgb[..., c] * (1.0 - ruts * 0.68) + rut_col[c] * (ruts * 0.68)
        deep = np.clip((ruts - 0.45) / 0.55, 0, 1)
        rgb[..., c] = rgb[..., c] * (1.0 - deep * 0.55) + wet[c] * (deep * 0.55)

    rng = np.random.default_rng(7)
    # Dense gravel / pebble litter (refs are rock-strewn)
    pebble_mask = (rng.random((h, w)) > 0.975) & (alpha > 0.25)
    rgb[pebble_mask, 0] = rng.uniform(140, 175, size=pebble_mask.sum())
    rgb[pebble_mask, 1] = rng.uniform(128, 160, size=pebble_mask.sum())
    rgb[pebble_mask, 2] = rng.uniform(108, 138, size=pebble_mask.sum())
    # Larger dark stones
    stone_mask = (rng.random((h, w)) > 0.994) & (alpha > 0.3)
    rgb[stone_mask, 0] = 92.0
    rgb[stone_mask, 1] = 84.0
    rgb[stone_mask, 2] = 72.0
    # Pale silt flecks on shoulders
    silt_mask = (rng.random((h, w)) > 0.982) & (alpha > 0.15) & (ruts < 0.22)
    rgb[silt_mask, 0] = 226.0
    rgb[silt_mask, 1] = 210.0
    rgb[silt_mask, 2] = 178.0

    streak = 0.91 + 0.09 * np.sin(ys * 52.0 + xs * 2.0 + fine * 5.0)
    for c in range(3):
        rgb[..., c] *= streak

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    rgba[..., 3] = (alpha * 255.0).astype(np.uint8)

    normal = height_to_normal(height, strength=7.2)
    spec = np.clip(0.12 + 0.08 * (1.0 - ruts) + 0.05 * grain - 0.03 * fine, 0.0, 1.0)
    # Packed rut bottoms a bit more specular (moist look)
    spec = np.clip(spec + 0.06 * np.clip(ruts - 0.5, 0, 1), 0, 1)
    spec8 = (spec * 255.0).astype(np.uint8)

    write_png8(ROAD / "p400_dirt_d.png", rgba)
    write_png8(ROAD / "p400_dirt_n.png", normal)
    write_png8(ROAD / "p400_dirt_s.png", spec8)

    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_dirt_road_preview.png", rgba[..., :3].copy())
    print(f"wrote Ben-ref dirt textures to {ROAD}")


if __name__ == "__main__":
    main()
