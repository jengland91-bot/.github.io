#!/usr/bin/env python3
"""
Parker 400 — desert bushes & trees for BeamNG (TSStatic).

Uses vegetation atlas + Colmesh + LOD0/1/2.

  /tmp/blender-4.2.9-linux-x64/blender --background --python batch_export_flora.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
PROPS = ROOT.parent
sys.path.insert(0, str(PROPS / "_shared"))
from beamng_export import (  # noqa: E402
    apply_object,
    box_collider,
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


def get_veg_mat():
    name = "ParkerVegAtlas"
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
    bsdf.inputs["Roughness"].default_value = 0.85
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    # alpha for leaf cards — cutout look via clip if supported
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = 1.0
    mat.blend_method = "OPAQUE"
    if ORM.exists():
        tex_orm = nodes.new("ShaderNodeTexImage")
        tex_orm.image = load_image(ORM)
        tex_orm.location = (-600, -300)
        if tex_orm.image:
            try:
                tex_orm.image.colorspace_settings.name = "Non-Color"
            except Exception:
                pass
        mat["orm_map"] = ORM.name
    return mat


def uv_set_rect(obj, key: str):
    rect = LAYOUT["rects"][key]
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    u0, v0, u1, v1 = rect["u0"], rect["v0"], rect["u1"], rect["v1"]
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


def leaf_card(name, loc, size_xy, rot_euler, mat, atlas_key):
    """Single foliage card (plane). Crossed cards = cheap bush volume."""
    sx, sy = size_xy
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, 1.0)
    obj.rotation_euler = rot_euler
    apply_object(obj)
    # Stand upright: plane is XY; rotate so it faces outward (already set rot)
    obj.data.materials.append(mat)
    uv_set_rect(obj, atlas_key)
    return obj


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
            dest = out_dir / f.name
            dest.write_bytes(f.read_bytes())


# ---------------------------------------------------------------------------
# BUSHES — crossed leaf cards + short stem; capsule collider
# ---------------------------------------------------------------------------
def build_creosote(name: str, height: float, spread: float, seed: int):
    clear_scene()
    mat = get_veg_mat()
    rng = random.Random(seed)
    parts = []

    stem_h = height * 0.35
    stem_r = max(0.02, spread * 0.04)
    parts.append(
        stem_cyl("stem", (0, 0, stem_h / 2), stem_r, stem_h, mat, "creosote_bark", verts=8)
    )

    # Crossed cards at a few heights/angles
    n_cards = 6 if height < 1.2 else 8
    for i in range(n_cards):
        ang = (i / n_cards) * math.tau + rng.uniform(-0.2, 0.2)
        z = stem_h * 0.5 + (i % 3) * (height - stem_h) / 3 + rng.uniform(0, 0.05)
        cx = math.cos(ang) * spread * 0.15
        cy = math.sin(ang) * spread * 0.15
        card_w = spread * rng.uniform(0.7, 1.0)
        card_h = (height - stem_h) * rng.uniform(0.7, 1.05)
        # Vertical card facing outward
        rot = (math.radians(90), 0, ang + math.pi / 2)
        parts.append(
            leaf_card(
                f"leaf_{i}",
                (cx, cy, z + card_h * 0.35),
                (card_w, card_h),
                rot,
                mat,
                "creosote_leaf",
            )
        )
    # Extra horizontal-ish card for volume
    parts.append(
        leaf_card(
            "leaf_top",
            (0, 0, height * 0.75),
            (spread * 0.9, spread * 0.9),
            (math.radians(15), 0, rng.uniform(0, 1)),
            mat,
            "creosote_leaf",
        )
    )

    col_h = height * 0.85
    col_r = spread * 0.35

    def cols(parent):
        # One 8-sided capsule/cylinder — not the leaf cards
        cylinder_collider("bush", (0, 0, col_h / 2), col_r, col_h, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


def build_dry_scrub(name: str, height: float, spread: float, seed: int):
    clear_scene()
    mat = get_veg_mat()
    rng = random.Random(seed)
    parts = []
    # Low tumbleweed / scrub — mostly cards, tiny stem
    parts.append(
        stem_cyl(
            "stem",
            (0, 0, 0.04),
            0.025,
            0.08,
            mat,
            "ocotillo_stem",
            verts=6,
        )
    )
    for i in range(5):
        ang = i * (math.tau / 5) + rng.uniform(-0.15, 0.15)
        rot = (math.radians(90), 0, ang)
        parts.append(
            leaf_card(
                f"scrub_{i}",
                (0, 0, height * 0.45),
                (spread, height),
                rot,
                mat,
                "dry_bush",
            )
        )

    def cols(parent):
        cylinder_collider("scrub", (0, 0, height / 2), spread * 0.4, height, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


# ---------------------------------------------------------------------------
# SAGUARO — trunk (+ optional arms); 8–12 sided cylinder collider
# ---------------------------------------------------------------------------
def build_saguaro(name: str, height: float, arms: int, seed: int):
    clear_scene()
    mat = get_veg_mat()
    rng = random.Random(seed)
    parts = []
    trunk_r = 0.18 + height * 0.02
    # Slightly tapered look: two stacked cylinders
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
        # Horizontal stub then up — approximate with angled cylinder
        ox = side * (trunk_r + 0.12)
        arm = stem_cyl(
            f"arm_{i}",
            (ox, rng.uniform(-0.05, 0.05), attach_z + arm_h * 0.35),
            trunk_r * 0.45,
            arm_h,
            mat,
            "saguaro_skin",
            verts=10,
            rot=(0, math.radians(side * -12), 0),
        )
        parts.append(arm)

    def cols(parent):
        # Ultra-simple 8–12 sided cylinder around trunk (not visual ribs)
        cylinder_collider(
            "trunk",
            (0, 0, height / 2),
            trunk_r * 1.15,
            height,
            parent,
            verts=10,
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


# ---------------------------------------------------------------------------
# OCOTILLO — cluster of thin stems
# ---------------------------------------------------------------------------
def build_ocotillo(name: str, height: float, stems: int, seed: int):
    clear_scene()
    mat = get_veg_mat()
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
        # One thin cylinder cluster bound — single capsule for the clump
        cylinder_collider("clump", (0, 0, height / 2), 0.28, height, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, OUT / f"{name}.dae")
    copy_atlas(OUT)


# ---------------------------------------------------------------------------
# DESERT TREE (mesquite-ish) — trunk + canopy cards
# ---------------------------------------------------------------------------
def build_desert_tree(name: str, height: float, canopy: float, seed: int):
    clear_scene()
    mat = get_veg_mat()
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
            mat,
            "creosote_bark",
            verts=10,
        )
    )
    # Forked branches
    for i, side in enumerate((-1, 1, 0.3)):
        bh = height * 0.25
        parts.append(
            stem_cyl(
                f"branch_{i}",
                (side * 0.2, rng.uniform(-0.1, 0.1), trunk_h + bh * 0.3),
                trunk_r * 0.45,
                bh,
                mat,
                "creosote_bark",
                verts=8,
                rot=(0, math.radians(side * -25), 0),
            )
        )
    # Canopy cards
    for i in range(6):
        ang = i * (math.tau / 6)
        rot = (math.radians(90), 0, ang)
        parts.append(
            leaf_card(
                f"canopy_{i}",
                (0, 0, height * 0.78),
                (canopy, canopy * 0.7),
                rot,
                mat,
                "creosote_leaf",
            )
        )
    parts.append(
        leaf_card(
            "canopy_top",
            (0, 0, height * 0.9),
            (canopy * 0.85, canopy * 0.85),
            (math.radians(10), 0, 0.5),
            mat,
            "creosote_leaf",
        )
    )

    def cols(parent):
        cylinder_collider("trunk", (0, 0, trunk_h / 2), trunk_r * 1.3, trunk_h, parent, verts=8)
        # Soft canopy collider so vehicles clip foliage less harshly
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
    print("=== Desert flora (bushes & trees) ===")

    # Bushes
    build_creosote("creosote_small", height=0.9, spread=0.7, seed=11)
    build_creosote("creosote_med", height=1.4, spread=1.1, seed=22)
    build_creosote("creosote_large", height=1.9, spread=1.5, seed=33)
    build_dry_scrub("scrub_small", height=0.45, spread=0.55, seed=41)
    build_dry_scrub("scrub_med", height=0.7, spread=0.9, seed=42)

    # Cacti / trees
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
