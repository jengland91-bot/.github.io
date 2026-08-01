#!/usr/bin/env python3
"""Bake BeamNG theTerrain.ter (v9) from the shipped 16-bit heightmap PNG.

Without this file, Freeroam loads a black/empty map because TerrainBlock
points at a missing .ter. Also paints the full layer map with desert_base
and writes companion theTerrain.terrain.json.
"""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LEVEL = ROOT / "levels" / "parker_400"
HEIGHTMAP = LEVEL / "import" / "heightmap_4096.png"
TER_PATH = LEVEL / "theTerrain.ter"
TER_JSON = LEVEL / "theTerrain.terrain.json"
MAX_HEIGHT = 1500.0
MATERIALS = ["desert_base", "course_pack", "rock_slope"]


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


def write_ter(path: Path, height: np.ndarray, layer: np.ndarray, materials: list[str]) -> None:
    if height.ndim != 2 or height.shape[0] != height.shape[1]:
        raise ValueError("heightmap must be square")
    if height.shape != layer.shape:
        raise ValueError("layer map shape mismatch")
    size = height.shape[0]
    # BeamNG .ter v9: LE heightmap + layer map; material names = u8 length + UTF-8
    with path.open("wb") as f:
        f.write(struct.pack("<B", 9))
        f.write(struct.pack("<I", size))
        f.write(np.ascontiguousarray(height, dtype="<u2").tobytes())
        f.write(np.ascontiguousarray(layer, dtype=np.uint8).tobytes())
        f.write(struct.pack("<I", len(materials)))
        for name in materials:
            b = name.encode("utf-8")
            if len(b) > 255:
                raise ValueError(f"material name too long: {name}")
            f.write(struct.pack("<B", len(b)))
            f.write(b)


def main() -> None:
    if not HEIGHTMAP.exists():
        raise SystemExit(f"Missing heightmap: {HEIGHTMAP}")

    height = read_png16_gray(HEIGHTMAP)
    size = height.shape[0]
    # Paint entire terrain with desert_base (satellite albedo) so first load isn't black
    layer = np.zeros((size, size), dtype=np.uint8)

    write_ter(TER_PATH, height, layer, MATERIALS)

    meta = {
        "version": 9,
        "datafile": "/levels/parker_400/theTerrain.ter",
        "heightmapImage": "/levels/parker_400/import/heightmap_4096.png",
        "size": size,
        "binaryFormat": (
            "version(char), size(unsigned int), "
            "heightMap(heightMapSize * heightMapItemSize), "
            "layerMap(layerMapSize * layerMapItemSize), "
            "layerTextureMap(layerMapSize * layerMapItemSize), materialNames"
        ),
        "heightMapSize": size * size,
        "heightMapItemSize": 2,
        "layerMapSize": size * size,
        "layerMapItemSize": 1,
        "materials": MATERIALS,
        "maxHeight": MAX_HEIGHT,
        "squareSize": 16.0,
        "note": "Pre-baked for BeamNG 0.39 so Freeroam is not an empty black map.",
    }
    TER_JSON.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    expected = 1 + 4 + size * size * 2 + size * size + 4 + sum(1 + len(m.encode()) for m in MATERIALS)
    actual = TER_PATH.stat().st_size
    print(
        json.dumps(
            {
                "wrote": str(TER_PATH),
                "size": size,
                "bytes": actual,
                "expectedBytes": expected,
                "heightMin": int(height.min()),
                "heightMax": int(height.max()),
                "materials": MATERIALS,
            },
            indent=2,
        )
    )
    if actual != expected:
        raise SystemExit(f"size mismatch: {actual} != {expected}")


if __name__ == "__main__":
    main()
