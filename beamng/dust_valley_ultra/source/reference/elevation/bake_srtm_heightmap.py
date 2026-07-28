#!/usr/bin/env python3
"""Bake real SRTM elevation under the CA300 footprint into heightmap_4096.png.

Downloads N34W118 SRTM 1-arcsec if needed, maps it through the same UV
transform as convert_ca300_to_map.py, and writes a 16-bit BeamNG heightmap
plus preview/meta.

Real footprint relief is ~700–800 m, so recommended maxHeight is ~900 m.
"""

from __future__ import annotations

import gzip
import json
import math
import re
import shutil
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

WORLD_M = 16384.0
SIZE = 4096
MARGIN = 0.04
MAX_HEIGHT_M = 900.0  # covers ~777 m real relief with headroom
HERE = Path(__file__).resolve().parent
CA300_DIR = HERE.parent / "ca300"
OUT_DIR = HERE.parents[1]  # source/
LEVEL_MINIMAP = HERE.parents[2] / "levels" / "dust_valley_ultra" / "minimap"
SRTM_URL = "https://s3.amazonaws.com/elevation-tiles-prod/skadi/N34/N34W118.hgt.gz"
SRTM_PATH = HERE / "N34W118.hgt"


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def ensure_srtm() -> Path:
    if SRTM_PATH.exists() and SRTM_PATH.stat().st_size > 1_000_000:
        return SRTM_PATH
    HERE.mkdir(parents=True, exist_ok=True)
    gz_path = HERE / "N34W118.hgt.gz"
    print(f"Downloading SRTM {SRTM_URL} ...")
    urllib.request.urlretrieve(SRTM_URL, gz_path)
    with gzip.open(gz_path, "rb") as f_in, open(SRTM_PATH, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_path.unlink(missing_ok=True)
    return SRTM_PATH


def load_hgt(path: Path) -> np.ndarray:
    data = np.fromfile(path, dtype=">i2")
    n = int(math.sqrt(data.size))
    return data.reshape(n, n).astype(np.float32)


def sample_srtm(hgt: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Bilinear sample SRTM N34W118 (1-arcsec). Void (-32768) → nan."""
    n = hgt.shape[0]
    # row 0 = 35N, col 0 = 118W
    row_f = (35.0 - lat) * 3600.0
    col_f = (lon - (-118.0)) * 3600.0
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
    return v0 * (1 - dc) + v1 * dc


def course_geo_bounds() -> tuple[float, float, float, float, list[tuple[float, float]]]:
    gpx = (CA300_DIR / "2024_CA300_Course_Race_Ready.gpx").read_text(encoding="utf-8")
    pts: list[tuple[float, float]] = []
    for m in re.finditer(r"<trkpt\s+([^>/]+)/?>", gpx):
        attrs = m.group(1)
        lat = float(re.search(r'lat="([^"]+)"', attrs).group(1))
        lon = float(re.search(r'lon="([^"]+)"', attrs).group(1))
        pts.append((lat, lon))
    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    return min(lats), max(lats), min(lons), max(lons), pts


def build_transform(min_lat: float, max_lat: float, min_lon: float, max_lon: float, pts: list[tuple[float, float]]):
    def to_m(lat: float, lon: float) -> tuple[float, float]:
        x = haversine(lat, min_lon, lat, lon)
        y = haversine(min_lat, lon, lat, lon)
        return x, y

    meters = [to_m(lat, lon) for lat, lon in pts]
    minx = min(x for x, _ in meters)
    maxx = max(x for x, _ in meters)
    miny = min(y for _, y in meters)
    maxy = max(y for _, y in meters)
    span = max(maxx - minx, maxy - miny)
    usable = WORLD_M * (1 - 2 * MARGIN)
    scale = usable / span
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    return {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon,
        "cx": cx,
        "cy": cy,
        "scale": scale,
        "span": span,
    }


def uv_to_latlon(u: np.ndarray, v: np.ndarray, t: dict) -> tuple[np.ndarray, np.ndarray]:
    """Inverse of convert_ca300_to_map UV (approx constant meters/degree)."""
    X = u * WORLD_M
    Y = v * WORLD_M
    xm = (X - WORLD_M / 2) / t["scale"] + t["cx"]
    ym = (Y - WORLD_M / 2) / t["scale"] + t["cy"]
    # meters → degrees
    m_per_deg_lat = 111320.0
    lat = t["min_lat"] + ym / m_per_deg_lat
    m_per_deg_lon = 111320.0 * np.cos(np.radians(lat))
    lon = t["min_lon"] + xm / np.maximum(m_per_deg_lon, 1.0)
    return lat.astype(np.float64), lon.astype(np.float64)


def main() -> None:
    ensure_srtm()
    hgt = load_hgt(SRTM_PATH)
    min_lat, max_lat, min_lon, max_lon, pts = course_geo_bounds()
    t = build_transform(min_lat, max_lat, min_lon, max_lon, pts)
    print(
        f"Geo bounds lat {min_lat:.4f}..{max_lat:.4f} lon {min_lon:.4f}..{max_lon:.4f} "
        f"scale={t['scale']:.3f}"
    )

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    u = xs / (SIZE - 1)
    v = ys / (SIZE - 1)
    lat, lon = uv_to_latlon(u, v, t)
    elev = sample_srtm(hgt, lat, lon)

    # Fill any voids with local median of valid neighbors (simple)
    if np.isnan(elev).any():
        fill = np.nanmedian(elev)
        elev = np.where(np.isnan(elev), fill, elev)

    zmin = float(np.min(elev))
    zmax = float(np.max(elev))
    relief = zmax - zmin
    print(f"SRTM elev in map: {zmin:.1f} .. {zmax:.1f} m (relief {relief:.1f} m)")

    # Normalize into BeamNG heightmap 0..1 using MAX_HEIGHT_M
    # Keep a small floor pad so oceans/voids aren't zero-clipped oddly
    pad = 20.0
    h = (elev - (zmin - pad)) / MAX_HEIGHT_M
    h = np.clip(h, 0.02, 0.98).astype(np.float32)

    # Very light race-corridor polish: slight smoothing toward local mean on course
    course_json = json.loads((CA300_DIR / "ca300_map_course.json").read_text(encoding="utf-8"))
    course_uv = np.array(course_json["longCourseUv"], dtype=np.float64)
    # Distance-to-course approx via coarse downsample for polish mask
    # (full polyline_distance at 4096 is heavy — use sparse points)
    step = max(1, len(course_uv) // 200)
    sparse = course_uv[::step]
    # chunked min distance
    dist = np.full((SIZE, SIZE), 1e9, dtype=np.float32)
    block = 512
    for y0 in range(0, SIZE, block):
        y1 = min(SIZE, y0 + block)
        vv = v[y0:y1]
        uu = u[y0:y1]
        dblock = np.full(uu.shape, 1e9, dtype=np.float32)
        for p in sparse:
            dblock = np.minimum(dblock, np.hypot(uu - p[0], vv - p[1]).astype(np.float32))
        dist[y0:y1] = dblock

    corridor = np.clip(1.0 - (dist / 0.015), 0, 1)
    # tiny berm hint without erasing real elevation
    h = h + corridor * 0.004

    # Danger accents from CA300 (subtle on top of real DEM)
    dangers_path = CA300_DIR / "ca300_map_dangers.json"
    if dangers_path.exists():
        dangers = json.loads(dangers_path.read_text(encoding="utf-8")).get("markers", [])
        yy = np.arange(SIZE)[:, None]
        xx = np.arange(SIZE)[None, :]
        for marker in dangers:
            cu, cv = marker["uv"]
            name = marker.get("name", "")
            severity = marker.get("severity", "danger")
            cx = cu * (SIZE - 1)
            cy = cv * (SIZE - 1)
            rad = 18 if severity == "extreme" else 12
            blob = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * rad * rad)))
            if "Rock" in name or "Boulder" in name:
                h += blob * 0.006
            elif "Wash" in name:
                h -= blob * 0.005
            elif "G Out" in name or "Drop" in name:
                h -= blob * 0.006
            elif "Face" in name or "Ledge" in name:
                h += blob * 0.005
        h = np.clip(h, 0.02, 0.98)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LEVEL_MINIMAP.mkdir(parents=True, exist_ok=True)

    data16 = (h * 65535.0).astype(np.uint16)
    Image.fromarray(data16).save(OUT_DIR / "heightmap_4096.png")
    preview8 = (h * 255.0).astype(np.uint8)
    Image.fromarray(preview8, mode="L").save(OUT_DIR / "heightmap_preview.png")

    # Quick shaded color preview for artifacts
    shade = (h - h.min()) / (h.max() - h.min() + 1e-9)
    rgb = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    rgb[..., 0] = 0.35 + 0.45 * shade
    rgb[..., 1] = 0.28 + 0.30 * shade
    rgb[..., 2] = 0.16 + 0.14 * shade
    color = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), mode="RGB")
    color.resize((1024, 1024), Image.Resampling.LANCZOS).save(HERE / "srtm_preview.png")
    color.resize((1024, 1024), Image.Resampling.LANCZOS).save("/opt/cursor/artifacts/ca300_srtm_elevation.png")

    meta = {
        "source": "SRTM 1-arcsec N34W118 under 2024 CA300 footprint",
        "resolution": SIZE,
        "worldSizeMeters": WORLD_M,
        "squareSize": WORLD_M / SIZE,
        "recommendedMaxHeight": MAX_HEIGHT_M,
        "elevMinMeters": round(zmin, 1),
        "elevMaxMeters": round(zmax, 1),
        "reliefMeters": round(relief, 1),
        "geographicScale": round(t["scale"], 4),
        "importNotes": (
            f"World Editor Heightmap Import: squareSize={WORLD_M/SIZE}, maxHeight={MAX_HEIGHT_M}. "
            "Real CA300 elevation is baked in."
        ),
    }
    (OUT_DIR / "heightmap_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (HERE / "elevation_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("Wrote heightmap_4096.png with REAL CA300 elevation")


if __name__ == "__main__":
    main()
