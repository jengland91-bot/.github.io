#!/usr/bin/env python3
"""Bake Colorado River / lake water objects for Parker 400.

Traces the low western valley from the USGS heightmap (Colorado / Moovalya
corridor) so water sits in the real wash instead of on desert hills.

Writes:
  - import/p400_water_objects.json  (consumed by bake_level.py)
  - levels/parker_400/art/water/main.materials.json
"""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IMPORT = ROOT / "import"
LEVEL = ROOT / "levels" / "parker_400"
HEIGHTMAP = IMPORT / "heightmap_4096.png"
WORLD_M = 65536.0
HALF = WORLD_M / 2.0
MAX_H = 1500.0

# Trace params — western low corridor = Colorado / Lake Moovalya in our frame
V_START = 0.48
V_END = 0.97
V_STEP_ROWS = 28
WEST_FRAC = 0.38
MAX_VALLEY_Z = 85.0
RIVER_WIDTH_M = 320.0
RIVER_DEPTH_M = 14.0
WATER_ABOVE_DEM_M = 2.4

# Extra WaterBlock basins (uv u,v, size x/y, depth) — sit in DEM lows
LAKE_UV = [
    ("p400_lake_moovalya", 0.07, 0.72, 2400, 1500, 24),
    ("p400_lake_north", 0.16, 0.85, 1800, 1200, 20),
]


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


def sample_height(img: np.ndarray, u: float, v: float) -> float:
    h, w = img.shape
    x = min(w - 1, max(0, int(round(u * (w - 1)))))
    y = min(h - 1, max(0, int(round(v * (h - 1)))))
    return (float(img[y, x]) / 65535.0) * MAX_H


def uv_to_world(u: float, v: float) -> tuple[float, float]:
    return u * WORLD_M - HALF, v * WORLD_M - HALF


def trace_river(img: np.ndarray) -> list[list[float]]:
    """Follow lowest west-side DEM column from south→north.

    Uses a soft lateral penalty so the path stays continuous but can jump
    when a clearly deeper inland channel appears (Colorado corridor).
    """
    h, w = img.shape
    elev = img.astype(np.float32) / 65535.0 * MAX_H
    west_cols = max(8, int(WEST_FRAC * w))
    r0 = int(V_START * (h - 1))
    r1 = int(V_END * (h - 1))
    nodes: list[list[float]] = []
    prev_c: int | None = None
    # meters-ish per column at this resolution (~16 m)
    lateral_penalty = 0.12  # elev meters per column of lateral move
    for row in range(r0, r1 + 1, V_STEP_ROWS):
        strip = elev[row, :west_cols]
        sm = np.convolve(strip, np.ones(11, dtype=np.float32) / 11.0, mode="same")
        if prev_c is not None:
            cols = np.arange(west_cols, dtype=np.float32)
            cost = sm + lateral_penalty * np.abs(cols - float(prev_c))
            c = int(np.argmin(cost))
            # If a much deeper valley exists, snap to it (don't hug the map edge)
            c_deep = int(np.argmin(sm))
            if sm[c_deep] + 8.0 < sm[c]:
                c = c_deep
        else:
            c = int(np.argmin(sm))
        z = float(elev[row, c])
        if z > MAX_VALLEY_Z:
            continue
        # Skip pure edge artifacts until we lock onto a real inland channel
        if c < 12 and (prev_c is None or prev_c < 20):
            # look for a better inland minimum under threshold
            inland = sm[12:]
            if inland.size and float(inland.min()) < MAX_VALLEY_Z:
                c = 12 + int(np.argmin(inland))
                z = float(elev[row, c])
                if z > MAX_VALLEY_Z:
                    continue
            else:
                continue
        prev_c = c
        u = c / (w - 1)
        v = row / (h - 1)
        # nudge off exact map edge so river renders inside terrain
        u = max(0.006, min(0.994, u))
        x, y = uv_to_world(u, v)
        surface = z + WATER_ABOVE_DEM_M
        nodes.append(
            [
                round(x, 2),
                round(y, 2),
                round(surface, 2),
                RIVER_WIDTH_M,
                RIVER_DEPTH_M,
                0.0,
                0.0,
                1.0,
            ]
        )
    return nodes


def main() -> None:
    if not HEIGHTMAP.exists():
        raise SystemExit(f"Missing {HEIGHTMAP}")
    img = load_png16_gray(HEIGHTMAP)

    river_nodes = trace_river(img)
    objects: list[dict] = []
    if len(river_nodes) >= 2:
        objects.append(
            {
                "class": "River",
                "name": "p400_colorado_river",
                "__parent": "Environment",
                "material": "p400_water",
                "SegmentLength": 48,
                "SubdivideLength": 10,
                "FlowMagnitudePhysics": 1.35,
                "LowLODDistance": 1200,
                "nodes": river_nodes,
            }
        )
        zs = [n[2] for n in river_nodes]
        print(
            f"River nodes: {len(river_nodes)}  "
            f"z={min(zs):.1f}..{max(zs):.1f}  width={RIVER_WIDTH_M}m"
        )

    for name, u, v, sx, sy, sz in LAKE_UV:
        if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
            print(f"  skip lake outside map {name}")
            continue
        x, y = uv_to_world(u, v)
        z = sample_height(img, u, v) + WATER_ABOVE_DEM_M
        objects.append(
            {
                "class": "WaterBlock",
                "name": name,
                "__parent": "Environment",
                "position": [round(x, 2), round(y, 2), round(z, 2)],
                "rotationMatrix": [1, 0, 0, 0, 1, 0, 0, 0, 1],
                "scale": [sx, sy, sz],
                "material": "p400_water",
                "gridElementSize": 20,
            }
        )
        print(f"Lake {name} @ ({x:.0f},{y:.0f},{z:.1f}) scale={sx}x{sy}")

    IMPORT.mkdir(parents=True, exist_ok=True)
    (IMPORT / "p400_water_objects.json").write_text(
        json.dumps({"objects": objects}, indent=2) + "\n", encoding="utf-8"
    )

    water_art = LEVEL / "art" / "water"
    water_art.mkdir(parents=True, exist_ok=True)
    mats = {
        "p400_water": {
            "name": "p400_water",
            "mapTo": "unmapped_mat",
            "class": "Material",
            "persistentId": "p400water00000001",
            "translucent": True,
            "translucentBlendOp": "LerpAlpha",
            "castShadows": False,
            "alphaRef": 1,
            "Stages": [
                {
                    "diffuseColor": [0.06, 0.20, 0.26, 0.78],
                    "specular": [0.85, 0.92, 1.0, 1.0],
                    "specularPower": 56,
                    "pixelSpecular": True,
                    "glow": [0, 0, 0, 0],
                    "useAnisotropic": True,
                },
                {},
                {},
                {},
            ],
            "materialTag0": "beamng",
            "materialTag1": "water",
            "annotation": "WATER",
        }
    }
    (water_art / "main.materials.json").write_text(json.dumps(mats, indent=2) + "\n")
    print(f"Wrote {len(objects)} water objects → import/p400_water_objects.json")


if __name__ == "__main__":
    main()
