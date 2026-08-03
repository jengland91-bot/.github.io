#!/usr/bin/env python3
"""Bake Parker 400 heightmaps from USGS 3DEP (same US DEM family MapNG uses).

MapNG's 3D preview is this elevation data — not a separate mesh. One MapNG tile
cannot cover the full 65 km Parker loop at 1 m/px; this script pulls USGS 3DEP
for our exact GPX frame and writes BeamNG 16-bit heightmaps.

Outputs:
  - import/heightmap_4096.png  (shipped .ter source, 16 m/px)
  - import/heightmap_8192.png  (optional HD import, 8 m/px)
  - import/heightmap_meta.json
  - copies under levels/parker_400/import/
"""

from __future__ import annotations

import json
import struct
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png16_gray, write_png8  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
IMPORT = ROOT / "import"
LEVEL_IMPORT = ROOT / "levels" / "parker_400" / "import"
CACHE = ROOT / "source" / "reference" / "elevation" / "usgs_3dep"

WORLD_M = 65536.0
MAX_HEIGHT_M = 1500.0
PAD_M = 25.0
USGS_EXPORT = (
    "https://elevation.nationalmap.gov/arcgis/rest/services/"
    "3DEPElevation/ImageServer/exportImage"
)
# USGS exportImage commonly accepts up to 4096; we stitch a 2×2 for HD source.
TILE_PX = 4096


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


def world_latlon_bounds(t: dict) -> tuple[float, float, float, float]:
    us = np.array([0.0, 1.0, 0.0, 1.0, 0.5, 0.5, 0.0, 1.0])
    vs = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.5, 0.5])
    lat, lon = uv_to_latlon(us, vs, t)
    return float(lon.min()), float(lat.min()), float(lon.max()), float(lat.max())


def read_tiff_f32(path: Path) -> tuple[np.ndarray, dict]:
    """Read uncompressed Float32 grayscale GeoTIFF (strips or tiles)."""
    data = path.read_bytes()
    if data[:2] not in (b"II", b"MM"):
        raise ValueError(f"not a TIFF: {path}")
    le = data[:2] == b"II"

    def u16(o: int) -> int:
        return struct.unpack_from("<H" if le else ">H", data, o)[0]

    def u32(o: int) -> int:
        return struct.unpack_from("<I" if le else ">I", data, o)[0]

    ifd = u32(4)
    n = u16(ifd)
    tags: dict[int, tuple[int, int, int]] = {}
    for i in range(n):
        o = ifd + 2 + i * 12
        tags[u16(o)] = (u16(o + 2), u32(o + 4), o + 8)

    def tag_vals(tag: int):
        typ, count, vo = tags[tag]
        size = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 11: 4, 12: 8}[typ]
        nbytes = size * count
        if nbytes <= 4:
            buf = data[vo : vo + nbytes]
        else:
            off = u32(vo)
            buf = data[off : off + nbytes]
        if typ == 3:
            fmt = "H"
        elif typ == 4:
            fmt = "I"
        elif typ == 11:
            fmt = "f"
        elif typ == 12:
            fmt = "d"
        else:
            raise ValueError(f"unsupported TIFF type {typ} for tag {tag}")
        end = "<" if le else ">"
        vals = struct.unpack_from(end + fmt * count, buf)
        return vals[0] if count == 1 else vals

    w = int(tag_vals(256))
    h = int(tag_vals(257))
    bps = int(tag_vals(258))
    comp = int(tag_vals(259))
    fmt = int(tag_vals(339)) if 339 in tags else 1
    if bps != 32 or comp != 1 or fmt != 3:
        raise ValueError(f"need uncompressed Float32 TIFF, got bps={bps} comp={comp} fmt={fmt}")

    arr = np.empty((h, w), dtype=np.float32)
    if 322 in tags and 324 in tags:
        tw = int(tag_vals(322))
        th = int(tag_vals(323))
        offs = tag_vals(324)
        bcs = tag_vals(325)
        if isinstance(offs, int):
            offs, bcs = (offs,), (bcs,)
        tiles_x = (w + tw - 1) // tw
        tiles_y = (h + th - 1) // th
        i = 0
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                off, bc = offs[i], bcs[i]
                i += 1
                tile = np.frombuffer(data[off : off + bc], dtype="<f4" if le else ">f4").reshape(th, tw)
                y0, x0 = ty * th, tx * tw
                y1, x1 = min(h, y0 + th), min(w, x0 + tw)
                arr[y0:y1, x0:x1] = tile[: y1 - y0, : x1 - x0]
    else:
        offs = tag_vals(273)
        bcs = tag_vals(279)
        if isinstance(offs, int):
            offs, bcs = (offs,), (bcs,)
        rows_per = int(tag_vals(278)) if 278 in tags else h
        y = 0
        for off, bc in zip(offs, bcs):
            rh = min(rows_per, h - y)
            strip = np.frombuffer(data[off : off + bc], dtype="<f4" if le else ">f4").reshape(rh, w)
            arr[y : y + rh] = strip
            y += rh

    # GeoTIFF ModelTiepoint + ModelPixelScale when present
    meta = {"width": w, "height": h}
    if 33550 in tags and 33922 in tags:
        sx, sy, _sz = tag_vals(33550)[:3]
        tie = tag_vals(33922)
        # I,J,K, X,Y,Z — usually (0,0,0, west, north, 0)
        meta["west"] = float(tie[3])
        meta["north"] = float(tie[4])
        meta["px_w"] = float(sx)
        meta["px_h"] = float(sy)
    return arr, meta


def download_usgs_tile(
    west: float, south: float, east: float, north: float, size: int, dest: Path
) -> tuple[np.ndarray, dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"  cache hit {dest.name}")
        arr, meta = read_tiff_f32(dest)
        # Prefer extent from sidecar json if present
        side = dest.with_suffix(".json")
        if side.exists():
            meta.update(json.loads(side.read_text(encoding="utf-8")))
        return arr, meta

    params = {
        "bbox": f"{west},{south},{east},{north}",
        "bboxSR": "4326",
        "size": f"{size},{size}",
        "imageSR": "4326",
        "format": "tiff",
        "pixelType": "F32",
        "interpolation": "RSP_BilinearInterpolation",
        "renderingRule": '{"rasterFunction":"None"}',
        "f": "json",
    }
    url = USGS_EXPORT + "?" + urllib.parse.urlencode(params)
    print(f"  requesting USGS {size}² …")
    for attempt in range(4):
        try:
            meta_json = json.loads(urllib.request.urlopen(url, timeout=180).read())
            href = meta_json["href"]
            urllib.request.urlretrieve(href, dest)
            break
        except Exception as e:
            if attempt == 3:
                raise
            wait = 4 * (2**attempt)
            print(f"  retry after {wait}s ({e})")
            time.sleep(wait)

    extent = meta_json["extent"]
    side = {
        "west": extent["xmin"],
        "south": extent["ymin"],
        "east": extent["xmax"],
        "north": extent["ymax"],
        "width": meta_json["width"],
        "height": meta_json["height"],
        "source": "USGS 3DEP Elevation ImageServer",
    }
    dest.with_suffix(".json").write_text(json.dumps(side, indent=2) + "\n", encoding="utf-8")
    arr, tmeta = read_tiff_f32(dest)
    tmeta.update(side)
    print(f"  wrote {dest.name} ({dest.stat().st_size / 1e6:.1f} MB) elev {arr.min():.1f}..{arr.max():.1f}")
    return arr, tmeta


def sample_geotiff(arr: np.ndarray, meta: dict, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Bilinear sample; row0 = north (GeoTIFF)."""
    west, north = meta["west"], meta["north"]
    # pixel size: prefer sidecar east/south
    if "east" in meta and "south" in meta:
        px_w = (meta["east"] - west) / arr.shape[1]
        px_h = (north - meta["south"]) / arr.shape[0]
    else:
        px_w = meta["px_w"]
        px_h = meta["px_h"]
    col_f = (lon - west) / px_w - 0.5
    row_f = (north - lat) / px_h - 0.5
    col_f = np.clip(col_f, 0, arr.shape[1] - 1.001)
    row_f = np.clip(row_f, 0, arr.shape[0] - 1.001)
    c0 = np.floor(col_f).astype(np.int32)
    r0 = np.floor(row_f).astype(np.int32)
    c1 = np.minimum(c0 + 1, arr.shape[1] - 1)
    r1 = np.minimum(r0 + 1, arr.shape[0] - 1)
    dc = (col_f - c0).astype(np.float32)
    dr = (row_f - r0).astype(np.float32)
    v00 = arr[r0, c0]
    v10 = arr[r1, c0]
    v01 = arr[r0, c1]
    v11 = arr[r1, c1]
    return (v00 * (1 - dr) * (1 - dc) + v10 * dr * (1 - dc) + v01 * (1 - dr) * dc + v11 * dr * dc)


class UsgsMosaic:
    """2×2 USGS tiles covering the Parker world bbox."""

    def __init__(self, tiles: list[tuple[np.ndarray, dict]]):
        self.tiles = tiles

    def sample(self, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        out = np.full(lat.shape, np.nan, dtype=np.float32)
        for arr, meta in self.tiles:
            west, east, south, north = meta["west"], meta["east"], meta["south"], meta["north"]
            mask = (lon >= west) & (lon <= east) & (lat >= south) & (lat <= north) & np.isnan(out)
            if not np.any(mask):
                continue
            out[mask] = sample_geotiff(arr, meta, lat[mask], lon[mask])
        # Edge voids: sample from nearest tile center
        if np.isnan(out).any():
            miss = np.isnan(out)
            lat_m, lon_m = lat[miss], lon[miss]
            best = np.full(lat_m.shape, np.inf, dtype=np.float64)
            pick = np.zeros(lat_m.shape, dtype=np.int32)
            for i, (_arr, meta) in enumerate(self.tiles):
                cy = 0.5 * (meta["south"] + meta["north"])
                cx = 0.5 * (meta["west"] + meta["east"])
                d = (lat_m - cy) ** 2 + (lon_m - cx) ** 2
                better = d < best
                best[better] = d[better]
                pick[better] = i
            for i, (arr, meta) in enumerate(self.tiles):
                sel = pick == i
                if not np.any(sel):
                    continue
                # map sel back into miss indices
                idx = np.flatnonzero(miss)
                out_flat = out.ravel()
                out_flat[idx[sel]] = sample_geotiff(arr, meta, lat_m[sel], lon_m[sel])
        return out


def build_mosaic(west: float, south: float, east: float, north: float) -> UsgsMosaic:
    mid_lon = 0.5 * (west + east)
    mid_lat = 0.5 * (south + north)
    # slight overlap so seams don't leave voids
    pad_lon = (east - west) * 0.02
    pad_lat = (north - south) * 0.02
    quads = [
        ("sw", west, south, mid_lon + pad_lon, mid_lat + pad_lat),
        ("se", mid_lon - pad_lon, south, east, mid_lat + pad_lat),
        ("nw", west, mid_lat - pad_lat, mid_lon + pad_lon, north),
        ("ne", mid_lon - pad_lon, mid_lat - pad_lat, east, north),
    ]
    tiles = []
    for name, w, s, e, n in quads:
        dest = CACHE / f"usgs_{name}_{TILE_PX}.tif"
        print(f"Tile {name}: {s:.4f},{w:.4f} → {n:.4f},{e:.4f}")
        tiles.append(download_usgs_tile(w, s, e, n, TILE_PX, dest))
    return UsgsMosaic(tiles)


def elev_to_heightmap(elev: np.ndarray, zmin: float) -> np.ndarray:
    h = (elev - (zmin - PAD_M)) / MAX_HEIGHT_M
    return np.clip(h, 0.01, 0.99).astype(np.float32)


def sample_grid(mosaic: UsgsMosaic, t: dict, size: int) -> np.ndarray:
    print(f"Sampling {size}×{size} BeamNG grid from USGS 3DEP…")
    elev = np.empty((size, size), dtype=np.float32)
    block = 256
    ys, xs = np.mgrid[0:size, 0:size]
    u = xs / (size - 1)
    v = ys / (size - 1)
    for y0 in range(0, size, block):
        y1 = min(size, y0 + block)
        lat, lon = uv_to_latlon(u[y0:y1], v[y0:y1], t)
        elev[y0:y1] = mosaic.sample(lat, lon)
        print(f"  rows {y0}..{y1}")
    if np.isnan(elev).any():
        fill = float(np.nanmedian(elev))
        n = int(np.isnan(elev).sum())
        print(f"Filling {n} voids with median {fill:.1f}")
        elev = np.where(np.isnan(elev), fill, elev)
    return elev


def main() -> None:
    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    t = {
        "scale": course["transform"]["scale"],
        "cx": course["transform"]["cx"],
        "cy": course["transform"]["cy"],
        "minLat": course["transform"]["minLat"],
        "minLon": course["transform"]["minLon"],
    }
    west, south, east, north = world_latlon_bounds(t)
    print(f"World bbox WGS84: {south:.6f},{west:.6f} → {north:.6f},{east:.6f}")

    mosaic = build_mosaic(west, south, east, north)

    elev4096 = sample_grid(mosaic, t, 4096)
    zmin = float(elev4096.min())
    zmax = float(elev4096.max())
    print(f"USGS elev @4096: {zmin:.1f} .. {zmax:.1f} m (relief {zmax - zmin:.1f})")

    elev8192 = sample_grid(mosaic, t, 8192)
    zmin8 = float(elev8192.min())
    zmax8 = float(elev8192.max())
    print(f"USGS elev @8192: {zmin8:.1f} .. {zmax8:.1f} m (relief {zmax8 - zmin8:.1f})")
    zmin = min(zmin, zmin8)
    zmax = max(zmax, zmax8)

    IMPORT.mkdir(parents=True, exist_ok=True)
    LEVEL_IMPORT.mkdir(parents=True, exist_ok=True)

    h4 = elev_to_heightmap(elev4096, zmin)
    h8 = elev_to_heightmap(elev8192, zmin)
    write_png16_gray(IMPORT / "heightmap_4096.png", (h4 * 65535.0).astype(np.uint16))
    write_png16_gray(LEVEL_IMPORT / "heightmap_4096.png", (h4 * 65535.0).astype(np.uint16))
    write_png16_gray(IMPORT / "heightmap_8192.png", (h8 * 65535.0).astype(np.uint16))
    write_png16_gray(LEVEL_IMPORT / "heightmap_8192.png", (h8 * 65535.0).astype(np.uint16))

    preview = (h4 * 255.0).astype(np.uint8)
    write_png8(IMPORT / "heightmap_preview.png", preview)
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_usgs_elevation_preview.png", preview)

    meta = {
        "source": "USGS 3DEP Elevation ImageServer (MapNG US DEM family) under 2026 Parker 400 CTUTV",
        "note": (
            "MapNG 3D preview = this height data. Full loop cannot be one MapNG 1 m tile "
            "(~8 km max). Shipped terrain uses 4096 @ 16 m/px from USGS 3DEP; "
            "import heightmap_8192.png at squareSize=8 for sharper local washes."
        ),
        "resolutionShipped": 4096,
        "resolutionHD": 8192,
        "worldSizeMeters": WORLD_M,
        "squareSizeShipped": WORLD_M / 4096,
        "squareSizeHD": WORLD_M / 8192,
        "recommendedMaxHeight": MAX_HEIGHT_M,
        "elevMinMeters": round(zmin, 1),
        "elevMaxMeters": round(zmax, 1),
        "reliefMeters": round(zmax - zmin, 1),
        "geographicScale": course["geographicScale"],
        "courseMiles": course["courseMiles"],
        "bboxWGS84": {
            "south": south,
            "west": west,
            "north": north,
            "east": east,
        },
        "importNotes": (
            f"Default .ter: squareSize=16, maxHeight={MAX_HEIGHT_M}, pos=[-32768,-32768,0]. "
            f"HD: World Editor import heightmap_8192.png with squareSize=8, maxHeight={MAX_HEIGHT_M}, "
            "same position — then re-save terrain."
        ),
    }
    for p in (IMPORT / "heightmap_meta.json", LEVEL_IMPORT / "heightmap_meta.json"):
        p.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print("Wrote USGS 3DEP heightmaps (4096 shipped + 8192 HD)")


if __name__ == "__main__":
    main()
