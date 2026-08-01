#!/usr/bin/env python3
"""Bake Parker 400 BeamNG level objects at 1:1 GPX scale.

Writes:
  - levels/parker_400/main/items.level.json
  - levels/parker_400/import/p400_gpx_scale.preset.json
  - import/p400_gpx_scale.preset.json
  - import/gpx_scale_build.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

P400 = ROOT / "source" / "reference" / "p400"
LEVEL = ROOT / "levels" / "parker_400"
IMPORT = ROOT / "import"
LEVEL_IMPORT = LEVEL / "import"
HEIGHTMAP = IMPORT / "heightmap_4096.png"

WORLD_M = 65536.0
HALF = WORLD_M / 2.0
SQUARE = 16.0
MAX_H = 1500.0
COURSE_WIDTH = 30.0  # off-road dirt DecalRoad width (meters)
PIT_WIDTH = 18.0
SPAWN_CLEARANCE_M = 25.0  # drop-in height so vehicles don't spawn under terrain
# Insert intermediate DecalRoad nodes so long GPX gaps don't leave broken ribbon
COURSE_MAX_NODE_SPACING_M = 40.0


def load_png16_gray(path: Path) -> np.ndarray:
    """Minimal 16-bit grayscale PNG reader (IHDR/IDAT only)."""
    import struct
    import zlib

    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    pos = 8
    width = height = bit_depth = color_type = None
    raw = b""
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        tag = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            width, height, bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", chunk)
        elif tag == b"IDAT":
            raw += chunk
        elif tag == b"IEND":
            break
    if width is None or bit_depth != 16 or color_type != 0:
        raise ValueError(f"unsupported PNG: {width}x{height} depth={bit_depth} type={color_type}")
    decompressed = zlib.decompress(raw)
    arr = np.empty((height, width), dtype=np.uint16)
    stride = 1 + width * 2
    for y in range(height):
        row = decompressed[y * stride : (y + 1) * stride]
        # skip filter byte
        arr[y] = np.frombuffer(row[1:], dtype=">u2")
    return arr


def uv_to_world(u: float, v: float) -> tuple[float, float]:
    return u * WORLD_M - HALF, v * WORLD_M - HALF


def sample_height(img: np.ndarray, u: float, v: float) -> float:
    h, w = img.shape
    x = min(w - 1, max(0, int(round(u * (w - 1)))))
    # BeamNG Y-north UV → image row from bottom (our bake stores v north at top of array row0=north)
    # bake_srtm uses v increasing with image row index from top (row0 = v=0 south? Wait)
    # In bake: ys,xs = mgrid; v = ys/(SIZE-1) → row 0 has v=0.
    # convert meters_to_uv: Y north increases v. So row 0 = south (v=0), row max = north.
    # That's image-y increasing north — atypical for images but consistent.
    # Sample directly: y = v * (h-1)
    y = min(h - 1, max(0, int(round(v * (h - 1)))))
    return (float(img[y, x]) / 65535.0) * MAX_H


def densify_uvs(uvs: list[list[float]], max_spacing_m: float) -> list[list[float]]:
    """Subdivide long GPX segments so DecalRoad / paint stay continuous."""
    if len(uvs) < 2:
        return list(uvs)
    out: list[list[float]] = [list(uvs[0])]
    for i in range(1, len(uvs)):
        u0, v0 = out[-1]
        u1, v1 = uvs[i]
        x0, y0 = uv_to_world(u0, v0)
        x1, y1 = uv_to_world(u1, v1)
        dist = float(np.hypot(x1 - x0, y1 - y0))
        n = max(1, int(np.ceil(dist / max_spacing_m)))
        for k in range(1, n + 1):
            t = k / n
            out.append([u0 + (u1 - u0) * t, v0 + (v1 - v0) * t])
    return out


def nodes_from_uv(uvs: list[list[float]], img: np.ndarray, width: float) -> list[list[float]]:
    dense = densify_uvs(uvs, COURSE_MAX_NODE_SPACING_M)
    out = []
    for u, v in dense:
        x, y = uv_to_world(u, v)
        z = sample_height(img, u, v)
        out.append([round(x, 2), round(y, 2), round(z, 2), width])
    return out


def main() -> None:
    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    waypoints = json.loads((P400 / "p400_map_waypoints.json").read_text(encoding="utf-8"))
    if not HEIGHTMAP.exists():
        raise SystemExit("Missing heightmap — run bake_srtm_heightmap.py first")
    img = load_png16_gray(HEIGHTMAP)

    course_nodes = nodes_from_uv(course["longCourseUv"], img, COURSE_WIDTH)

    # Build a short pit-row ribbon near Main Pit if present, else first pit center
    pits = course.get("pitCenters") or []
    pit_nodes: list[list[float]] = []
    main = next((p for p in pits if p.get("name") == "Main Pit"), pits[0] if pits else None)
    if main:
        u, v = main["uv"]
        # small E-W pad
        for du in (-0.0012, -0.0006, 0.0, 0.0006, 0.0012):
            x, y = uv_to_world(u + du, v)
            z = sample_height(img, u + du, v)
            pit_nodes.append([round(x, 2), round(y, 2), round(z, 2), PIT_WIDTH])

    # Spawns
    start = next((g for g in waypoints.get("gates", []) if g.get("name") == "Start Line"), None)
    if start:
        su, sv = start["uv"]
    else:
        su, sv = course["longCourseUv"][0]
    sx, sy = uv_to_world(su, sv)
    sz = sample_height(img, su, sv) + SPAWN_CLEARANCE_M
    if pit_nodes:
        mid = pit_nodes[len(pit_nodes) // 2]
        px, py = mid[0], mid[1]
        pz = mid[2] + SPAWN_CLEARANCE_M
    else:
        px, py, pz = sx, sy, sz

    lines: list[dict] = [
        {"class": "SimGroup", "name": "MissionGroup"},
        {"class": "SimGroup", "name": "PlayerDropPoints", "__parent": "MissionGroup"},
        {
            "class": "SpawnSphere",
            "name": "spawns_pits",
            "__parent": "PlayerDropPoints",
            "dataBlock": "SpawnSphereMarker",
            "position": [round(px, 2), round(py, 2), round(pz, 2)],
            "rotationMatrix": [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "scale": [1, 1, 1],
            "radius": 16,
            "spineRadius": 2,
            "canSaveDynamicFields": 1,
        },
        {
            "class": "SpawnSphere",
            "name": "spawns_course",
            "__parent": "PlayerDropPoints",
            "dataBlock": "SpawnSphereMarker",
            "position": [round(sx, 2), round(sy, 2), round(sz, 2)],
            "rotationMatrix": [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "scale": [1, 1, 1],
            "radius": 14,
            "spineRadius": 2,
            "canSaveDynamicFields": 1,
        },
        {"class": "SimGroup", "name": "LevelObjects", "__parent": "MissionGroup"},
        {
            "class": "TerrainBlock",
            "name": "theTerrain",
            "__parent": "LevelObjects",
            "position": [-HALF, -HALF, 0],
            "rotationMatrix": [1, 0, 0, 0, 1, 0, 0, 0, 1],
            "scale": [1, 1, 1],
            "terrainFile": "/levels/parker_400/theTerrain.ter",
            "materialTextureSet": "parker_400TerrainMaterialTextureSet",
            "squareSize": SQUARE,
            "maxHeight": MAX_H,
            "baseTexSize": 1024,
            "lightMapSize": 256,
            "screenError": 24,
            "castShadows": True,
            "canSave": True,
            "canSaveDynamicFields": True,
        },
        {"class": "SimGroup", "name": "Roads", "__parent": "LevelObjects"},
        {
            "class": "DecalRoad",
            "name": "p400_ctutv_course",
            "__parent": "Roads",
            "material": "p400_dirt_road",
            "textureLength": 14,
            "drivability": 0.55,
            "oneWay": False,
            "autoLanes": True,
            "autoJunction": True,
            "overObjects": False,
            # Baked gold trail is in minimap/terrain.png; keep DecalRoad visible in
            # nav too (large maps often clip engine roads — baked PNG is the backup)
            "hiddenInNavi": False,
            "renderPriority": 10,
            "improvedSpline": True,
            "smoothness": 0.45,
            "detail": 0.2,
            "decalBias": 0.003,
            "distanceFade": [12000, 1200],
            "nodes": course_nodes,
        },
    ]

    if len(pit_nodes) >= 2:
        lines.append(
            {
                "class": "DecalRoad",
                "name": "p400_main_pit",
                "__parent": "Roads",
                "material": "p400_dirt_road",
                "textureLength": 12,
                "drivability": 0.55,
                "oneWay": False,
                "autoLanes": True,
                "autoJunction": True,
                "overObjects": False,
                "hiddenInNavi": False,
                "renderPriority": 11,
                "decalBias": 0.003,
                "distanceFade": [8000, 800],
                "nodes": pit_nodes,
            }
        )

    # Waypoints (pits/VCPs/dangers) stay in p400_map_waypoints.json for props later.
    lines.extend(
        [
            {"class": "SimGroup", "name": "Environment", "__parent": "MissionGroup"},
            {
                "class": "LevelInfo",
                "name": "theLevelInfo",
                "__parent": "Environment",
                "visible": True,
                "canSave": True,
                "canSaveDynamicFields": True,
                "blurClamp": 0.08,
                "blurMin": 0.03,
                "blurSlope": 0.9,
                "ambient": [0.55, 0.52, 0.48, 1],
                "fogColor": [0.78, 0.82, 0.88, 1],
                "fogDensity": 0.00002,
                "fogAtmosphereHeight": 1200,
                "nearClip": 0.1,
                "visibleDistance": 25000,
                "gravity": -9.81,
                "bigMapTimeOfDay": 0.0,
            },
            {
                # BeamNG TOD: 0=noon, 0.25=evening, 0.5=midnight, 0.75=morning
                "class": "TimeOfDay",
                "name": "tod",
                "__parent": "Environment",
                "time": 0.0,
                "startTime": 0.0,
                "dayLength": 2400,
                "play": False,
                "axisTilt": 23.44,
                "latitude": 34.15,
                "longitude": -114.29,
                "year": 2026,
                "month": 2,
                "day": 7,
                "utcOffset": "-7",
                "dstRule": "us",
                "celestialProfile": "earth",
            },
            {
                "class": "ScatterSky",
                "name": "theScatterSky",
                "__parent": "Environment",
                "canSave": True,
                "canSaveDynamicFields": True,
                "skyBrightness": 40,
                "mieScattering": 0.0018,
                "rayleighScattering": 0.0022,
                "exposure": 1.15,
            },
            {
                "class": "CloudLayer",
                "name": "clouds",
                "__parent": "Environment",
                "coverage": 0.04,
                "windSpeed": 0.3,
            },
        ]
    )

    LEVEL.joinpath("main").mkdir(parents=True, exist_ok=True)
    LEVEL_IMPORT.mkdir(parents=True, exist_ok=True)
    IMPORT.mkdir(parents=True, exist_ok=True)

    # items.level.json is newline-delimited JSON objects in BeamNG
    items_path = LEVEL / "main" / "items.level.json"
    with items_path.open("w", encoding="utf-8") as f:
        for obj in lines:
            f.write(json.dumps(obj, separators=(",", ":")) + "\n")

    preset = {
        "type": "TerrainData",
        "name": "theTerrain",
        "heightMapPath": "/levels/parker_400/import/heightmap_4096.png",
        "heightScale": MAX_H,
        "holeMapPath": "",
        "opacityMaps": [],
        "pos": {"x": -HALF, "y": -HALF, "z": 0},
        "squareSize": SQUARE,
        "applyTransform": True,
        "flipYAxis": False,
    }
    (IMPORT / "p400_gpx_scale.preset.json").write_text(json.dumps(preset, indent=2) + "\n", encoding="utf-8")
    (LEVEL_IMPORT / "p400_gpx_scale.preset.json").write_text(json.dumps(preset, indent=2) + "\n", encoding="utf-8")

    build = {
        "worldSizeMeters": WORLD_M,
        "squareSize": SQUARE,
        "maxHeight": MAX_H,
        "geographicScale": course["geographicScale"],
        "courseMiles": course["courseMiles"],
        "courseNodes": len(course_nodes),
        "pitNodes": len(pit_nodes),
        "waypointFile": "source/reference/p400/p400_map_waypoints.json",
        "terrainPosition": [-HALF, -HALF, 0],
        "importPreset": "import/p400_gpx_scale.preset.json",
        "heightmap": "import/heightmap_4096.png",
    }
    (IMPORT / "gpx_scale_build.json").write_text(json.dumps(build, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(build, indent=2))
    print(f"Wrote {items_path}")


if __name__ == "__main__":
    main()
