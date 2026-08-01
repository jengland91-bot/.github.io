#!/usr/bin/env python3
"""
Parker 400 — desert bushes & trees for BeamNG (TSStatic).

Foliage rules (alpha / overdraw):
  - Cut meshes tightly to leaf silhouettes — no large empty transparent quads
  - Single-sided leaf planes only (do NOT duplicate faces)
  - Enable Two-Sided / Double-Sided on the material IN BeamNG, not in Blender
  - Prefer fewer sprays over stacked transparent layers

  /tmp/blender-4.2.9-linux-x64/blender --background --python batch_export_flora.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent
PROPS = ROOT.parent
sys.path.insert(0, str(PROPS / "_shared"))
from beamng_export import (  # noqa: E402
    apply_object,
    clear_scene,
    cylinder_collider,
    export_dae,
    wrap_beamng_hierarchy,
)

OUT = ROOT / "export" / "dae"
ATLAS = PROPS / "atlases" / "vegetation_atlas_2048.png"
ORM = PROPS / "atlases" / "vegetation_orm_2048.png"
LAYOUT = json.loads((PROPS / "atlases" / "vegetation_atlas_layout.json").read_text())


def load_image(path: Path):
    path = Path(path)
    for img in bpy.data.images:
        if img.name == path.name:
            return img
    if path.exists():
        return bpy.data.images.load(str(path))
    return None


def get_bark_mat():
    """Opaque atlas material (trunk / cactus) — no alpha."""
    name = "ParkerVegBark"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = load_image(ATLAS)
    tex.interpolation = "Closest"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    mat.blend_method = "OPAQUE"
    mat["beamng_two_sided"] = False
    return mat


def get_foliage_mat():
    """
    Alpha-clip foliage atlas material.
    SINGLE-SIDED mesh — set Two-Sided in BeamNG material editor (do not duplicate faces).
    """
    name = "ParkerVegFoliage"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = load_image(ATLAS)
    tex.interpolation = "Closest"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    # Alpha clip — opaque leaf blobs only; mesh already hugs silhouette
    if "Alpha" in bsdf.inputs:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.85
    mat.blend_method = "CLIP"
    if hasattr(mat, "alpha_threshold"):
        mat.alpha_threshold = 0.45
    # Explicitly single-sided in Blender
    mat.use_backface_culling = True
    mat["beamng_two_sided"] = True  # reminder for engine setup
    mat["beamng_note"] = "Enable Two-Sided in BeamNG — do not duplicate faces"
    if ORM.exists():
        tex_orm = nodes.new("ShaderNodeTexImage")
        tex_orm.image = load_image(ORM)
        tex_orm.location = (-600, -300)
        mat["orm_map"] = ORM.name
    return mat


def uv_set_rect(obj, key: str, uv_inset: float = 0.0):
    """Map faces into atlas rect. Optional inset keeps UVs on opaque leaf pixels."""
    rect = LAYOUT["rects"][key]
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    u0, v0, u1, v1 = rect["u0"], rect["v0"], rect["u1"], rect["v1"]
    if uv_inset > 0:
        du, dv = (u1 - u0) * uv_inset, (v1 - v0) * uv_inset
        u0, u1, v0, v1 = u0 + du, u1 - du, v0 + dv, v1 - dv
    corners4 = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    corners3 = [(u0, v0), (u1, v0), (u1, v1)]
    for poly in me.polygons:
        idxs = list(poly.loop_indices)
        if len(idxs) == 4:
            for li, uvco in zip(idxs, corners4):
                uv[li].uv = uvco
        elif len(idxs) == 3:
            for li, uvco in zip(idxs, corners3):
                uv[li].uv = uvco


def uv_from_local_xy(obj, key: str, bounds: tuple[float, float, float, float]):
    """
    Project each loop UV from local X/Y into atlas rect.
    bounds = (xmin, ymin, xmax, ymax) of the silhouette in local mesh space.
    """
    rect = LAYOUT["rects"][key]
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    u0, v0, u1, v1 = rect["u0"], rect["v0"], rect["u1"], rect["v1"]
    # Inset UVs ~10% so silhouette stays on opaque leaf blobs
    du, dv = (u1 - u0) * 0.10, (v1 - v0) * 0.10
    u0, u1, v0, v1 = u0 + du, u1 - du, v0 + dv, v1 - dv
    xmin, ymin, xmax, ymax = bounds
    bw = max(1e-6, xmax - xmin)
    bh = max(1e-6, ymax - ymin)
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            co = me.vertices[vi].co
            tx = (co.x - xmin) / bw
            ty = (co.y - ymin) / bh
            uv[li].uv = (u0 + (u1 - u0) * tx, v0 + (v1 - v0) * ty)


# Irregular outlines hugging foliage (normalized ~[-0.5, 0.5]) — NOT full quads
SILHOUETTES = {
    "bush": [
        (0.00, 0.46),
        (0.22, 0.40),
        (0.38, 0.18),
        (0.36, -0.08),
        (0.22, -0.32),
        (0.05, -0.44),
        (-0.18, -0.40),
        (-0.36, -0.20),
        (-0.40, 0.05),
        (-0.30, 0.30),
        (-0.12, 0.44),
    ],
    "branch": [
        (0.00, 0.48),
        (0.18, 0.30),
        (0.28, 0.05),
        (0.20, -0.25),
        (0.05, -0.45),
        (-0.12, -0.35),
        (-0.26, -0.05),
        (-0.22, 0.25),
        (-0.08, 0.42),
    ],
    "scrub": [
        (0.00, 0.42),
        (0.30, 0.28),
        (0.40, 0.00),
        (0.28, -0.28),
        (0.00, -0.40),
        (-0.28, -0.28),
        (-0.40, 0.00),
        (-0.30, 0.28),
    ],
}


def foliage_silhouette(name, loc, size_xy, rot_euler, mat, atlas_key, shape="bush"):
    """
    Single-sided silhouette mesh cut tightly around foliage.
    Avoids large empty transparent quad overdraw.
    Do NOT duplicate for two-sided — enable Two-Sided in engine.
    """
    sx, sy = size_xy
    outline = SILHOUETTES.get(shape, SILHOUETTES["bush"])
    # Build in XY, then rotate into place
    verts = [(p[0] * sx, p[1] * sy, 0.0) for p in outline]
    # Fan from centroid
    cx = sum(v[0] for v in verts) / len(verts)
    cy = sum(v[1] for v in verts) / len(verts)
    verts.append((cx, cy, 0.0))
    cidx = len(verts) - 1
    faces = []
    n = len(outline)
    for i in range(n):
        faces.append((i, (i + 1) % n, cidx))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot_euler
    apply_object(obj)
    obj.data.materials.append(mat)

    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    # After apply, verts are in object local (rotation baked) — recompute bounds from mesh
    # UVs: use pre-bake XY from original outline mapped into atlas
    # Re-read coords after apply — rotation baked into mesh, so use projected bounds from outline
    uv_from_outline(obj, atlas_key, outline, sx, sy)
    return obj


def uv_from_outline(obj, key: str, outline, sx: float, sy: float):
    """UV from silhouette outline parameters (stable after rot/scale bake)."""
    rect = LAYOUT["rects"][key]
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    u0, v0, u1, v1 = rect["u0"], rect["v0"], rect["u1"], rect["v1"]
    du, dv = (u1 - u0) * 0.08, (v1 - v0) * 0.08
    u0, u1, v0, v1 = u0 + du, u1 - du, v0 + dv, v1 - dv

    # Map by matching vertex index: outline verts 0..n-1, center n
    n = len(outline)
    # Build per-vertex UV for original topology
    vert_uv = []
    for i, (ox, oy) in enumerate(outline):
        tx = ox + 0.5  # [-0.5,0.5] → [0,1]
        ty = oy + 0.5
        vert_uv.append((u0 + (u1 - u0) * tx, v0 + (v1 - v0) * ty))
    # center
    vert_uv.append((u0 + (u1 - u0) * 0.5, v0 + (v1 - v0) * 0.5))

    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            if vi < len(vert_uv):
                uv[li].uv = vert_uv[vi]


def stem_cyl(name, loc, radius, depth, mat, atlas_key, verts=8, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rot
    apply_object(obj)
    obj.data.materials.append(mat)
    uv_set_rect(obj, atlas_key)
    return obj


def copy_atlas(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in (ATLAS, ORM):
        if f.exists():
            (out_dir / f.name).write_bytes(f.read_bytes())


# ---------------------------------------------------------------------------
# BUSHES — few silhouette sprays + stem; capsule collider
# ---------------------------------------------------------------------------
def build_creosote(name: str, height: float, spread: float, seed: int):
    clear_scene()
    bark = get_bark_mat()
    leaf = get_foliage_mat()
    rng = random.Random(seed)
    parts = []

    stem_h = height * 0.35
    stem_r = max(0.02, spread * 0.04)
    parts.append(
        stem_cyl("stem", (0, 0, stem_h / 2), stem_r, stem_h, bark, "creosote_bark", verts=8)
    )

    # FEWER sprays (3–4) to limit transparent overdraw; silhouettes not full quads
    n_cards = 3 if height < 1.2 else 4
    for i in range(n_cards):
        ang = (i / n_cards) * math.tau + rng.uniform(-0.15, 0.15)
        z = stem_h * 0.55 + (i % 2) * (height - stem_h) * 0.25
        cx = math.cos(ang) * spread * 0.12
        cy = math.sin(ang) * spread * 0.12
        card_w = spread * rng.uniform(0.55, 0.75)
        card_h = (height - stem_h) * rng.uniform(0.65, 0.85)
        rot = (math.radians(90), 0, ang + math.pi / 2)
        parts.append(
            foliage_silhouette(
                f"leaf_{i}",
                (cx, cy, z + card_h * 0.35),
                (card_w, card_h),
                rot,
                leaf,
                "creosote_leaf",
                shape="bush",
            )
        )

    col_h = height * 0.85
    col_r = spread * 0.35

    def cols(parent):
        cylinder_collider("bush", (0, 0, col_h / 2), col_r, col_h, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


def build_dry_scrub(name: str, height: float, spread: float, seed: int):
    clear_scene()
    bark = get_bark_mat()
    leaf = get_foliage_mat()
    rng = random.Random(seed)
    parts = [
        stem_cyl("stem", (0, 0, 0.04), 0.025, 0.08, bark, "ocotillo_stem", verts=6)
    ]
    # 3 silhouettes only — enough volume, low overdraw
    for i in range(3):
        ang = i * (math.tau / 3) + rng.uniform(-0.1, 0.1)
        rot = (math.radians(90), 0, ang)
        parts.append(
            foliage_silhouette(
                f"scrub_{i}",
                (0, 0, height * 0.45),
                (spread * 0.85, height * 0.9),
                rot,
                leaf,
                "dry_bush",
                shape="scrub",
            )
        )

    def cols(parent):
        cylinder_collider("scrub", (0, 0, height / 2), spread * 0.4, height, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


# ---------------------------------------------------------------------------
# SAGUARO — opaque cylinders only (no alpha foliage)
# ---------------------------------------------------------------------------
def build_saguaro(name: str, height: float, arms: int, seed: int):
    clear_scene()
    mat = get_bark_mat()
    rng = random.Random(seed)
    parts = []
    trunk_r = 0.18 + height * 0.02
    parts.append(
        stem_cyl(
            "trunk_lo",
            (0, 0, height * 0.35),
            trunk_r,
            height * 0.7,
            mat,
            "saguaro_rib",
            verts=12,
        )
    )
    parts.append(
        stem_cyl(
            "trunk_hi",
            (0, 0, height * 0.75),
            trunk_r * 0.85,
            height * 0.5,
            mat,
            "saguaro_skin",
            verts=12,
        )
    )
    for i in range(arms):
        side = -1 if i % 2 == 0 else 1
        arm_h = height * rng.uniform(0.28, 0.4)
        attach_z = height * rng.uniform(0.4, 0.55)
        ox = side * (trunk_r + 0.12)
        parts.append(
            stem_cyl(
                f"arm_{i}",
                (ox, rng.uniform(-0.05, 0.05), attach_z + arm_h * 0.35),
                trunk_r * 0.45,
                arm_h,
                mat,
                "saguaro_skin",
                verts=10,
                rot=(0, math.radians(side * -12), 0),
            )
        )

    def cols(parent):
        cylinder_collider(
            "trunk", (0, 0, height / 2), trunk_r * 1.15, height, parent, verts=10
        )
        for i in range(arms):
            side = -1 if i % 2 == 0 else 1
            arm_h = height * 0.35
            attach_z = height * 0.45
            ox = side * (trunk_r + 0.12)
            cylinder_collider(
                f"arm{i}",
                (ox, 0, attach_z + arm_h * 0.35),
                trunk_r * 0.5,
                arm_h,
                parent,
                verts=8,
            )

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


def build_ocotillo(name: str, height: float, stems: int, seed: int):
    clear_scene()
    mat = get_bark_mat()
    rng = random.Random(seed)
    parts = []
    for i in range(stems):
        ang = (i / stems) * math.tau + rng.uniform(-0.1, 0.1)
        rad = rng.uniform(0.05, 0.22)
        ox = math.cos(ang) * rad
        oy = math.sin(ang) * rad
        h = height * rng.uniform(0.75, 1.05)
        lean = math.radians(rng.uniform(-8, 8))
        parts.append(
            stem_cyl(
                f"stem_{i}",
                (ox, oy, h / 2),
                0.018,
                h,
                mat,
                "ocotillo_stem",
                verts=6,
                rot=(lean, 0, ang),
            )
        )

    def cols(parent):
        cylinder_collider("clump", (0, 0, height / 2), 0.28, height, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


def build_desert_tree(name: str, height: float, canopy: float, seed: int):
    clear_scene()
    bark = get_bark_mat()
    leaf = get_foliage_mat()
    rng = random.Random(seed)
    parts = []
    trunk_h = height * 0.55
    trunk_r = 0.08 + height * 0.015
    parts.append(
        stem_cyl(
            "trunk",
            (0, 0, trunk_h / 2),
            trunk_r,
            trunk_h,
            bark,
            "creosote_bark",
            verts=10,
        )
    )
    for i, side in enumerate((-1, 1, 0.3)):
        bh = height * 0.25
        parts.append(
            stem_cyl(
                f"branch_{i}",
                (side * 0.2, rng.uniform(-0.1, 0.1), trunk_h + bh * 0.3),
                trunk_r * 0.45,
                bh,
                bark,
                "creosote_bark",
                verts=8,
                rot=(0, math.radians(side * -25), 0),
            )
        )
    # 3 canopy silhouettes only (was 6+ quads) — big overdraw win
    for i in range(3):
        ang = i * (math.tau / 3)
        rot = (math.radians(90), 0, ang)
        parts.append(
            foliage_silhouette(
                f"canopy_{i}",
                (0, 0, height * 0.78),
                (canopy * 0.75, canopy * 0.55),
                rot,
                leaf,
                "creosote_leaf",
                shape="branch",
            )
        )

    def cols(parent):
        cylinder_collider("trunk", (0, 0, trunk_h / 2), trunk_r * 1.3, trunk_h, parent, verts=8)
        cylinder_collider(
            "canopy",
            (0, 0, height * 0.78),
            canopy * 0.35,
            height * 0.35,
            parent,
            verts=8,
        )

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    if not ATLAS.exists():
        raise SystemExit("Missing vegetation atlas — run build_atlases.py first")

    OUT.mkdir(parents=True, exist_ok=True)
    print("=== Desert flora (silhouette foliage, single-sided) ===")

    build_creosote("creosote_small", height=0.9, spread=0.7, seed=11)
    build_creosote("creosote_med", height=1.4, spread=1.1, seed=22)
    build_creosote("creosote_large", height=1.9, spread=1.5, seed=33)
    build_dry_scrub("scrub_small", height=0.45, spread=0.55, seed=41)
    build_dry_scrub("scrub_med", height=0.7, spread=0.9, seed=42)

    build_saguaro("saguaro_small", height=2.2, arms=0, seed=51)
    build_saguaro("saguaro_tall", height=5.5, arms=0, seed=52)
    build_saguaro("saguaro_armed", height=4.8, arms=2, seed=53)
    build_saguaro("saguaro_multi", height=6.2, arms=3, seed=54)

    build_ocotillo("ocotillo_med", height=3.2, stems=7, seed=61)
    build_ocotillo("ocotillo_tall", height=4.5, stems=9, seed=62)

    build_desert_tree("mesquite_small", height=3.0, canopy=2.2, seed=71)
    build_desert_tree("mesquite_med", height=4.5, canopy=3.2, seed=72)
    build_desert_tree("mesquite_large", height=6.0, canopy=4.5, seed=73)

    print("DONE flora")


if __name__ == "__main__":
    main()
