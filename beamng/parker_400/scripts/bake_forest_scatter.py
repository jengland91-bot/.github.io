#!/usr/bin/env python3
"""Scatter rocks + desert bushes outside the Parker race line (Forest system).

Creates lightweight in-mod .dae shapes (no dependency on other BeamNG maps),
places them along the GPX corridor shoulders, and writes:
  - levels/parker_400/art/forest/managedItemData.json
  - levels/parker_400/art/shapes/...
  - levels/parker_400/forest/*.forest4.json
"""

from __future__ import annotations

import json
import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
LEVEL = ROOT / "levels" / "parker_400"
IMPORT = ROOT / "import"
HEIGHTMAP = IMPORT / "heightmap_4096.png"
ART_SHAPES = LEVEL / "art" / "shapes"
ART_FOREST = LEVEL / "art" / "forest"
FOREST_DIR = LEVEL / "forest"

WORLD_M = 65536.0
HALF = WORLD_M / 2.0
MAX_H = 1500.0
# Keep clear of DecalRoad (~15 m half) + silt; place in outer shoulder band
ROAD_CLEAR_M = 18.0
BAND_INNER_M = 20.0
BAND_OUTER_M = 220.0
STEP_M = 38.0  # denser stations along course for Parker scrub look
RNG_SEED = 4002026
ROCK_P = 0.82
BUSH_P = 0.78
OUTER_ROCK_P = 0.35  # sparse rocks farther out
OUTER_BUSH_P = 0.42


def load_png16_gray(path: Path) -> np.ndarray:
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
        raise ValueError("need 16-bit gray heightmap")
    decompressed = zlib.decompress(raw)
    arr = np.empty((height, width), dtype=np.uint16)
    stride = 1 + width * 2
    for y in range(height):
        row = decompressed[y * stride : (y + 1) * stride]
        arr[y] = np.frombuffer(row[1:], dtype=">u2")
    return arr


def uv_to_world(u: float, v: float) -> tuple[float, float]:
    return u * WORLD_M - HALF, v * WORLD_M - HALF


def sample_height(img: np.ndarray, u: float, v: float) -> float:
    h, w = img.shape
    x = min(w - 1, max(0, int(round(u * (w - 1)))))
    y = min(h - 1, max(0, int(round(v * (h - 1)))))
    return (float(img[y, x]) / 65535.0) * MAX_H


def yaw_matrix(yaw: float) -> list[float]:
    c, s = math.cos(yaw), math.sin(yaw)
    # Z-up: rotate around Z
    return [c, s, 0.0, -s, c, 0.0, 0.0, 0.0, 1.0]


def write_dae_rock(path: Path, name: str, seed: int) -> None:
    """Low-poly irregular rock mesh (unit-ish size ~1.2 m)."""
    rng = np.random.default_rng(seed)
    # Start from icosahedron-ish verts, jitter
    phi = (1 + math.sqrt(5)) / 2
    raw = [
        (-1, phi, 0),
        (1, phi, 0),
        (-1, -phi, 0),
        (1, -phi, 0),
        (0, -1, phi),
        (0, 1, phi),
        (0, -1, -phi),
        (0, 1, -phi),
        (phi, 0, -1),
        (phi, 0, 1),
        (-phi, 0, -1),
        (-phi, 0, 1),
    ]
    verts = []
    for x, y, z in raw:
        # BeamNG Z-up: map (x,y,z_icosa) → (x, z, y) then squash Y less
        vx = x * 0.55 + rng.normal(0, 0.08)
        vy = z * 0.50 + rng.normal(0, 0.08)
        vz = abs(y) * 0.28 + rng.uniform(0.05, 0.15)  # sit on ground
        verts.append((vx, vy, vz))
    # faces of regular icosahedron
    faces = [
        (0, 11, 5),
        (0, 5, 1),
        (0, 1, 7),
        (0, 7, 10),
        (0, 10, 11),
        (1, 5, 9),
        (5, 11, 4),
        (11, 10, 2),
        (10, 7, 6),
        (7, 1, 8),
        (3, 9, 4),
        (3, 4, 2),
        (3, 2, 6),
        (3, 6, 8),
        (3, 8, 9),
        (4, 9, 5),
        (2, 4, 11),
        (6, 2, 10),
        (8, 6, 7),
        (9, 8, 1),
    ]
    pos_list = " ".join(f"{x:.4f} {y:.4f} {z:.4f}" for x, y, z in verts)
    tri = " ".join(f"{a} {b} {c}" for a, b, c in faces)
    mat = "p400_rock_mat"
    dae = f"""<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset><up_axis>Z_UP</up_axis></asset>
  <library_effects>
    <effect id="{mat}-fx"><profile_COMMON>
      <technique sid="common"><lambert>
        <diffuse><color>0.42 0.36 0.30 1</color></diffuse>
      </lambert></technique>
    </profile_COMMON></effect>
  </library_effects>
  <library_materials>
    <material id="{mat}" name="{mat}"><instance_effect url="#{mat}-fx"/></material>
  </library_materials>
  <library_geometries>
    <geometry id="{name}-mesh" name="{name}">
      <mesh>
        <source id="{name}-pos"><float_array id="{name}-pos-array" count="{len(verts)*3}">{pos_list}</float_array>
          <technique_common><accessor source="#{name}-pos-array" count="{len(verts)}" stride="3">
            <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>
          </accessor></technique_common>
        </source>
        <vertices id="{name}-verts"><input semantic="POSITION" source="#{name}-pos"/></vertices>
        <triangles material="{mat}" count="{len(faces)}">
          <input semantic="VERTEX" source="#{name}-verts" offset="0"/>
          <p>{tri}</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="Scene" name="Scene">
      <node id="{name}" name="{name}" type="NODE">
        <instance_geometry url="#{name}-mesh">
          <bind_material><technique_common>
            <instance_material symbol="{mat}" target="#{mat}"/>
          </technique_common></bind_material>
        </instance_geometry>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene><instance_visual_scene url="#Scene"/></scene>
</COLLADA>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dae, encoding="utf-8")


def write_bush_texture(path: Path) -> None:
    """Sparse desert scrub silhouette (RGBA) — short brown-olive clumps."""
    s = 256
    yy, xx = np.mgrid[0:s, 0:s]
    cx, cy = (s - 1) / 2.0, (s - 1) * 0.68
    dx = (xx - cx) / (s * 0.36)
    dy = (yy - cy) / (s * 0.36)
    # low wide scrub (refs are short, not tall bushes)
    r = np.sqrt(dx * dx + dy * dy * 1.35)
    lobe = 0.18 * np.sin(np.arctan2(dy, dx) * 6.0)
    cover = np.clip(1.12 - (r + lobe), 0, 1)
    # ragged edge / holes
    rng = np.random.default_rng(11)
    noise = rng.random((s, s)).astype(np.float32)
    cover = np.clip(cover * (0.75 + 0.35 * noise) - 0.08, 0, 1)
    alpha = (cover**1.55 * 255).astype(np.uint8)
    # dusty brown-olive creosote (Ben refs: dark green/brown scrub)
    rgb = np.zeros((s, s, 3), dtype=np.float32)
    rgb[..., 0] = 68 + 38 * cover
    rgb[..., 1] = 70 + 28 * cover
    rgb[..., 2] = 38 + 14 * cover
    stem = np.exp(-((xx - cx) ** 2) / 70.0) * np.clip((yy - cy) / (s * 0.28), 0, 1)
    rgb[..., 0] *= 1.0 - 0.40 * stem
    rgb[..., 1] *= 1.0 - 0.30 * stem
    rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), alpha])
    write_png8(path, rgba)


def write_dae_bush(path: Path, name: str) -> None:
    """Two crossed planes with bush texture (billboard-style scrub)."""
    # Short wide scrub — refs are knee/waist height clumps, not tall bushes
    mat = "p400_bush_mat"
    verts = [
        (-0.7, 0.0, 0.0),
        (0.7, 0.0, 0.0),
        (0.7, 0.0, 0.72),
        (-0.7, 0.0, 0.72),
        (0.0, -0.7, 0.0),
        (0.0, 0.7, 0.0),
        (0.0, 0.7, 0.72),
        (0.0, -0.7, 0.72),
    ]
    uvs = [
        (0, 1),
        (1, 1),
        (1, 0),
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
        (0, 0),
    ]
    faces = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7)]
    pos_list = " ".join(f"{x:.4f} {y:.4f} {z:.4f}" for x, y, z in verts)
    uv_list = " ".join(f"{u:.4f} {v:.4f}" for u, v in uvs)
    # triangles with VERTEX and TEXCOORD
    p_idx = []
    for a, b, c in faces:
        p_idx.extend([a, a, b, b, c, c])  # v/t pairs with offset 0/1
    p_str = " ".join(str(i) for i in p_idx)
    tex = "/levels/parker_400/art/shapes/bushes/p400_bush_d.png"
    dae = f"""<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset><up_axis>Z_UP</up_axis></asset>
  <library_images>
    <image id="bush_img" name="bush_img"><init_from>{tex}</init_from></image>
  </library_images>
  <library_effects>
    <effect id="{mat}-fx"><profile_COMMON>
      <newparam sid="bush_surface"><surface type="2D"><init_from>bush_img</init_from></surface></newparam>
      <newparam sid="bush_sampler"><sampler2D><source>bush_surface</source></sampler2D></newparam>
      <technique sid="common"><lambert>
        <diffuse><texture texture="bush_sampler" texcoord="UVSET0"/></diffuse>
        <transparent opaque="A_ONE"><texture texture="bush_sampler" texcoord="UVSET0"/></transparent>
      </lambert></technique>
    </profile_COMMON></effect>
  </library_effects>
  <library_materials>
    <material id="{mat}" name="{mat}"><instance_effect url="#{mat}-fx"/></material>
  </library_materials>
  <library_geometries>
    <geometry id="{name}-mesh" name="{name}">
      <mesh>
        <source id="{name}-pos"><float_array id="{name}-pos-array" count="{len(verts)*3}">{pos_list}</float_array>
          <technique_common><accessor source="#{name}-pos-array" count="{len(verts)}" stride="3">
            <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>
          </accessor></technique_common>
        </source>
        <source id="{name}-uv"><float_array id="{name}-uv-array" count="{len(uvs)*2}">{uv_list}</float_array>
          <technique_common><accessor source="#{name}-uv-array" count="{len(uvs)}" stride="2">
            <param name="S" type="float"/><param name="T" type="float"/>
          </accessor></technique_common>
        </source>
        <vertices id="{name}-verts"><input semantic="POSITION" source="#{name}-pos"/></vertices>
        <triangles material="{mat}" count="{len(faces)}">
          <input semantic="VERTEX" source="#{name}-verts" offset="0"/>
          <input semantic="TEXCOORD" source="#{name}-uv" offset="1" set="0"/>
          <p>{p_str}</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="Scene" name="Scene">
      <node id="{name}" name="{name}" type="NODE">
        <instance_geometry url="#{name}-mesh">
          <bind_material><technique_common>
            <instance_material symbol="{mat}" target="#{mat}">
              <bind_vertex_input semantic="UVSET0" input_semantic="TEXCOORD" input_set="0"/>
            </instance_material>
          </technique_common></bind_material>
        </instance_geometry>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene><instance_visual_scene url="#Scene"/></scene>
</COLLADA>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dae, encoding="utf-8")


def densify_uvs(uvs: list[list[float]], max_spacing_m: float) -> list[list[float]]:
    if len(uvs) < 2:
        return list(uvs)
    out: list[list[float]] = [list(uvs[0])]
    for i in range(1, len(uvs)):
        u0, v0 = out[-1]
        u1, v1 = uvs[i]
        x0, y0 = uv_to_world(u0, v0)
        x1, y1 = uv_to_world(u1, v1)
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(math.ceil(dist / max_spacing_m)))
        for k in range(1, n + 1):
            t = k / n
            out.append([u0 + (u1 - u0) * t, v0 + (v1 - v0) * t])
    return out


def main() -> None:
    if not HEIGHTMAP.exists():
        raise SystemExit(f"Missing {HEIGHTMAP}")
    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    uvs = densify_uvs(course["longCourseUv"], STEP_M)
    img = load_png16_gray(HEIGHTMAP)
    rng = np.random.default_rng(RNG_SEED)

    # shapes
    rock_dir = ART_SHAPES / "rocks"
    bush_dir = ART_SHAPES / "bushes"
    rock_dir.mkdir(parents=True, exist_ok=True)
    bush_dir.mkdir(parents=True, exist_ok=True)
    write_dae_rock(rock_dir / "p400_rock_a.dae", "p400_rock_a", seed=1)
    write_dae_rock(rock_dir / "p400_rock_b.dae", "p400_rock_b", seed=2)
    write_bush_texture(bush_dir / "p400_bush_d.png")
    write_dae_bush(bush_dir / "p400_bush_a.dae", "p400_bush_a")

    # BeamNG shape materials (mapTo matches DAE material ids)
    mats = {
        "p400_rock_mat": {
            "name": "p400_rock_mat",
            "mapTo": "p400_rock_mat",
            "class": "Material",
            "persistentId": "p400rockmat000001",
            "Stages": [
                {
                    "diffuseColor": [0.42, 0.36, 0.30, 1],
                    "roughnessFactor": 0.92,
                    "metallicFactor": 0.0,
                    "useAnisotropic": True,
                },
                {},
                {},
                {},
            ],
            "materialTag0": "beamng",
            "materialTag1": "rock",
            "annotation": "ROCK",
        },
        "p400_bush_mat": {
            "name": "p400_bush_mat",
            "mapTo": "p400_bush_mat",
            "class": "Material",
            "persistentId": "p400bushmat000001",
            "Stages": [
                {
                    "colorMap": "/levels/parker_400/art/shapes/bushes/p400_bush_d.png",
                    "roughnessFactor": 0.85,
                    "metallicFactor": 0.0,
                    "alphaRef": 80,
                    "castShadows": True,
                    "useAnisotropic": True,
                },
                {},
                {},
                {},
            ],
            "alphaRef": 80,
            "translucent": True,
            "translucentBlendOp": "None",
            "materialTag0": "beamng",
            "materialTag1": "vegetation",
            "annotation": "FOLIAGE",
        },
    }
    (rock_dir / "main.materials.json").write_text(json.dumps({"p400_rock_mat": mats["p400_rock_mat"]}, indent=2) + "\n")
    (bush_dir / "main.materials.json").write_text(json.dumps({"p400_bush_mat": mats["p400_bush_mat"]}, indent=2) + "\n")

    ART_FOREST.mkdir(parents=True, exist_ok=True)
    managed = {
        "p400_rock_a": {
            "class": "TSForestItemData",
            "internalName": "p400_rock_a",
            "shapeFile": "/levels/parker_400/art/shapes/rocks/p400_rock_a.dae",
            "collidable": True,
            "radius": 1.2,
            "snapRotationToTerrain": False,
            "windScale": 0,
            "annotation": "ROCK",
        },
        "p400_rock_b": {
            "class": "TSForestItemData",
            "internalName": "p400_rock_b",
            "shapeFile": "/levels/parker_400/art/shapes/rocks/p400_rock_b.dae",
            "collidable": True,
            "radius": 1.4,
            "snapRotationToTerrain": False,
            "windScale": 0,
            "annotation": "ROCK",
        },
        "p400_bush_a": {
            "class": "TSForestItemData",
            "internalName": "p400_bush_a",
            "shapeFile": "/levels/parker_400/art/shapes/bushes/p400_bush_a.dae",
            "collidable": False,
            "radius": 1.0,
            "snapRotationToTerrain": False,
            "windScale": 0.35,
            "trunkBendScale": 0.15,
            "branchAmp": 0.4,
            "detailAmp": 0.2,
            "detailFreq": 1.0,
            "annotation": "FOLIAGE",
        },
    }
    (ART_FOREST / "managedItemData.json").write_text(json.dumps(managed, indent=2) + "\n", encoding="utf-8")

    placements: dict[str, list[dict]] = {k: [] for k in managed}

    for i in range(len(uvs) - 1):
        u0, v0 = uvs[i]
        u1, v1 = uvs[i + 1]
        x0, y0 = uv_to_world(u0, v0)
        x1, y1 = uv_to_world(u1, v1)
        dx, dy = x1 - x0, y1 - y0
        seg = math.hypot(dx, dy)
        if seg < 1.0:
            continue
        # unit tangent / normal (left)
        tx, ty = dx / seg, dy / seg
        nx, ny = -ty, tx

        for side in (-1.0, 1.0):
            # Near-shoulder rocks (desert rubble along two-track)
            if rng.random() < ROCK_P:
                dist = float(rng.uniform(BAND_INNER_M, min(95.0, BAND_OUTER_M * 0.45)))
                along = float(rng.uniform(0.12, 0.88))
                px = x0 + tx * seg * along + nx * side * dist
                py = y0 + ty * seg * along + ny * side * dist
                u = (px + HALF) / WORLD_M
                v = (py + HALF) / WORLD_M
                if 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0:
                    z = sample_height(img, u, v) - float(rng.uniform(0.05, 0.35))
                    kind = "p400_rock_a" if rng.random() < 0.55 else "p400_rock_b"
                    scale = float(rng.uniform(0.65, 2.4))
                    yaw = float(rng.uniform(0, math.tau))
                    placements[kind].append(
                        {
                            "type": kind,
                            "pos": [round(px, 2), round(py, 2), round(z, 2)],
                            "rotationMatrix": [round(v, 5) for v in yaw_matrix(yaw)],
                            "scale": round(scale, 3),
                        }
                    )
            # Farther sparse rock piles
            if rng.random() < OUTER_ROCK_P:
                dist = float(rng.uniform(90.0, BAND_OUTER_M))
                along = float(rng.uniform(0.1, 0.9))
                px = x0 + tx * seg * along + nx * side * dist
                py = y0 + ty * seg * along + ny * side * dist
                u = (px + HALF) / WORLD_M
                v = (py + HALF) / WORLD_M
                if 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0:
                    z = sample_height(img, u, v) - float(rng.uniform(0.05, 0.4))
                    kind = "p400_rock_b" if rng.random() < 0.6 else "p400_rock_a"
                    scale = float(rng.uniform(0.9, 2.8))
                    yaw = float(rng.uniform(0, math.tau))
                    placements[kind].append(
                        {
                            "type": kind,
                            "pos": [round(px, 2), round(py, 2), round(z, 2)],
                            "rotationMatrix": [round(v, 5) for v in yaw_matrix(yaw)],
                            "scale": round(scale, 3),
                        }
                    )
            # Creosote / brush clumps near road
            bush_n = 1 + int(rng.random() < 0.45)
            for _ in range(bush_n):
                if rng.random() > BUSH_P:
                    continue
                dist = float(rng.uniform(BAND_INNER_M * 0.9, min(120.0, BAND_OUTER_M * 0.55)))
                along = float(rng.uniform(0.08, 0.92))
                px = x0 + tx * seg * along + nx * side * dist
                py = y0 + ty * seg * along + ny * side * dist
                u = (px + HALF) / WORLD_M
                v = (py + HALF) / WORLD_M
                if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
                    continue
                z = sample_height(img, u, v) - 0.02
                # Shorter scrub scales to match open-desert refs
                scale = float(rng.uniform(0.55, 1.45))
                yaw = float(rng.uniform(0, math.tau))
                placements["p400_bush_a"].append(
                    {
                        "type": "p400_bush_a",
                        "pos": [round(px, 2), round(py, 2), round(z, 2)],
                        "rotationMatrix": [round(v, 5) for v in yaw_matrix(yaw)],
                        "scale": round(scale, 3),
                    }
                )
            # Sparse outer scrub
            if rng.random() < OUTER_BUSH_P:
                dist = float(rng.uniform(100.0, BAND_OUTER_M))
                along = float(rng.uniform(0.1, 0.9))
                px = x0 + tx * seg * along + nx * side * dist
                py = y0 + ty * seg * along + ny * side * dist
                u = (px + HALF) / WORLD_M
                v = (py + HALF) / WORLD_M
                if 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0:
                    z = sample_height(img, u, v) - 0.02
                    scale = float(rng.uniform(0.5, 1.35))
                    yaw = float(rng.uniform(0, math.tau))
                    placements["p400_bush_a"].append(
                        {
                            "type": "p400_bush_a",
                            "pos": [round(px, 2), round(py, 2), round(z, 2)],
                            "rotationMatrix": [round(v, 5) for v in yaw_matrix(yaw)],
                            "scale": round(scale, 3),
                        }
                    )

    FOREST_DIR.mkdir(parents=True, exist_ok=True)
    # clear old forest4
    for old in FOREST_DIR.glob("*.forest4.json"):
        old.unlink()

    total = 0
    for kind, items in placements.items():
        out = FOREST_DIR / f"{kind}.forest4.json"
        with out.open("w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, separators=(",", ":")) + "\n")
        total += len(items)
        print(f"  {kind}: {len(items)} → {out.name}")

    meta = {
        "totalItems": total,
        "bandInnerM": BAND_INNER_M,
        "bandOuterM": BAND_OUTER_M,
        "stepM": STEP_M,
        "types": {k: len(v) for k, v in placements.items()},
    }
    (FOREST_DIR / "scatter_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    print("Forest scatter ready — ensure bake_level.py includes theForest object")


if __name__ == "__main__":
    main()
