#!/usr/bin/env python3
"""Bake pale wash-silt textures for the course shoulder (outside DecalRoad).

Uses compact tiled maps (1024/512) so the mod stays under GitHub's 100 MiB limit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

ART = ROOT / "levels" / "parker_400" / "art" / "terrains"

# Parker wash silt — pale cream / tan (matches satellite desert shoulders)
SILT_LIGHT = np.array([232, 218, 190], dtype=np.float32)
SILT_MID = np.array([214, 198, 168], dtype=np.float32)
SILT_DARK = np.array([188, 174, 148], dtype=np.float32)


def fbm(h: int, w: int, octaves: int = 4, seed: int = 7) -> np.ndarray:
    """Soft value-noise FBM (fewer octaves → better PNG compression + silt look)."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        gh = max(2, h >> (octaves - o))
        gw = max(2, w >> (octaves - o))
        grid = rng.random((gh + 1, gw + 1), dtype=np.float32)
        # bilinear upsample
        ys = np.linspace(0, gh - 1e-6, h)
        xs = np.linspace(0, gw - 1e-6, w)
        y0 = np.floor(ys).astype(np.int32)
        x0 = np.floor(xs).astype(np.int32)
        fy = (ys - y0).astype(np.float32)
        fx = (xs - x0).astype(np.float32)
        y1 = np.minimum(y0 + 1, gh)
        x1 = np.minimum(x0 + 1, gw)
        g00 = grid[y0[:, None], x0[None, :]]
        g10 = grid[y1[:, None], x0[None, :]]
        g01 = grid[y0[:, None], x1[None, :]]
        g11 = grid[y1[:, None], x1[None, :]]
        fy2 = fy[:, None]
        fx2 = fx[None, :]
        tile = g00 * (1 - fy2) * (1 - fx2) + g10 * fy2 * (1 - fx2) + g01 * (1 - fy2) * fx2 + g11 * fy2 * fx2
        out += tile * amp
        total += amp
        amp *= 0.5
    return out / total


def make_albedo(size: int, seed: int) -> np.ndarray:
    n = fbm(size, size, octaves=4, seed=seed)
    grain = fbm(size, size, octaves=5, seed=seed + 99)
    t = np.clip(0.65 * n + 0.35 * grain, 0, 1)[..., None]
    yy = np.linspace(0, 1, size, dtype=np.float32)[:, None]
    streak = 0.5 + 0.5 * np.sin(yy * 14.0 + n * 2.5)
    t = np.clip(t * 0.88 + streak[..., None] * 0.12, 0, 1)
    rgb = SILT_DARK * (1 - t) + SILT_MID * t
    rgb = rgb * 0.62 + SILT_LIGHT * (0.38 * (1.0 - t))
    rgb[..., 0] *= 0.97
    rgb[..., 2] *= 1.04
    return np.clip(rgb, 0, 255).astype(np.uint8)


def make_height(size: int, seed: int) -> np.ndarray:
    h = fbm(size, size, octaves=4, seed=seed)
    return np.clip(0.48 + 0.10 * h, 0, 1).astype(np.float32)


def height_to_normal(height: np.ndarray, strength: float = 0.8) -> np.ndarray:
    dy, dx = np.gradient(height.astype(np.float32))
    nx = -dx * strength
    ny = -dy * strength
    nz = np.ones_like(height)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx * inv, ny * inv, nz * inv
    rgb = np.stack(
        [(nx * 0.5 + 0.5) * 255, (ny * 0.5 + 0.5) * 255, (nz * 0.5 + 0.5) * 255],
        axis=-1,
    )
    return np.clip(rgb, 0, 255).astype(np.uint8)


def gray_rgb(v: np.ndarray) -> np.ndarray:
    g = (np.clip(v, 0, 1) * 255).astype(np.uint8)
    return np.stack([g, g, g], axis=-1)


def write_maps(stem: str, size: int, seed: int, normal_strength: float) -> None:
    albedo = make_albedo(size, seed)
    height = make_height(size, seed + 1)
    normal = height_to_normal(height, strength=normal_strength)
    rough = gray_rgb(0.74 + 0.10 * fbm(size, size, 3, seed + 2))
    ao = gray_rgb(0.90 + 0.08 * fbm(size, size, 3, seed + 3))
    h_rgb = gray_rgb(height)
    write_png8(ART / f"{stem}_b.png", albedo)
    write_png8(ART / f"{stem}_nm.png", normal)
    write_png8(ART / f"{stem}_r.png", rough)
    write_png8(ART / f"{stem}_ao.png", ao)
    write_png8(ART / f"{stem}_h.png", h_rgb)
    print(f"  wrote {stem}_* ({size}px)")


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    print("Baking wash-silt course_pack textures…")
    # Compact tiled bases — materials still point at *_4096 names
    size = 1024
    albedo = make_albedo(size, 11)
    height = make_height(size, 12)
    normal = height_to_normal(height, strength=0.75)
    rough = gray_rgb(0.74 + 0.10 * fbm(size, size, 3, 13))
    ao = gray_rgb(0.90 + 0.08 * fbm(size, size, 3, 14))
    h_rgb = gray_rgb(height)
    for name, arr in [
        ("course_pack_base_b_4096.png", albedo),
        ("course_pack_base_nm_4096.png", normal),
        ("course_pack_base_r_4096.png", rough),
        ("course_pack_base_ao_4096.png", ao),
        ("course_pack_base_h_4096.png", h_rgb),
        ("course_pack_base_b.png", albedo),
        ("course_pack_base_nm.png", normal),
        ("course_pack_base_r.png", rough),
        ("course_pack_base_ao.png", ao),
        ("course_pack_base_h.png", h_rgb),
    ]:
        write_png8(ART / name, arr)
    print(f"  wrote course_pack_base_* ({size}px, also as *_4096)")

    write_maps("course_pack_macro", 512, seed=22, normal_strength=1.0)
    write_maps("course_pack_detail", 512, seed=33, normal_strength=1.3)

    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_course_silt_preview.png", make_albedo(512, 11))
    print("Done — pale wash silt shoulder ready")


if __name__ == "__main__":
    main()
