#!/usr/bin/env python3
"""Bake Esri World Imagery satellite base for the exact Parker 400 map frame.

Same idea as MapNG's satellite export, but locked to our 65536 m / 1:1 GPX frame
so the DecalRoad lines up. No MapNG UI required.

Outputs:
  - import/parker400_base_color.png          (4096² RGB)
  - levels/parker_400/art/terrains/parker400_base_color.png
  - import/parker400_base_color_preview.png  (1024² with course overlay)
  - /opt/cursor/artifacts/parker400_satellite.png
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
IMPORT = ROOT / "import"
LEVEL_ART = ROOT / "levels" / "parker_400" / "art" / "terrains"

WORLD_M = 65536.0
OUT = 4096  # matches shipped heightmap
ZOOM = 13  # ~10–16 m/px over Parker — good for 65 km square
USER_AGENT = "Parker400BeamNGBaker/1.0 (personal mod; Esri World Imagery tiles)"


def latlon_to_tile_xy(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2.0**z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y


def uv_to_latlon(u: np.ndarray, v: np.ndarray, t: dict) -> tuple[np.ndarray, np.ndarray]:
    X = u * WORLD_M
    Y = v * WORLD_M
    xm = (X - WORLD_M / 2.0) / t["scale"] + t["cx"]
    ym = (Y - WORLD_M / 2.0) / t["scale"] + t["cy"]
    lat = t["minLat"] + ym / 111320.0
    lon = t["minLon"] + xm / (111320.0 * np.cos(np.radians(lat)))
    return lat, lon


def download_tile(z: int, x: int, y: int, cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / f"{z}_{x}_{y}.jpg"
    if out.exists() and out.stat().st_size > 1000:
        return out
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        out.write_bytes(resp.read())
    return out


def jpg_to_rgb(path: Path) -> np.ndarray:
    """Decode JPEG via ffmpeg → RGB uint8 (H, W, 3)."""
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
    )
    # Esri tiles are 256x256
    arr = np.frombuffer(raw, dtype=np.uint8)
    n = arr.size // 3
    side = int(math.sqrt(n))
    return arr.reshape(side, side, 3)


def main() -> None:
    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    t = {
        "scale": course["transform"]["scale"],
        "cx": course["transform"]["cx"],
        "cy": course["transform"]["cy"],
        "minLat": course["transform"]["minLat"],
        "minLon": course["transform"]["minLon"],
    }

    # Corners → tile range
    corners = [(0, 0), (1, 0), (0, 1), (1, 1)]
    xs, ys = [], []
    for u, v in corners:
        lat, lon = uv_to_latlon(np.array([u]), np.array([v]), t)
        tx, ty = latlon_to_tile_xy(float(lat[0]), float(lon[0]), ZOOM)
        xs.append(tx)
        ys.append(ty)
    x0, x1 = int(math.floor(min(xs))), int(math.floor(max(xs)))
    y0, y1 = int(math.floor(min(ys))), int(math.floor(max(ys)))
    print(f"Zoom {ZOOM} tiles x={x0}..{x1} y={y0}..{y1} ({(x1-x0+1)*(y1-y0+1)} tiles)")

    cache = ROOT / "source" / "reference" / "satellite_cache"
    tiles: dict[tuple[int, int], np.ndarray] = {}
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            path = download_tile(ZOOM, x, y, cache)
            tiles[(x, y)] = jpg_to_rgb(path)
            print(f"  tile {x},{y} ok")

    # Mosaic in tile-pixel space
    tw = tiles[(x0, y0)].shape[1]
    th = tiles[(x0, y0)].shape[0]
    mosaic = np.zeros(((y1 - y0 + 1) * th, (x1 - x0 + 1) * tw, 3), dtype=np.uint8)
    for (x, y), img in tiles.items():
        px = (x - x0) * tw
        py = (y - y0) * th
        mosaic[py : py + th, px : px + tw] = img

    # Sample mosaic at each output UV (row0 = south v=0 to match heightmap bake)
    print(f"Resampling to {OUT}x{OUT} ...")
    out = np.zeros((OUT, OUT, 3), dtype=np.uint8)
    block = 256
    for y0b in range(0, OUT, block):
        y1b = min(OUT, y0b + block)
        vv = np.linspace(y0b / (OUT - 1), (y1b - 1) / (OUT - 1), y1b - y0b)[:, None]
        uu = np.linspace(0, 1, OUT)[None, :]
        uu = np.broadcast_to(uu, (y1b - y0b, OUT))
        vv = np.broadcast_to(vv, (y1b - y0b, OUT))
        lat, lon = uv_to_latlon(uu, vv, t)
        # fractional tile coords
        n = 2.0**ZOOM
        fx = (lon + 180.0) / 360.0 * n
        lat_r = np.radians(lat)
        fy = (1.0 - np.log(np.tan(lat_r) + 1.0 / np.cos(lat_r)) / math.pi) / 2.0 * n
        # mosaic pixel
        px = (fx - x0) * tw
        py = (fy - y0) * th
        px = np.clip(px, 0, mosaic.shape[1] - 1.001)
        py = np.clip(py, 0, mosaic.shape[0] - 1.001)
        ix = px.astype(np.int32)
        iy = py.astype(np.int32)
        out[y0b:y1b] = mosaic[iy, ix]
        print(f"  rows {y0b}..{y1b}")

    IMPORT.mkdir(parents=True, exist_ok=True)
    LEVEL_ART.mkdir(parents=True, exist_ok=True)
    write_png8(IMPORT / "parker400_base_color.png", out)
    write_png8(LEVEL_ART / "parker400_base_color.png", out)

    # Preview with course overlay (flip V for north-up display)
    preview = out[::4, ::4].copy()  # 1024
    ph, pw = preview.shape[:2]
    for u, v in course["longCourseUv"][::2]:
        x = int(round(u * (pw - 1)))
        y = int(round((1.0 - v) * (ph - 1)))  # north-up
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                yy, xx = y + dy, x + dx
                if 0 <= yy < ph and 0 <= xx < pw:
                    preview[yy, xx] = (242, 199, 71)
    # Our out array has v increasing upward in index (south at top). Flip for preview north-up:
    # Actually course overlay used 1-v assuming north-up image. Fix: build north-up preview.
    north_up = np.flipud(out[::4, ::4].copy())
    for u, v in course["longCourseUv"][::2]:
        x = int(round(u * (pw - 1)))
        y = int(round((1.0 - v) * (ph - 1)))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                yy, xx = y + dy, x + dx
                if 0 <= yy < ph and 0 <= xx < pw:
                    north_up[yy, xx] = (242, 199, 71)
    write_png8(IMPORT / "parker400_base_color_preview.png", north_up)
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_satellite.png", north_up)

    meta = {
        "source": "Esri World Imagery tiles (same family MapNG uses for satellite)",
        "zoom": ZOOM,
        "resolution": OUT,
        "worldSizeMeters": WORLD_M,
        "geographicScale": course["geographicScale"],
        "tileRange": {"x0": x0, "x1": x1, "y0": y0, "y1": y1},
        "center": {"lat": 34.086139, "lon": -113.897239},
        "note": "Locked to Parker 400 GPX 1:1 frame — race line should align.",
    }
    (IMPORT / "parker400_base_color_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    print("Wrote parker400_base_color.png for exact Parker 400 frame")


if __name__ == "__main__":
    main()
