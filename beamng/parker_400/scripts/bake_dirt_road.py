#!/usr/bin/env python3
"""Bake a rutted off-road dirt DecalRoad texture (diffuse/normal/spec)."""

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


def height_to_normal(height: np.ndarray, strength: float = 5.5) -> np.ndarray:
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
    grain = fbm(h, w, 7, seed=99)

    # Soft edge alpha
    edge = np.minimum(xs, 1.0 - xs) * 2.0
    alpha = np.clip((edge - 0.02) / 0.18, 0.0, 1.0)
    alpha = np.clip(alpha * (0.85 + 0.15 * grain), 0.0, 1.0)

    def rut(cx: float, width: float, depth: float) -> np.ndarray:
        d = np.abs(xs - cx) / width
        return (depth * np.exp(-0.5 * (d**2) * 8.0)).astype(np.float32)

    ruts = rut(0.32, 0.07, 1.0) + rut(0.68, 0.07, 1.0)
    chatter = (0.35 * np.sin(ys * 70.0 + n * 8.0) * ruts).astype(np.float32)
    berm = (
        0.25 * np.exp(-0.5 * ((np.abs(xs - 0.5) - 0.42) / 0.06) ** 2)
    ).astype(np.float32)

    height = np.clip(0.55 + 0.12 * n + 0.08 * grain - 0.22 * ruts + 0.05 * chatter + berm, 0, 1)

    base = np.array([148.0, 118.0, 82.0], dtype=np.float32)
    dust = np.array([186.0, 158.0, 118.0], dtype=np.float32)
    rut_col = np.array([112.0, 88.0, 62.0], dtype=np.float32)

    t = np.clip(0.4 + 0.4 * n + 0.2 * grain, 0.0, 1.0)
    rgb = np.empty((h, w, 3), dtype=np.float32)
    for c in range(3):
        rgb[..., c] = base[c] * (1.0 - t) + dust[c] * t
        rgb[..., c] = rgb[..., c] * (1.0 - ruts * 0.55) + rut_col[c] * (ruts * 0.55)

    rng = np.random.default_rng(7)
    pebble_mask = (rng.random((h, w)) > 0.992) & (alpha > 0.35)
    rgb[pebble_mask, 0] = 160.0
    rgb[pebble_mask, 1] = 145.0
    rgb[pebble_mask, 2] = 125.0

    streak = 0.92 + 0.08 * np.sin(ys * 40.0 + xs * 3.0)
    for c in range(3):
        rgb[..., c] *= streak

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    rgba[..., 3] = (alpha * 255.0).astype(np.uint8)

    normal = height_to_normal(height, strength=5.5)
    spec = np.clip(0.18 + 0.08 * (1.0 - ruts) + 0.05 * grain, 0.0, 1.0)
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
