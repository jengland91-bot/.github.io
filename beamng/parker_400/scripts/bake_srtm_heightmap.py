#!/usr/bin/env python3
"""Bake real SRTM elevation under the 2026 Parker 400 footprint.

Downloads AWS Skadi SRTM 1-arcsec tiles covering the course bbox, samples them
into a BeamNG 16-bit heightmap at 1:1 geographic scale.

Tiles: N33W115, N33W114, N34W115, N34W114
Outputs:
  - import/heightmap_8192.png
  - import/heightmap_preview.png
  - import/heightmap_meta.json
  - levels/parker_400/import/ (copies)
  - levels/parker_400/minimap/terrain.png
"""

from __future__ import annotations

import gzip
import json
import math
import shutil
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8, write_png16_gray  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
ELEV = ROOT / "source" / "reference" / "elevation"
IMPORT = ROOT / "import"
LEVEL = ROOT / "levels" / "parker_400"
LEVEL_IMPORT = LEVEL / "import"
LEVEL_MINIMAP = LEVEL / "minimap"

WORLD_M = 65536.0
SIZE = 8192  # power of two; squareSize = 8 m
MAX_HEIGHT_M = 1500.0  # Full 65 km tile mosaic relief can exceed 1200 m
PAD_M = 25.0

# AWS Open Data Skadi SRTM 1-arcsec
SKADI = "https://s3.amazonaws.com/elevation-tiles-prod/skadi"
TILES = [
    ("N33", "W115"),
    ("N33", "W114"),
    ("N34", "W115"),
    ("N34", "W114"),
]


def ensure_tile(ns: str, ew: str) -> Path:
    ELEV.mkdir(parents=True, exist_ok=True)
    name = f"{ns}{ew}.hgt"
    path = ELEV / name
    if path.exists() and path.stat().st_size > 1_000_000:
        return path
    url = f"{SKADI}/{ns}/{name}.gz"
    gz_path = ELEV / f"{name}.gz"
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, gz_path)
    with gzip.open(gz_path, "rb") as f_in, open(path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_path.unlink(missing_ok=True)
    print(f"  wrote {path} ({path.stat().st_size} bytes)")
    return path


def load_hgt(path: Path) -> np.ndarray:
    data = np.fromfile(path, dtype=">i2")
    n = int(math.sqrt(data.size))
    return data.reshape(n, n).astype(np.float32)


def tile_origin(ns: str, ew: str) -> tuple[float, float]:
    """Return (lat_north, lon_west) corner for Skadi tile naming."""
    lat0 = float(ns[1:]) + (0.0 if ns[0] == "N" else -float(ns[1:]))
    # N33 → south edge 33, north edge 34; Skadi row0 is north edge
    lat_north = float(ns[1:]) + 1.0 if ns[0] == "N" else -(float(ns[1:]))
    lon_west = -float(ew[1:]) if ew[0] == "W" else float(ew[1:])
    return lat_north, lon_west


def sample_mosaic(
    tiles: dict[tuple[str, str], np.ndarray], lat: np.ndarray, lon: np.ndarray
) -> np.ndarray:
    """Bilinear sample across Parker SRTM mosaic. Void → nan."""
    out = np.full(lat.shape, np.nan, dtype=np.float32)
    # For N33W114: lat in [33,34], lon in [-114,-113]
    for (ns, ew), hgt in tiles.items():
        lat_north, lon_west = tile_origin(ns, ew)
        # tile covers lat [lat_north-1, lat_north], lon [lon_west, lon_west+1]
        lat_south = lat_north - 1.0
        lon_east = lon_west + 1.0
        mask = (lat >= lat_south) & (lat <= lat_north) & (lon >= lon_west) & (lon <= lon_east)
        if not np.any(mask):
            continue
        n = hgt.shape[0]
        row_f = (lat_north - lat[mask]) * 3600.0
        col_f = (lon[mask] - lon_west) * 3600.0
        row_f = np.clip(row_f, 0, n - 1.001)
        col_f = np.clip(col_f, 0, n - 1.001)
        r0 = np.floor(row_f).astype(np.int32)
        c0 = np.floor(col_f).astype(np.int32)
        r1 = np.minimum(r0 + 1, n - 1)
        c1 = np.minimum(c0 + 1, n - 1)
        dr = row_f - r0
        dc = col_f - c0

        def get(r: np.ndarray, c: np.ndarray) -> np.ndarray:
            v = hgt[r, c]
            return np.where(v <= -32000, np.nan, v)

        v00 = get(r0, c0)
        v10 = get(r1, c0)
        v01 = get(r0, c1)
        v11 = get(r1, c1)
        v0 = v00 * (1 - dr) + v10 * dr
        v1 = v01 * (1 - dr) + v11 * dr
        vals = v0 * (1 - dc) + v1 * dc
        out[mask] = vals.astype(np.float32)
    return out


def uv_to_latlon(u: np.ndarray, v: np.ndarray, t: dict) -> tuple[np.ndarray, np.ndarray]:
    X = u * WORLD_M
    Y = v * WORLD_M
    xm = (X - WORLD_M / 2.0) / t["scale"] + t["cx"]
    ym = (Y - WORLD_M / 2.0) / t["scale"] + t["cy"]
    m_per_deg_lat = 111320.0
    lat = t["minLat"] + ym / m_per_deg_lat
    m_per_deg_lon = 111320.0 * np.cos(np.radians(lat))
    lon = t["minLon"] + xm / np.maximum(m_per_deg_lon, 1.0)
    return lat.astype(np.float64), lon.astype(np.float64)


def main() -> None:
    course_path = P400 / "p400_map_course.json"
    if not course_path.exists():
        raise SystemExit("Run convert_p400_to_map.py first")
    course = json.loads(course_path.read_text(encoding="utf-8"))
    t = {
        "scale": course["transform"]["scale"],
        "cx": course["transform"]["cx"],
        "cy": course["transform"]["cy"],
        "minLat": course["transform"]["minLat"],
        "minLon": course["transform"]["minLon"],
    }

    tiles: dict[tuple[str, str], np.ndarray] = {}
    for ns, ew in TILES:
        path = ensure_tile(ns, ew)
        tiles[(ns, ew)] = load_hgt(path)
        print(f"Loaded {ns}{ew} shape={tiles[(ns, ew)].shape}")

    print(f"Sampling {SIZE}x{SIZE} elevation grid ...")
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    u = xs / (SIZE - 1)
    v = ys / (SIZE - 1)
    # Process in row blocks to limit peak memory
    elev = np.empty((SIZE, SIZE), dtype=np.float32)
    block = 512
    for y0 in range(0, SIZE, block):
        y1 = min(SIZE, y0 + block)
        lat, lon = uv_to_latlon(u[y0:y1], v[y0:y1], t)
        elev[y0:y1] = sample_mosaic(tiles, lat, lon)
        print(f"  rows {y0}..{y1}")

    if np.isnan(elev).any():
        fill = float(np.nanmedian(elev))
        n_nan = int(np.isnan(elev).sum())
        print(f"Filling {n_nan} void samples with median {fill:.1f}")
        elev = np.where(np.isnan(elev), fill, elev)

    zmin = float(np.min(elev))
    zmax = float(np.max(elev))
    relief = zmax - zmin
    print(f"SRTM elev: {zmin:.1f} .. {zmax:.1f} m (relief {relief:.1f} m)")

    # Normalize into BeamNG heightmap using fixed maxHeight
    h = (elev - (zmin - PAD_M)) / MAX_HEIGHT_M
    h = np.clip(h, 0.01, 0.99).astype(np.float32)

    # Subtle corridor polish so the race line reads on the minimap without rewriting DEM
    course_uv = np.array(course["longCourseUv"], dtype=np.float64)
    step = max(1, len(course_uv) // 400)
    sparse = course_uv[::step]
    dist = np.full((SIZE, SIZE), 1e9, dtype=np.float32)
    for y0 in range(0, SIZE, block):
        y1 = min(SIZE, y0 + block)
        uu = u[y0:y1]
        vv = v[y0:y1]
        dblock = np.full(uu.shape, 1e9, dtype=np.float32)
        for p in sparse:
            dblock = np.minimum(dblock, np.hypot(uu - p[0], vv - p[1]).astype(np.float32))
        dist[y0:y1] = dblock
    corridor = np.clip(1.0 - (dist / 0.008), 0, 1)
    h = np.clip(h + corridor * 0.003, 0.01, 0.99)

    IMPORT.mkdir(parents=True, exist_ok=True)
    LEVEL_IMPORT.mkdir(parents=True, exist_ok=True)
    LEVEL_MINIMAP.mkdir(parents=True, exist_ok=True)
    ELEV.mkdir(parents=True, exist_ok=True)

    data16 = (h * 65535.0).astype(np.uint16)
    write_png16_gray(IMPORT / "heightmap_8192.png", data16)
    write_png16_gray(LEVEL_IMPORT / "heightmap_8192.png", data16)

    preview8 = (h * 255.0).astype(np.uint8)
    write_png8(IMPORT / "heightmap_preview.png", preview8)

    # Color minimap (desert shade + gold course)
    shade = (h - h.min()) / (h.max() - h.min() + 1e-9)
    rgb = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    rgb[..., 0] = 0.38 + 0.42 * shade
    rgb[..., 1] = 0.28 + 0.28 * shade
    rgb[..., 2] = 0.14 + 0.12 * shade
    # draw course in UV space (downsample-friendly: paint near corridor)
    gold = np.array([0.95, 0.78, 0.28], dtype=np.float32)
    mask = corridor > 0.15
    rgb[mask] = rgb[mask] * (1 - corridor[mask, None] * 0.85) + gold * (corridor[mask, None] * 0.85)
    color = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    # Store full-res preview + 1024 minimap
    write_png8(IMPORT / "heightmap_color.png", color)
    # nearest-neighbor downsample for minimap
    mm = color[::8, ::8]  # 1024
    write_png8(LEVEL_MINIMAP / "terrain.png", mm)
    write_png8(IMPORT / "minimap_1024.png", mm)
    # artifact copy
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_srtm_elevation.png", mm)

    meta = {
        "source": "SRTM 1-arcsec Skadi mosaic N33/N34 W114/W115 under 2026 Parker 400 CTUTV",
        "resolution": SIZE,
        "worldSizeMeters": WORLD_M,
        "squareSize": WORLD_M / SIZE,
        "recommendedMaxHeight": MAX_HEIGHT_M,
        "elevMinMeters": round(zmin, 1),
        "elevMaxMeters": round(zmax, 1),
        "reliefMeters": round(relief, 1),
        "geographicScale": course["geographicScale"],
        "courseMiles": course["courseMiles"],
        "tiles": [f"{ns}{ew}" for ns, ew in TILES],
        "importNotes": (
            f"World Editor Heightmap Import: squareSize={WORLD_M/SIZE}, maxHeight={MAX_HEIGHT_M}, "
            f"position=[-{WORLD_M/2:.0f}, -{WORLD_M/2:.0f}, 0]. Real Parker elevation is baked in."
        ),
    }
    (IMPORT / "heightmap_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (LEVEL_IMPORT / "heightmap_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (ELEV / "elevation_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("Wrote heightmap_8192.png with REAL Parker 400 elevation (1:1)")


if __name__ == "__main__":
    main()
