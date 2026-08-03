#!/usr/bin/env python3
"""Bake BlenderGIS SRTM .glb mesh into Parker 400 heightmaps.

Centers the mesh on the BeamNG world origin (same center as Blender export),
splats verts onto 4096/8192 grids, fills holes, and uses USGS outside coverage.
"""

from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png16_gray, write_png8  # noqa: E402

IMPORT = ROOT / "import"
LEVEL_IMPORT = ROOT / "levels" / "parker_400" / "import"
GLB = IMPORT / "parker400_terrain.glb"
USGS_HM = IMPORT / "heightmap_4096.png"

WORLD_M = 65536.0
HALF = WORLD_M / 2.0
MAX_H = 1500.0
PAD_M = 25.0
SIZE = 4096
SIZE_HD = 8192


def load_png16_gray(path: Path) -> np.ndarray:
    data = path.read_bytes()
    pos = 8
    w = h = None
    raw = b""
    while pos < len(data):
        ln = int.from_bytes(data[pos : pos + 4], "big")
        tag = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + ln]
        pos += 12 + ln
        if tag == b"IHDR":
            w, h = struct.unpack(">II", chunk[:8])
        elif tag == b"IDAT":
            raw += chunk
        elif tag == b"IEND":
            break
    dec = zlib.decompress(raw)
    arr = np.empty((h, w), dtype=np.uint16)
    stride = 1 + w * 2
    for y in range(h):
        arr[y] = np.frombuffer(dec[y * stride + 1 : (y + 1) * stride], dtype=">u2")
    return arr


def load_glb_srtm_verts(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise SystemExit(f"not a glb: {path}")
    chunk_len = struct.unpack_from("<I", data, 12)[0]
    js = json.loads(data[20 : 20 + chunk_len])
    pad = (4 - (chunk_len % 4)) % 4
    off = 20 + chunk_len + pad
    bin_len = struct.unpack_from("<I", data, off)[0]
    bin_data = data[off + 8 : off + 8 + bin_len]

    pos_idx = None
    for mesh in js["meshes"]:
        for prim in mesh["primitives"]:
            if "POSITION" in prim["attributes"]:
                # prefer named srtm mesh
                if mesh.get("name") == "srtm" or pos_idx is None:
                    pos_idx = prim["attributes"]["POSITION"]
    acc = js["accessors"][pos_idx]
    bv = js["bufferViews"][acc["bufferView"]]
    byte_offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    return np.frombuffer(bin_data, dtype="<f4", count=count * 3, offset=byte_offset).reshape(
        count, 3
    )


def gltf_to_beamng(verts: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Blender Z-up → glTF Y-up: X east, Y height, Z=-north → BeamNG x,y,elev."""
    x = verts[:, 0].astype(np.float64)
    elev = verts[:, 1].astype(np.float64)
    y = (-verts[:, 2]).astype(np.float64)
    return x, y, elev


def splat_elev(size: int, x: np.ndarray, y: np.ndarray, elev: np.ndarray) -> np.ndarray:
    """Average Blender elev into a size×size world grid; NaN where empty."""
    u = (x + HALF) / WORLD_M * (size - 1)
    v = (y + HALF) / WORLD_M * (size - 1)
    ui = np.rint(u).astype(np.int32)
    vi = np.rint(v).astype(np.int32)
    inside = (ui >= 0) & (ui < size) & (vi >= 0) & (vi < size)
    ui, vi, ev = ui[inside], vi[inside], elev[inside].astype(np.float64)
    print(f"  splat {size}: {inside.sum()}/{len(elev)} verts inside world")

    acc = np.zeros((size, size), dtype=np.float64)
    cnt = np.zeros((size, size), dtype=np.float64)
    np.add.at(acc, (vi, ui), ev)
    np.add.at(cnt, (vi, ui), 1.0)
    out = np.full((size, size), np.nan, dtype=np.float32)
    mask = cnt > 0
    out[mask] = (acc[mask] / cnt[mask]).astype(np.float32)
    return out


def fill_small_holes(grid: np.ndarray, passes: int = 8) -> np.ndarray:
    """Fill NaNs that have neighbors (inside Blender footprint)."""
    g = grid.copy()
    for _ in range(passes):
        nan = ~np.isfinite(g)
        if not nan.any():
            break
        padded = np.pad(g, 1, constant_values=np.nan)
        # average of finite 4-neighbors
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]
        stack = np.stack([up, down, left, right], axis=0)
        finite = np.isfinite(stack)
        weight = finite.sum(axis=0)
        # only fill where we have neighbors AND currently nan
        can = nan & (weight > 0)
        if not can.any():
            break
        s = np.nansum(stack, axis=0)
        g[can] = (s[can] / weight[can]).astype(np.float32)
    return g


def elev_to_hm(elev: np.ndarray, zmin: float) -> np.ndarray:
    h = (elev - (zmin - PAD_M)) / MAX_H
    return np.clip(h, 0.01, 0.99).astype(np.float32)


def upsample_nearest(src: np.ndarray, size: int) -> np.ndarray:
    if src.shape[0] == size:
        return src
    yy = np.linspace(0, src.shape[0] - 1, size)
    xx = np.linspace(0, src.shape[1] - 1, size)
    yi = np.clip(np.round(yy).astype(np.int32), 0, src.shape[0] - 1)
    xi = np.clip(np.round(xx).astype(np.int32), 0, src.shape[1] - 1)
    return src[yi][:, xi]


def main() -> None:
    if not GLB.exists():
        raise SystemExit(f"Missing {GLB}")
    verts = load_glb_srtm_verts(GLB)
    x, y, elev = gltf_to_beamng(verts)
    print(
        f"blender verts {len(elev)}  x=[{x.min():.0f},{x.max():.0f}] "
        f"y=[{y.min():.0f},{y.max():.0f}] elev=[{elev.min():.1f},{elev.max():.1f}]"
    )

    usgs_elev = None
    if USGS_HM.exists():
        hm = load_png16_gray(USGS_HM)
        meta_path = IMPORT / "heightmap_meta.json"
        zmin_usgs = 111.5
        if meta_path.exists():
            try:
                zmin_usgs = float(json.loads(meta_path.read_text()).get("elevMinMeters", 111.5))
            except Exception:
                pass
        game_z = hm.astype(np.float32) / 65535.0 * MAX_H
        usgs_elev = game_z + (zmin_usgs - PAD_M)
        print(f"USGS absolute elev ~ {usgs_elev.min():.1f}..{usgs_elev.max():.1f}")

    b4 = fill_small_holes(splat_elev(SIZE, x, y, elev), passes=12)
    b8 = fill_small_holes(splat_elev(SIZE_HD, x, y, elev), passes=10)
    cover4 = float(np.isfinite(b4).mean() * 100)
    cover8 = float(np.isfinite(b8).mean() * 100)
    print(f"blender cover 4096={cover4:.1f}%  8192={cover8:.1f}%")

    if usgs_elev is not None:
        elev4096 = np.where(np.isfinite(b4), b4, usgs_elev).astype(np.float32)
        elev8192 = np.where(np.isfinite(b8), b8, upsample_nearest(usgs_elev, SIZE_HD)).astype(
            np.float32
        )
    else:
        fill = float(np.nanmedian(b4))
        elev4096 = np.where(np.isfinite(b4), b4, fill).astype(np.float32)
        elev8192 = np.where(np.isfinite(b8), b8, fill).astype(np.float32)

    zmin = float(min(elev4096.min(), elev8192.min()))
    zmax = float(max(elev4096.max(), elev8192.max()))
    print(f"combined elev {zmin:.1f}..{zmax:.1f} (relief {zmax - zmin:.1f})")

    h4 = elev_to_hm(elev4096, zmin)
    h8 = elev_to_hm(elev8192, zmin)
    IMPORT.mkdir(parents=True, exist_ok=True)
    LEVEL_IMPORT.mkdir(parents=True, exist_ok=True)
    write_png16_gray(IMPORT / "heightmap_4096.png", (h4 * 65535.0).astype(np.uint16))
    write_png16_gray(LEVEL_IMPORT / "heightmap_4096.png", (h4 * 65535.0).astype(np.uint16))
    write_png16_gray(IMPORT / "heightmap_8192.png", (h8 * 65535.0).astype(np.uint16))
    write_png16_gray(LEVEL_IMPORT / "heightmap_8192.png", (h8 * 65535.0).astype(np.uint16))

    preview = (h4 * 255.0).astype(np.uint8)
    write_png8(IMPORT / "heightmap_preview.png", preview)
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_blender_height_preview.png", preview)

    # coverage mask preview
    mask = (np.isfinite(b4).astype(np.uint8) * 255)
    write_png8(art / "parker400_blender_coverage.png", mask)

    meta = {
        "source": "BlenderGIS SRTM glb (parker400_terrain.glb) + USGS fill outside coverage",
        "glb": "import/parker400_terrain.glb",
        "gridSource": "1050625 verts splat+holefill",
        "resolutionShipped": SIZE,
        "resolutionHD": SIZE_HD,
        "worldSizeMeters": WORLD_M,
        "squareSizeShipped": WORLD_M / SIZE,
        "maxHeight": MAX_H,
        "elevMinMeters": round(zmin, 1),
        "elevMaxMeters": round(zmax, 1),
        "reliefMeters": round(zmax - zmin, 1),
        "blenderCoverPercent4096": round(cover4, 1),
    }
    (IMPORT / "heightmap_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    print("Wrote Blender-baked heightmaps — next: bake_ter.py + bake_level.py")


if __name__ == "__main__":
    main()
