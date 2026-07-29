#!/usr/bin/env python3
"""Bake California 300 level scene objects at GPX-matched 16384 m scale.

Writes:
  - levels/california_300/main/items.level.json
    (TerrainBlock + CA300 DecalRoad + pit row + spawns/env)
  - levels/california_300/import/ca300_gpx_scale.preset.json
    (World Editor Import Terrain preset: squareSize=4, maxHeight=900)
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]  # beamng/california_300
CA300 = ROOT / "source" / "reference" / "ca300"
LEVEL = ROOT / "levels" / "california_300"
IMPORT = ROOT / "import"
HEIGHTMAP = IMPORT / "heightmap_4096.png"

WORLD_M = 16384.0
HALF = WORLD_M / 2.0
SQUARE = 4.0
MAX_H = 900.0
COURSE_WIDTH = 9.0  # meters — Ultra 4 / desert race ribbon
PIT_WIDTH = 12.0


def uv_to_world(u: float, v: float) -> tuple[float, float]:
    """Map UV (0..1, Y north) to BeamNG world XY with terrain corner at -8192,-8192."""
    return u * WORLD_M - HALF, v * WORLD_M - HALF


def sample_height(img: Image.Image, u: float, v: float) -> float:
    """Sample 16-bit heightmap; BeamNG Y-north UV → image row from bottom."""
    w, h = img.size
    x = min(w - 1, max(0, int(round(u * (w - 1)))))
    y = min(h - 1, max(0, int(round((1.0 - v) * (h - 1)))))
    px = img.getpixel((x, y))
    if isinstance(px, tuple):
        px = px[0]
    return (float(px) / 65535.0) * MAX_H


def nodes_from_uv(uvs: list[list[float]], img: Image.Image, width: float) -> list[list[float]]:
    out = []
    for u, v in uvs:
        x, y = uv_to_world(u, v)
        z = sample_height(img, u, v)
        out.append([round(x, 2), round(y, 2), round(z, 2), width])
    return out


def main() -> None:
    course = json.loads((CA300 / "ca300_map_course.json").read_text(encoding="utf-8"))
    img = Image.open(HEIGHTMAP)

    course_nodes = nodes_from_uv(course["longCourseUv"], img, COURSE_WIDTH)
    pit_nodes = nodes_from_uv(course.get("pitRowUv") or [], img, PIT_WIDTH)

    # Spawn near start of course (first UV) and pits midpoint
    sx, sy = uv_to_world(*course["longCourseUv"][0])
    sz = sample_height(img, *course["longCourseUv"][0]) + 3.0
    if pit_nodes:
        mid = pit_nodes[len(pit_nodes) // 2]
        px, py, pz = mid[0], mid[1], mid[2] + 3.0
    else:
        px, py, pz = sx, sy, sz

    lines: list[dict] = [
        {"class": "SimGroup", "name": "MissionGroup"},
        {"class": "SimGroup", "name": "PlayerDropPoints", "__parent": "MissionGroup"},
        {
            "class": "SpawnSphere",
            "name": "spawns_pits",
            "__parent": "PlayerDropPoints",
            "position": [round(px, 2), round(py, 2), round(pz, 2)],
            "rotationMatrix": [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "scale": [1, 1, 1],
            "radius": 14,
            "spineRadius": 2,
            "canSaveDynamicFields": 1,
        },
        {
            "class": "SpawnSphere",
            "name": "spawns_course",
            "__parent": "PlayerDropPoints",
            "position": [round(sx, 2), round(sy, 2), round(sz, 2)],
            "rotationMatrix": [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "scale": [1, 1, 1],
            "radius": 12,
            "spineRadius": 2,
            "canSaveDynamicFields": 1,
        },
        {"class": "SimGroup", "name": "LevelObjects", "__parent": "MissionGroup"},
        {
            "class": "TerrainBlock",
            "name": "theTerrain",
            "__parent": "LevelObjects",
            "position": [-8192, -8192, 0],
            "rotationMatrix": [1, 0, 0, 0, 1, 0, 0, 0, 1],
            "scale": [1, 1, 1],
            "terrainFile": "/levels/california_300/theTerrain.ter",
            "squareSize": SQUARE,
            "maxHeight": MAX_H,
            "baseTexSize": 1024,
            "lightMapSize": 256,
            "screenError": 16,
            "castShadows": True,
            "canSave": True,
            "canSaveDynamicFields": True,
        },
        {"class": "SimGroup", "name": "Roads", "__parent": "LevelObjects"},
        {
            "class": "DecalRoad",
            "name": "ca300_race_ready",
            "__parent": "Roads",
            "material": "road_asphalt_2lane",
            "textureLength": 12,
            "drivability": 1,
            "oneWay": False,
            "autoLanes": True,
            "autoJunction": True,
            "overObjects": False,
            "renderPriority": 10,
            "nodes": course_nodes,
        },
    ]

    if len(pit_nodes) >= 2:
        lines.append(
            {
                "class": "DecalRoad",
                "name": "ca300_pit_row",
                "__parent": "Roads",
                "material": "road_asphalt_2lane",
                "textureLength": 10,
                "drivability": 1,
                "oneWay": False,
                "autoLanes": True,
                "autoJunction": True,
                "overObjects": False,
                "renderPriority": 11,
                "nodes": pit_nodes,
            }
        )

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
                "blurClamp": 0.12,
                "blurMin": 0.05,
                "blurSlope": 0.85,
                "ambient": [0.45, 0.38, 0.28, 1],
                "fogColor": [0.72, 0.58, 0.38, 1],
                "fogDensity": 0.00022,
                "fogDensityOffset": 120,
                "nearClip": 0.1,
                "visibleDistance": 12000,
                "gravity": -9.81,
            },
            {
                "class": "TimeOfDay",
                "name": "tod",
                "__parent": "Environment",
                "time": 0.5,
                "dayLength": 120,
                "azimuthOverride": 0,
                "startTime": 0.5,
            },
            {
                "class": "CloudLayer",
                "name": "clouds",
                "__parent": "Environment",
                "coverage": 0.18,
                "windSpeed": 0.4,
            },
            {"class": "SimGroup", "name": "TODO_WorldEditor", "__parent": "MissionGroup"},
            {
                "class": "Note",
                "name": "build_notes",
                "__parent": "TODO_WorldEditor",
                "position": [0, 0, 120],
                "text": (
                    "GPX scale locked: Import import/heightmap_4096.png with "
                    "Load Preset ca300_gpx_scale.preset.json (squareSize=4, maxHeight=900, "
                    "pos -8192,-8192). DecalRoad ca300_race_ready follows 2024 Race Ready course."
                ),
            },
        ]
    )

    out_items = LEVEL / "main" / "items.level.json"
    out_items.parent.mkdir(parents=True, exist_ok=True)
    with out_items.open("w", encoding="utf-8") as f:
        for obj in lines:
            f.write(json.dumps(obj, separators=(",", ":")) + "\n")

    preset = {
        "type": "TerrainData",
        "name": "theTerrain",
        "heightMapPath": "/levels/california_300/import/heightmap_4096.png",
        "heightScale": MAX_H,
        "holeMapPath": "",
        "opacityMaps": [],
        "pos": {"x": -8192, "y": -8192, "z": 0},
        "squareSize": SQUARE,
        "applyTransform": True,
        "flipYAxis": False,
    }
    IMPORT.mkdir(parents=True, exist_ok=True)
    # Also copy into level import path used by BeamNG userfolder layout
    level_import = LEVEL / "import"
    level_import.mkdir(parents=True, exist_ok=True)
    for dest in (IMPORT / "ca300_gpx_scale.preset.json", level_import / "ca300_gpx_scale.preset.json"):
        dest.write_text(json.dumps(preset, indent=2) + "\n", encoding="utf-8")

    # Ensure heightmap is also under levels/.../import for the preset path
    hm_level = level_import / "heightmap_4096.png"
    if not hm_level.exists() or hm_level.stat().st_size != HEIGHTMAP.stat().st_size:
        hm_level.write_bytes(HEIGHTMAP.read_bytes())

    meta = {
        "worldSizeMeters": WORLD_M,
        "squareSize": SQUARE,
        "maxHeight": MAX_H,
        "geographicScale": course["geographicScale"],
        "courseMiles": course["courseMiles"],
        "courseNodes": len(course_nodes),
        "pitNodes": len(pit_nodes),
        "terrainPosition": [-8192, -8192, 0],
        "importPreset": "import/ca300_gpx_scale.preset.json",
        "heightmap": "import/heightmap_4096.png",
    }
    (IMPORT / "gpx_scale_build.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
