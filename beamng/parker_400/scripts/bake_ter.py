#!/usr/bin/env python3
"""Bake BeamNG theTerrain.ter (v9) from heightmap + paint race corridor."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LEVEL = ROOT / "levels" / "parker_400"
HEIGHTMAP = LEVEL / "import" / "heightmap_4096.png"
COURSE_JSON = ROOT / "source" / "reference" / "p400" / "p400_map_course.json"
TER_PATH = LEVEL / "theTerrain.ter"
TER_JSON = LEVEL / "theTerrain.terrain.json"
MAX_HEIGHT = 1500.0
SQUARE = 16.0
# Only materials with matching 4096 base textures
MATERIALS = ["desert_base", "course_pack"]
# Paint a ~90 m wide packed-dirt ribbon so the course is visible on the ground
COURSE_HALF_WIDTH_M = 60.0


def read_png16_gray(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    i = 8
    w = h = bit = color = None
    idat = b""
    while i < len(data):
        ln = struct.unpack(">I", data[i : i + 4])[0]
        tag = data[i + 4 : i + 8]
        chunk = data[i + 8 : i + 8 + ln]
        i += 12 + ln
        if tag == b"IHDR":
            w, h, bit, color, *_ = struct.unpack(">IIBBBBB", chunk)
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
    if w is None or bit != 16 or color != 0:
        raise ValueError(f"expected 16-bit grayscale PNG, got {w}x{h} bit={bit} color={color}")
    raw = zlib.decompress(idat)
    arr = np.empty((h, w), dtype=np.uint16)
    off = 0
    for y in range(h):
        if raw[off] != 0:
            raise ValueError(f"unsupported PNG filter byte {raw[off]} at row {y}")
        off += 1
        arr[y] = np.frombuffer(raw[off : off + w * 2], dtype=">u2")
        off += w * 2
    return arr


def paint_course_corridor(size: int, uvs: list[list[float]], half_width_m: float) -> np.ndarray:
    """Layer map: 0=desert_base, 1=course_pack along GPX UV polyline."""
    layer = np.zeros((size, size), dtype=np.uint8)
    if not uvs:
        return layer
    radius = max(1, int(round(half_width_m / SQUARE)))
    pts = np.array(uvs, dtype=np.float64)
    # Convert UV to pixel (row0 = south/v=0 — matches heightmap bake)
    xs = np.clip(np.round(pts[:, 0] * (size - 1)).astype(np.int32), 0, size - 1)
    ys = np.clip(np.round(pts[:, 1] * (size - 1)).astype(np.int32), 0, size - 1)
    # Stamp discs along path (dense enough from decimated GPX)
    yy, xx = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    disk = xx * xx + yy * yy <= radius * radius
    for x, y in zip(xs, ys):
        y0, y1 = y - radius, y + radius + 1
        x0, x1 = x - radius, x + radius + 1
        gy0, gy1 = max(0, y0), min(size, y1)
        gx0, gx1 = max(0, x0), min(size, x1)
        dy0, dx0 = gy0 - y0, gx0 - x0
        patch = disk[dy0 : dy0 + (gy1 - gy0), dx0 : dx0 + (gx1 - gx0)]
        layer[gy0:gy1, gx0:gx1][patch] = 1
    return layer


def write_ter(path: Path, height: np.ndarray, layer: np.ndarray, materials: list[str]) -> None:
    size = height.shape[0]
    with path.open("wb") as f:
        f.write(struct.pack("<B", 9))
        f.write(struct.pack("<I", size))
        f.write(np.ascontiguousarray(height, dtype="<u2").tobytes())
        f.write(np.ascontiguousarray(layer, dtype=np.uint8).tobytes())
        f.write(struct.pack("<I", len(materials)))
        for name in materials:
            b = name.encode("utf-8")
            f.write(struct.pack("<B", len(b)))
            f.write(b)


def main() -> None:
    if not HEIGHTMAP.exists():
        raise SystemExit(f"Missing heightmap: {HEIGHTMAP}")
    course = json.loads(COURSE_JSON.read_text(encoding="utf-8"))
    uvs = course.get("longCourseUv") or []

    height = read_png16_gray(HEIGHTMAP)
    size = height.shape[0]
    layer = paint_course_corridor(size, uvs, COURSE_HALF_WIDTH_M)
    course_px = int((layer == 1).sum())

    write_ter(TER_PATH, height, layer, MATERIALS)

    meta = {
        "version": 9,
        "datafile": "/levels/parker_400/theTerrain.ter",
        "heightmapImage": "/levels/parker_400/import/heightmap_4096.png",
        "size": size,
        "heightMapSize": size * size,
        "heightMapItemSize": 2,
        "layerMapSize": size * size,
        "layerMapItemSize": 1,
        "materials": MATERIALS,
        "maxHeight": MAX_HEIGHT,
        "squareSize": SQUARE,
        "courseHalfWidthMeters": COURSE_HALF_WIDTH_M,
        "coursePixels": course_px,
        "note": "desert_base = Parker satellite; course_pack painted on GPX corridor",
    }
    TER_JSON.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(f"wrote {TER_PATH} ({TER_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
