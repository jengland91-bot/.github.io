"""
Rebuild high-priority Parker 400 props with dedicated BeamNG Colmesh-1 collision.

Run from repo:
  /tmp/blender-4.2.9-linux-x64/blender --background --python rebuild_with_collision.py

Creates proper base00 / start01 / Colmesh_*-1 hierarchy.
Collision shapes are ultra-simple (boxes / 8-sided cylinders), bevel-free.
Drive-through arch uses SEPARATE convex colliders for legs + header.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "_shared"))
from beamng_export import (  # noqa: E402
    apply_object,
    box_collider,
    clear_scene,
    cylinder_collider,
    export_dae,
    make_collision_mat,
    new_empty,
    wrap_beamng_hierarchy,
)

BLENDER = True

# Shared atlases (one material / one albedo bind for all signs; one for vegetation)
ATLAS_DIR = ROOT / "atlases"
SIGN_ATLAS = ATLAS_DIR / "sign_atlas_2048.png"
SIGN_ORM = ATLAS_DIR / "sign_orm_2048.png"
SIGN_LAYOUT_PATH = ATLAS_DIR / "sign_atlas_layout.json"
VEG_ATLAS = ATLAS_DIR / "vegetation_atlas_2048.png"
VEG_ORM = ATLAS_DIR / "vegetation_orm_2048.png"
VEG_LAYOUT_PATH = ATLAS_DIR / "vegetation_atlas_layout.json"

_SIGN_LAYOUT = None
_VEG_LAYOUT = None
_SIGN_MAT = None
_VEG_MAT = None


def reset_units():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "METERS"


def load_image(path: Path):
    path = Path(path)
    for img in bpy.data.images:
        if img.filepath and Path(bpy.path.abspath(img.filepath)) == path.resolve():
            return img
        if img.name == path.name:
            return img
    if path.exists():
        return bpy.data.images.load(str(path))
    return None


def load_sign_layout():
    global _SIGN_LAYOUT
    if _SIGN_LAYOUT is None:
        import json

        _SIGN_LAYOUT = json.loads(SIGN_LAYOUT_PATH.read_text())
    return _SIGN_LAYOUT


def load_veg_layout():
    global _VEG_LAYOUT
    if _VEG_LAYOUT is None:
        import json

        _VEG_LAYOUT = json.loads(VEG_LAYOUT_PATH.read_text())
    return _VEG_LAYOUT


def make_orm_atlas_mat(name: str, albedo: Path, orm: Path):
    """
    Shared atlas material for Collada export.

    Collada only reliably exports Image Texture → Principled Base Color.
    Albedo atlas is bound for draw-call batching; ORM PNG is copied beside
    the DAE for manual PBR wiring (R=AO G=Roughness B=Metallic).
    """
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_alb = nodes.new("ShaderNodeTexImage")
    tex_alb.image = load_image(albedo)
    tex_alb.interpolation = "Closest"
    # Direct link required for Blender Collada texture export
    links.new(tex_alb.outputs["Color"], bsdf.inputs["Base Color"])

    # Sensible scalars if ORM isn't wired in-engine yet
    bsdf.inputs["Roughness"].default_value = 0.65
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.05

    # Keep ORM image loaded/packed so it ships with use_texture_copies when referenced
    # via a custom property path (and for artists opening the .blend later).
    if Path(orm).exists():
        orm_img = load_image(orm)
        mat["orm_map"] = Path(orm).name
        # Secondary unused texture node — some exporters skip it; file is still copied by us
        tex_orm = nodes.new("ShaderNodeTexImage")
        tex_orm.image = orm_img
        tex_orm.interpolation = "Linear"
        tex_orm.location = (-600, -300)
        if orm_img:
            try:
                orm_img.colorspace_settings.name = "Non-Color"
            except Exception:
                pass

    return mat


def get_sign_atlas_mat():
    global _SIGN_MAT
    if _SIGN_MAT is None:
        _SIGN_MAT = make_orm_atlas_mat("ParkerSignAtlas", SIGN_ATLAS, SIGN_ORM)
    return _SIGN_MAT


def get_veg_atlas_mat():
    global _VEG_MAT
    if _VEG_MAT is None:
        _VEG_MAT = make_orm_atlas_mat("ParkerVegAtlas", VEG_ATLAS, VEG_ORM)
    return _VEG_MAT


def uv_set_rect(obj, rect: dict):
    """Map every face of obj into the atlas UV rectangle."""
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
        else:
            for i, li in enumerate(idxs):
                t = i / max(1, len(idxs) - 1)
                uv[li].uv = (u0 + (u1 - u0) * t, v0 + (v1 - v0) * (i % 2))


def copy_atlas_set(out_dir: Path, kind: str):
    """Copy albedo + ORM into the DAE folder so BeamNG finds textures beside the mesh."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if kind == "sign":
        files = (SIGN_ATLAS, SIGN_ORM)
    else:
        files = (VEG_ATLAS, VEG_ORM)
    for f in files:
        if f.exists():
            dest = out_dir / f.name
            if not dest.exists() or dest.stat().st_size != f.stat().st_size:
                dest.write_bytes(f.read_bytes())


def make_mat(name, color, roughness=0.7, metallic=0.0, image_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path:
        p = Path(image_path)
        if p.exists():
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = load_image(p)
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def uv_smart(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)


def mesh_box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    apply_object(obj)
    obj.data.materials.append(mat)
    uv_smart(obj)
    return obj


def mesh_cyl(name, loc, radius, depth, mat, verts=16, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rot
    apply_object(obj)
    obj.data.materials.append(mat)
    uv_smart(obj)
    return obj


# ---------------------------------------------------------------------------
# K-RAILS — simple visual + bevel-free box collider
# ---------------------------------------------------------------------------
def build_krail(out_dir: Path, tex: Path, length: float, name: str):
    clear_scene()
    mat = make_mat("krail_vis", (0.65, 0.64, 0.6), 0.85, 0.0, tex)
    # Simplified visual jersey profile as a single box (visual can be slightly detailed later)
    # Use a tapered look with 2 stacked boxes for silhouette, but ONE smooth box collider
    base = mesh_box("krail_base", (0, length / 2, 0.04), (0.61, length, 0.08), mat)
    mid = mesh_box("krail_mid", (0, length / 2, 0.30), (0.36, length, 0.44), mat)
    top = mesh_box("krail_top", (0, length / 2, 0.63), (0.18, length, 0.22), mat)

    def cols(parent):
        # ONE bevel-free box covering the whole barrier (slightly inset so visuals show)
        box_collider("krail", (0, length / 2, 0.40), (0.58, length * 0.98, 0.80), parent)

    root = wrap_beamng_hierarchy([base, mid, top], [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")
    # ensure texture copied if present
    if tex.exists():
        (out_dir / tex.name).write_bytes(tex.read_bytes())


# ---------------------------------------------------------------------------
# TIRE STACKS — cylinder collider
# ---------------------------------------------------------------------------
def build_tire_stack(out_dir: Path, count: int, name: str):
    clear_scene()
    rubber = make_mat(
        "tire",
        (0.08, 0.08, 0.08),
        0.9,
        0.0,
        ROOT / "tire-stacks" / "textures" / "tire_rubber.png",
    )
    rim = make_mat(
        "rim",
        (0.4, 0.4, 0.42),
        0.4,
        0.6,
        ROOT / "tire-stacks" / "textures" / "tire_rim.png",
    )
    parts = []
    th, tr = 0.24, 0.36
    for i in range(count):
        z = i * th * 0.92 + th / 2
        bpy.ops.mesh.primitive_torus_add(
            major_radius=tr - 0.06,
            minor_radius=0.08,
            major_segments=20,
            minor_segments=8,
            location=(0, 0, z),
        )
        t = bpy.context.active_object
        t.name = f"tire_{i}"
        t.scale = (1, 1, (th * 0.45) / 0.08)
        apply_object(t)
        t.data.materials.append(rubber)
        parts.append(t)
        r = mesh_cyl(f"rim_{i}", (0, 0, z), tr - 0.14, 0.04, rim, verts=12)
        parts.append(r)

    total_h = count * th * 0.92

    def cols(parent):
        # Single capsule/cylinder around the stack — no bevels, 8 sides
        cylinder_collider("stack", (0, 0, total_h / 2), tr + 0.02, total_h, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# HAY BALES — box collider
# ---------------------------------------------------------------------------
def build_hay(out_dir: Path, name: str, kind: str, tex_name: str = "hay_gold.png"):
    clear_scene()
    tex = ROOT / "hay-bales" / "textures" / tex_name
    mat = make_mat("hay", (0.8, 0.7, 0.3), 0.95, 0.0, tex)
    parts = []
    colliders = []
    sx, sy, sz = 1.0, 0.45, 0.35

    if kind == "rect":
        parts.append(mesh_box("bale", (0, 0, sz / 2), (sx, sy, sz), mat))

        def cols(parent):
            box_collider("bale", (0, 0, sz / 2), (sx, sy, sz), parent)

        colliders = [cols]
    elif kind == "stack2":
        parts.append(mesh_box("bale0", (0, 0, sz / 2), (sx, sy, sz), mat))
        parts.append(mesh_box("bale1", (0, 0, sz + sz / 2), (sx, sy, sz), mat))

        def cols(parent):
            box_collider("stack", (0, 0, sz), (sx, sy, sz * 2), parent)

        colliders = [cols]
    elif kind == "stack3":
        for i in range(3):
            parts.append(mesh_box(f"bale{i}", (0, 0, i * sz + sz / 2), (sx, sy, sz), mat))

        def cols(parent):
            box_collider("stack", (0, 0, sz * 1.5), (sx, sy, sz * 3), parent)

        colliders = [cols]
    elif kind == "wall4":
        # 2 wide x 2 tall — single smooth box collider (no snag seams)
        for ix, x in enumerate((-sx / 2, sx / 2)):
            for iz in range(2):
                parts.append(
                    mesh_box(f"bale_{ix}_{iz}", (x, 0, iz * sz + sz / 2), (sx, sy, sz), mat)
                )

        def cols(parent):
            box_collider("wall", (0, 0, sz), (sx * 2, sy, sz * 2), parent)

        colliders = [cols]
    elif kind == "round":
        r, d = 0.75, 1.2
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16, radius=r, depth=d, location=(0, 0, r)
        )
        obj = bpy.context.active_object
        obj.rotation_euler[0] = math.radians(90)
        apply_object(obj)
        min_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
        obj.location.z -= min_z
        obj.data.materials.append(mat)
        parts.append(obj)

        def cols(parent):
            # approximate as box for sliding stability
            box_collider("round", (0, 0, r), (d, r * 2, r * 2), parent)

        colliders = [cols]
    else:
        return

    root = wrap_beamng_hierarchy(parts, colliders, f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")
    if tex.exists():
        (out_dir / tex.name).write_bytes(tex.read_bytes())


# ---------------------------------------------------------------------------
# TIRE ROW — one low cylinder per tire (convex, no cavities)
# ---------------------------------------------------------------------------
def build_tire_row(out_dir: Path, count: int, name: str):
    clear_scene()
    rubber = make_mat(
        "tire",
        (0.08, 0.08, 0.08),
        0.9,
        0.0,
        ROOT / "tire-stacks" / "textures" / "tire_rubber.png",
    )
    rim = make_mat(
        "rim",
        (0.4, 0.4, 0.42),
        0.4,
        0.6,
        ROOT / "tire-stacks" / "textures" / "tire_rim.png",
    )
    parts = []
    th, tr = 0.24, 0.36
    spacing = tr * 2.05
    for i in range(count):
        x = (i - (count - 1) / 2) * spacing
        z = th / 2
        bpy.ops.mesh.primitive_torus_add(
            major_radius=tr - 0.06,
            minor_radius=0.08,
            major_segments=20,
            minor_segments=8,
            location=(x, 0, z),
        )
        t = bpy.context.active_object
        t.name = f"tire_{i}"
        t.scale = (1, 1, (th * 0.45) / 0.08)
        apply_object(t)
        t.data.materials.append(rubber)
        parts.append(t)
        parts.append(mesh_cyl(f"rim_{i}", (x, 0, z), tr - 0.14, 0.04, rim, verts=12))

    def cols(parent):
        # One 8-sided cylinder per tire — bevel-free so bumpers slide
        for i in range(count):
            x = (i - (count - 1) / 2) * spacing
            cylinder_collider(f"t{i}", (x, 0, th / 2), tr + 0.02, th, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# ROCKS — vegetation atlas tile + simple cylinder collider
# ---------------------------------------------------------------------------
def build_rock(out_dir: Path, name: str, tex_name: str, scale, seed: int):
    clear_scene()
    key = tex_name.replace(".png", "")
    layout = load_veg_layout()["rects"]
    rect = layout.get(key) or layout.get("rock_tan")
    mat = get_veg_atlas_mat()

    rng = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.5, location=(0, 0, 0.5))
    rock = bpy.context.active_object
    rock.scale = scale
    apply_object(rock)
    for v in rock.data.vertices:
        nrm = v.co.normalized() if v.co.length > 1e-6 else Vector((0, 0, 1))
        noise = rng.uniform(-0.08, 0.12)
        v.co += nrm * noise * 0.4
        if v.co.z < 0.02:
            v.co.z = 0.02
    rock.data.update()
    min_z = min(v.co.z for v in rock.data.vertices)
    rock.location.z -= min_z
    rock.data.materials.clear()
    rock.data.materials.append(mat)
    uv_set_rect(rock, rect)

    rx, ry, rz = scale
    rad = max(rx, ry) * 0.45
    height = rz * 0.95

    def cols(parent):
        cylinder_collider("rock", (0, 0, height / 2), rad, height, parent, verts=8)

    root = wrap_beamng_hierarchy([rock], [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")
    copy_atlas_set(out_dir, "veg")


# ---------------------------------------------------------------------------
# ARCH — split convex colliders (drive-through)
# ---------------------------------------------------------------------------
def build_arch(out_dir: Path, name: str):
    clear_scene()
    tube_tex = ROOT / "arch-gate" / "textures" / "arch_tube.png"
    block_tex = ROOT / "arch-gate" / "textures" / "arch_block.png"
    logo_tex = ROOT / "arch-gate" / "textures" / "arch_logo.png"
    tube_m = make_mat("tube", (0.9, 0.9, 0.9), 0.5, 0.0, tube_tex)
    block_m = make_mat("block", (0.7, 0.7, 0.7), 0.55, 0.0, block_tex)
    logo_m = make_mat("logo", (0.5, 0.5, 0.5), 0.45, 0.0, logo_tex)

    clear_w, clear_h, tube_r = 7.0, 4.6, 0.55
    block_w, block_h, block_d = 3.2, 1.35, 0.85
    half_w = clear_w / 2 + tube_r
    leg_top = clear_h + tube_r * 0.3
    block_z = clear_h + block_h / 2 + 0.15
    parts = []

    for side, sx in (("L", -half_w), ("R", half_w)):
        leg = mesh_cyl(f"leg_{side}", (sx, 0, leg_top / 2), tube_r, leg_top, tube_m, verts=14)
        parts.append(leg)
        foot = mesh_cyl(f"foot_{side}", (sx, 0, 0.06), tube_r * 1.3, 0.12, tube_m, verts=14)
        parts.append(foot)

    # angled arms approximated as boxes for visual simplicity in rebuild
    for side, sx in (("L", -1), ("R", 1)):
        arm = mesh_box(
            f"arm_{side}",
            (sx * (half_w + block_w / 2) / 2, 0, (leg_top + block_z) / 2),
            (abs(half_w - block_w / 2) * 0.9, tube_r * 1.6, tube_r * 1.6),
            tube_m,
        )
        parts.append(arm)

    block = mesh_box("block", (0, 0, block_z), (block_w, block_d, block_h), block_m)
    parts.append(block)
    for i, y in enumerate((-block_d / 2 - 0.02, block_d / 2 + 0.02)):
        plate = mesh_box(
            f"logo_{i}",
            (0, y, block_z),
            (block_w * 0.88, 0.025, block_h * 0.72),
            logo_m,
        )
        parts.append(plate)

    def cols(parent):
        # LEFT LEG — convex cylinder/box
        box_collider(
            "legL",
            (-half_w, 0, leg_top / 2),
            (tube_r * 2.1, tube_r * 2.1, leg_top),
            parent,
        )
        # RIGHT LEG
        box_collider(
            "legR",
            (half_w, 0, leg_top / 2),
            (tube_r * 2.1, tube_r * 2.1, leg_top),
            parent,
        )
        # HEADER / center block only — leaves the drive-through opening empty
        box_collider(
            "header",
            (0, 0, block_z),
            (block_w + tube_r * 2.5, max(block_d, tube_r * 2.2), block_h + tube_r),
            parent,
        )

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")
    for t in (tube_tex, block_tex, logo_tex):
        if t.exists():
            (out_dir / t.name).write_bytes(t.read_bytes())


# ---------------------------------------------------------------------------
# FENCE / NETTING — thin box collider (panel)
# ---------------------------------------------------------------------------
def build_fence_panel(out_dir: Path, name: str, width: float, height: float, tex: Path, kind: str):
    clear_scene()
    mat = make_mat("fence", (0.4, 0.4, 0.4), 0.6, 0.3, tex)
    post_m = make_mat("post", (0.3, 0.3, 0.3), 0.4, 0.7)
    parts = []
    for i, x in enumerate((0.04, width - 0.04)):
        parts.append(mesh_cyl(f"post_{i}", (x, 0, height / 2), 0.04, height + 0.1, post_m, verts=8))
    mesh = mesh_box("mesh", (width / 2, 0, height / 2), (width - 0.12, 0.02, height * 0.92), mat)
    parts.append(mesh)

    def cols(parent):
        # Thin wall box — vehicles bounce off, low face count
        box_collider("panel", (width / 2, 0, height / 2), (width, 0.08, height), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")
    if tex.exists():
        (out_dir / tex.name).write_bytes(tex.read_bytes())


# ---------------------------------------------------------------------------
# PORTA-POTTY — single box
# ---------------------------------------------------------------------------
def build_porta(out_dir: Path, name: str, body_tex: Path, door_tex: Path):
    clear_scene()
    W, D, H = 1.1, 1.15, 2.3
    body_m = make_mat("body", (0.25, 0.4, 0.65), 0.55, 0.0, body_tex)
    door_m = make_mat("door", (0.25, 0.4, 0.65), 0.55, 0.0, door_tex)
    roof_m = make_mat("roof", (0.15, 0.15, 0.15), 0.6, 0.0, ROOT / "porta-potties" / "textures" / "pp_roof.png")
    parts = [
        mesh_box("body", (0, 0, H / 2), (W, D, H), body_m),
        mesh_box("door", (0, -D / 2 - 0.02, H * 0.48), (W * 0.72, 0.04, H * 0.78), door_m),
        mesh_box("roof", (0, 0, H + 0.04), (W * 1.06, D * 1.06, 0.08), roof_m),
    ]

    def cols(parent):
        box_collider("potty", (0, 0, H / 2), (W, D, H), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# TENT — separate pole + roof colliders (opening underneath for walking)
# ---------------------------------------------------------------------------
def build_tent(out_dir: Path, name: str, size_xy, height: float, fabric_tex: Path):
    clear_scene()
    sx, sy = size_xy
    hx, hy = sx / 2, sy / 2
    eave = height * 0.78
    fab = make_mat("fab", (0.9, 0.9, 0.9), 0.8, 0.0, fabric_tex)
    pole_m = make_mat("pole", (0.2, 0.2, 0.2), 0.35, 0.7)
    parts = []
    corners = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    for i, (x, y) in enumerate(corners):
        parts.append(mesh_cyl(f"pole_{i}", (x, y, eave / 2), 0.03, eave, pole_m, verts=8))
    # roof as flat-ish box at eave height
    parts.append(mesh_box("roof", (0, 0, (eave + height) / 2), (sx * 1.02, sy * 1.02, 0.08), fab))

    def cols(parent):
        # Four thin pole boxes + roof slab — open under canopy
        for i, (x, y) in enumerate(corners):
            box_collider(f"pole{i}", (x, y, eave / 2), (0.08, 0.08, eave), parent)
        box_collider("roof", (0, 0, (eave + height) / 2), (sx * 1.02, sy * 1.02, 0.12), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# LIGHT TOWER — body box + mast cylinder
# ---------------------------------------------------------------------------
def build_lighttower(out_dir: Path, name: str, mast_h: float, body_tex: Path | None = None):
    clear_scene()
    if body_tex is None:
        body_tex = ROOT / "light-towers" / "textures" / "lt_body.png"
    body_m = make_mat("body", (0.85, 0.85, 0.84), 0.55, 0.05, body_tex)
    black_m = make_mat("black", (0.1, 0.1, 0.1), 0.4, 0.7)
    lens_m = make_mat("lens", (1, 0.95, 0.8), 0.2, 0.0, ROOT / "light-towers" / "textures" / "lt_lens.png")
    parts = [
        mesh_box("chassis", (0, 0.6, 0.18), (1.05, 2.3, 0.12), black_m),
        mesh_box("body", (0, 0.75, 0.75), (1.0, 1.7, 1.05), body_m),
        mesh_box("tongue", (0, -1.15, 0.28), (0.12, 1.1, 0.08), black_m),
        mesh_box("mast", (0, -0.15, 1.35 + mast_h / 2), (0.12, 0.12, mast_h), black_m),
        mesh_box("bar", (0, -0.15, 1.35 + mast_h * 0.95), (1.6, 0.08, 0.08), black_m),
    ]
    for i, x in enumerate((-0.45, 0.45, -0.45, 0.45)):
        y = -0.15 if i < 2 else -0.35
        z = 1.35 + mast_h * 0.95 + 0.2
        parts.append(mesh_box(f"light_{i}", (x, y, z), (0.35, 0.18, 0.28), black_m))
        parts.append(mesh_box(f"lens_{i}", (x, y - 0.1, z), (0.3, 0.03, 0.24), lens_m))

    def cols(parent):
        box_collider("body", (0, 0.7, 0.7), (1.05, 2.0, 1.3), parent)
        # mast as thin box (8-face cylinder approx via box is fine for snag-free)
        box_collider("mast", (0, -0.15, 1.35 + mast_h / 2), (0.18, 0.18, mast_h), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# SIGNS / MILE MARKERS — shared sign atlas (one material / one draw texture)
# ---------------------------------------------------------------------------
def build_signpost(
    out_dir: Path,
    name: str,
    atlas_key: str,
    post_h=1.55,
    sign_w=0.38,
    sign_h=0.62,
):
    """Portrait race plates (taller than wide) — matches BITD-style markers."""
    clear_scene()
    layout = load_sign_layout()["rects"]
    mat = get_sign_atlas_mat()
    wood_rect = layout.get("post_wood")
    sign_rect = layout.get(atlas_key)
    if sign_rect is None:
        print(f"WARNING: no atlas rect for {atlas_key}, skipping")
        return

    # Sign center height on post
    sign_z = post_h * 0.72
    post = mesh_box("post", (0, 0, post_h / 2), (0.1, 0.1, post_h), mat)
    sign = mesh_box("sign", (0, -0.08, sign_z), (sign_w, 0.03, sign_h), mat)
    if wood_rect:
        uv_set_rect(post, wood_rect)
    uv_set_rect(sign, sign_rect)
    parts = [post, sign]

    def cols(parent):
        cylinder_collider("post", (0, 0, post_h / 2), 0.06, post_h, parent, verts=8)
        box_collider("sign", (0, -0.08, sign_z), (sign_w, 0.05, sign_h), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")
    copy_atlas_set(out_dir, "sign")


# ---------------------------------------------------------------------------
# FEATHER FLAG — thin pole cylinder (cloth usually non-colliding / decorative)
# ---------------------------------------------------------------------------
def build_feather_flag(out_dir: Path, name: str, flag_tex: Path):
    clear_scene()
    pole_m = make_mat("pole", (0.75, 0.75, 0.78), 0.35, 0.7, ROOT / "feather-flags" / "textures" / "flag_pole.png")
    flag_m = make_mat("flag", (0.9, 0.4, 0.1), 0.7, 0.0, flag_tex)
    pole_h = 4.2
    parts = [
        mesh_cyl("pole", (0, 0, pole_h / 2), 0.035, pole_h, pole_m, verts=10),
        mesh_box("flag", (0.35, 0, pole_h * 0.62), (0.7, 0.02, 2.2), flag_m),
    ]

    def cols(parent):
        # Pole only — soft flag should not snag vehicles
        cylinder_collider("pole", (0, 0, pole_h / 2), 0.045, pole_h, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# PIT MAT — thin ground box (optional low collision)
# ---------------------------------------------------------------------------
def build_mat(out_dir: Path, name: str, size_xy, tex: Path):
    clear_scene()
    sx, sy = size_xy
    mat = make_mat("mat", (0.2, 0.2, 0.2), 0.9, 0.0, tex)
    th = 0.03
    parts = [mesh_box("mat", (0, 0, th / 2), (sx, sy, th), mat)]

    def cols(parent):
        box_collider("mat", (0, 0, th / 2), (sx, sy, th), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


# ---------------------------------------------------------------------------
# SINGLE STAKE / POST — thin cylinder
# ---------------------------------------------------------------------------
def build_stake(out_dir: Path, name: str, height=1.05, radius=0.035, tex: Path | None = None):
    clear_scene()
    mat = make_mat("stake", (0.4, 0.35, 0.3), 0.6, 0.2, tex)
    parts = [mesh_cyl("stake", (0, 0, height / 2), radius, height, mat, verts=8)]

    def cols(parent):
        cylinder_collider("stake", (0, 0, height / 2), radius + 0.01, height, parent, verts=8)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


def build_porta_double(out_dir: Path, name: str, body_tex: Path, door_tex: Path):
    clear_scene()
    W, D, H = 1.1, 1.15, 2.3
    gap = 0.08
    body_m = make_mat("body", (0.25, 0.4, 0.65), 0.55, 0.0, body_tex)
    door_m = make_mat("door", (0.25, 0.4, 0.65), 0.55, 0.0, door_tex)
    roof_m = make_mat("roof", (0.15, 0.15, 0.15), 0.6, 0.0, ROOT / "porta-potties" / "textures" / "pp_roof.png")
    parts = []
    for i, x in enumerate((-W / 2 - gap / 2, W / 2 + gap / 2)):
        parts.append(mesh_box(f"body_{i}", (x, 0, H / 2), (W, D, H), body_m))
        parts.append(mesh_box(f"door_{i}", (x, -D / 2 - 0.02, H * 0.48), (W * 0.72, 0.04, H * 0.78), door_m))
        parts.append(mesh_box(f"roof_{i}", (x, 0, H + 0.04), (W * 1.06, D * 1.06, 0.08), roof_m))

    def cols(parent):
        # One convex box covering both units (no cavity between)
        box_collider("double", (0, 0, H / 2), (W * 2 + gap, D, H), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


def build_chainlink_gate(out_dir: Path, name: str):
    clear_scene()
    tex = ROOT / "chainlink" / "textures" / "chainlink.png"
    mat = make_mat("fence", (0.4, 0.4, 0.4), 0.6, 0.3, tex)
    post_m = make_mat("post", (0.3, 0.3, 0.3), 0.4, 0.7)
    w, h = 1.0, 1.8
    parts = [
        mesh_cyl("postL", (0.04, 0, h / 2), 0.04, h + 0.1, post_m, verts=8),
        mesh_cyl("postR", (w - 0.04, 0, h / 2), 0.04, h + 0.1, post_m, verts=8),
        mesh_box("mesh", (w / 2, 0, h / 2), (w - 0.12, 0.02, h * 0.92), mat),
    ]

    def cols(parent):
        box_collider("gate", (w / 2, 0, h / 2), (w, 0.08, h), parent)

    root = wrap_beamng_hierarchy(parts, [cols], f"{name}_a800")
    export_dae(root, out_dir / f"{name}.dae")


def main():
    global _SIGN_MAT, _VEG_MAT, _SIGN_LAYOUT, _VEG_LAYOUT
    bpy.ops.wm.read_factory_settings(use_empty=True)
    reset_units()
    _SIGN_MAT = _VEG_MAT = None
    _SIGN_LAYOUT = _VEG_LAYOUT = None

    if not SIGN_ATLAS.exists() or not VEG_ATLAS.exists():
        raise SystemExit(
            "Atlases missing — run: python3 beamng-props/build_atlases.py"
        )

    print("=== Rebuilding props with Colmesh + atlases + LODs ===")

    # K-rails — bevel-free single box colliders
    kdir = ROOT / "k-rails" / "export" / "dae"
    ktex = ROOT / "k-rails" / "textures"
    for length, label in ((2.0, "2m"), (3.0, "3m"), (6.0, "6m")):
        build_krail(kdir, ktex / "krail.png", length, f"krail_blank_{label}")
    for length, label in ((2.0, "2m"), (3.0, "3m")):
        build_krail(kdir, ktex / "krail_stripe.png", length, f"krail_stripe_{label}")
        build_krail(kdir, ktex / "krail_concrete.png", length, f"krail_concrete_{label}")
        build_krail(kdir, ktex / "krail_orange.png", length, f"krail_orange_{label}")
        build_krail(kdir, ktex / "krail_dark.png", length, f"krail_dark_{label}")
        if (ktex / "krail_white.png").exists():
            build_krail(kdir, ktex / "krail_white.png", length, f"krail_white_{label}")

    # Tires
    tdir = ROOT / "tire-stacks" / "export" / "dae"
    for n in range(1, 7):
        build_tire_stack(tdir, n, "tire_single" if n == 1 else f"tire_stack_{n}")
    build_tire_row(tdir, 3, "tire_row_3")

    # Hay
    hdir = ROOT / "hay-bales" / "export" / "dae"
    build_hay(hdir, "haybale_rect_gold", "rect", "hay_gold.png")
    build_hay(hdir, "haybale_rect_dry", "rect", "hay_dry.png")
    build_hay(hdir, "haybale_rect_green", "rect", "hay_green.png")
    build_hay(hdir, "haybale_stack_2", "stack2")
    build_hay(hdir, "haybale_stack_3", "stack3")
    build_hay(hdir, "haybale_wall_4", "wall4")
    build_hay(hdir, "haybale_round_gold", "round")

    # Rocks — 8-sided cylinder colliders
    rdir = ROOT / "rocks" / "export" / "dae"
    rock_jobs = [
        ("rock_small_tan_a", "rock_tan.png", (0.55, 0.45, 0.35), 11),
        ("rock_small_tan_b", "rock_tan.png", (0.5, 0.5, 0.32), 12),
        ("rock_small_red_a", "rock_red.png", (0.5, 0.42, 0.34), 13),
        ("rock_med_tan_a", "rock_tan.png", (1.4, 1.1, 0.85), 21),
        ("rock_med_tan_b", "rock_tan.png", (1.2, 1.3, 0.8), 22),
        ("rock_med_gray_a", "rock_gray.png", (1.3, 1.0, 0.90), 23),
        ("rock_med_red_a", "rock_red.png", (1.25, 1.05, 0.88), 24),
        ("rock_large_tan_a", "rock_tan.png", (3.2, 2.4, 1.8), 31),
        ("rock_large_gray_a", "rock_gray.png", (3.0, 2.5, 1.9), 32),
        ("rock_large_dark_a", "rock_dark.png", (3.5, 2.6, 2.2), 33),
        ("rock_boulder_tan", "rock_tan.png", (5.0, 4.2, 3.0), 41),
        ("rock_boulder_red", "rock_red.png", (4.8, 4.0, 2.9), 42),
    ]
    for name, texn, scale, seed in rock_jobs:
        tex = ROOT / "rocks" / "textures" / texn
        if tex.exists():
            build_rock(rdir, name, texn, scale, seed)

    # Arch — drive-through split collision
    adir = ROOT / "arch-gate" / "export" / "dae"
    build_arch(adir, "arch_blank")
    # Presets are texture-swap copies of the blank DAE (same Colmesh split)
    blank = (adir / "arch_blank.dae").read_bytes()
    for preset in (
        "arch_preset_orange_black.dae",
        "arch_preset_white_navyish.dae",
        "arch_preset_yellow_black.dae",
    ):
        (adir / preset).write_bytes(blank)

    # Chainlink + safety netting
    cdir = ROOT / "chainlink" / "export" / "dae"
    cl = ROOT / "chainlink" / "textures"
    for w, label in ((2.0, "2m"), (3.0, "3m"), (6.0, "6m")):
        build_fence_panel(cdir, f"chainlink_{label}", w, 1.8, cl / "chainlink.png", "cl")
    build_fence_panel(cdir, "chainlink_tall_3m", 3.0, 2.4, cl / "chainlink.png", "cl")
    if (cl / "chainlink_dark.png").exists():
        build_fence_panel(cdir, "chainlink_dark_3m", 3.0, 1.8, cl / "chainlink_dark.png", "cl")
    if (cl / "chainlink_green.png").exists():
        build_fence_panel(cdir, "chainlink_green_3m", 3.0, 1.8, cl / "chainlink_green.png", "cl")
    build_chainlink_gate(cdir, "chainlink_gate_1m")
    build_stake(cdir, "chainlink_post", height=1.9, radius=0.045, tex=cl / "fence_post.png")

    ndir = ROOT / "safety-netting" / "export" / "dae"
    net = ROOT / "safety-netting" / "textures" / "safety_orange.png"
    for w, label in ((2.0, "2m"), (3.0, "3m"), (5.0, "5m")):
        build_fence_panel(ndir, f"safetynet_orange_{label}", w, 1.1, net, "net")
    build_fence_panel(ndir, "safetynet_orange_tall_3m", 3.0, 1.6, net, "net")
    build_fence_panel(ndir, "safetynet_orange_wood_3m", 3.0, 1.1, net, "net")
    yel = ROOT / "safety-netting" / "textures" / "safety_yellow.png"
    if yel.exists():
        build_fence_panel(ndir, "safetynet_yellow_3m", 3.0, 1.1, yel, "net")

    # Barriers
    bdir = ROOT / "barriers" / "export" / "dae"
    btex = ROOT / "barriers" / "textures"
    build_fence_panel(bdir, "snowfence_orange_2m", 2.0, 1.05, btex / "snowfence_orange.png", "sf")
    if (btex / "snowfence_wood.png").exists():
        build_fence_panel(bdir, "snowfence_wood_1m", 1.0, 1.05, btex / "snowfence_wood.png", "sf")
        build_fence_panel(bdir, "snowfence_wood_2m", 2.0, 1.05, btex / "snowfence_wood.png", "sf")
    for rib, base in (
        ("ribbon_caution.png", "ribbon_caution"),
        ("ribbon_orange.png", "ribbon_orange"),
        ("ribbon_yellow_black.png", "ribbon_yellow"),
    ):
        rp = btex / rib
        if not rp.exists():
            continue
        for w, lab in ((2.0, "2m"), (3.0, "3m"), (5.0, "5m")):
            build_fence_panel(bdir, f"{base}_{lab}", w, 1.0, rp, "rib")
            build_fence_panel(bdir, f"stake_{base}_{lab}", w, 1.0, rp, "rib")
    build_stake(bdir, "stake_wood", height=1.1, radius=0.04, tex=btex / "stake_wood.png")
    build_stake(bdir, "stake_metal", height=1.1, radius=0.035, tex=btex / "stake_metal.png")

    # Porta
    pdir = ROOT / "porta-potties" / "export" / "dae"
    ptex = ROOT / "porta-potties" / "textures"
    for color, body, door in (
        ("blank", "pp_body.png", "pp_door.png"),
        ("blue", "pp_body_blue.png", "pp_door_blue.png"),
        ("gray", "pp_body_gray.png", "pp_door_gray.png"),
        ("green", "pp_body_green.png", "pp_door_green.png"),
        ("orange", "pp_body_orange.png", "pp_door_orange.png"),
        ("white", "pp_body_white.png", "pp_door_white.png"),
    ):
        bp, dp = ptex / body, ptex / door
        if bp.exists() and dp.exists():
            build_porta(pdir, f"portapotty_{color}", bp, dp)
    build_porta_double(pdir, "portapotty_double_blue", ptex / "pp_body_blue.png", ptex / "pp_door_blue.png")

    # Tents — poles + roof (open under canopy)
    tndir = ROOT / "tents" / "export" / "dae"
    ttex = ROOT / "tents" / "textures"
    for name, size, h, fab in (
        ("tent_blank_3x3", (3.0, 3.0), 2.4, "tent_fabric.png"),
        ("tent_blank_6x3", (6.0, 3.0), 2.6, "tent_fabric.png"),
        ("tent_orange_3x3", (3.0, 3.0), 2.4, "tent_fabric_orange.png"),
        ("tent_blue_3x3", (3.0, 3.0), 2.4, "tent_fabric_blue.png"),
        ("tent_white_3x3", (3.0, 3.0), 2.4, "tent_fabric_white.png"),
        ("tent_black_6x3", (6.0, 3.0), 2.6, "tent_fabric_black.png"),
    ):
        fp = ttex / fab
        if fp.exists():
            build_tent(tndir, name, size, h, fp)

    # Light towers
    ldir = ROOT / "light-towers" / "export" / "dae"
    lt = ROOT / "light-towers" / "textures"
    build_lighttower(ldir, "lighttower_blank_raised", 7.5)
    build_lighttower(ldir, "lighttower_blank_mid", 4.5)
    for cname, ctex in (
        ("lighttower_orange_raised", "lt_body_orange.png"),
        ("lighttower_white_raised", "lt_body_white.png"),
        ("lighttower_yellow_raised", "lt_body_yellow.png"),
    ):
        src = lt / ctex
        if src.exists():
            build_lighttower(ldir, cname, 7.5, body_tex=src)

    # Mile markers 1–100 — UV islands on shared sign atlas
    mdir = ROOT / "mile-marker" / "export" / "dae"
    for n in range(1, 101):
        key = f"mile_{n:03d}"
        if key in load_sign_layout()["rects"]:
            build_signpost(mdir, f"milemarker_{n:03d}", key)

    # Course / lap / exit signs — same ParkerSignAtlas material
    sdir = ROOT / "course-signs" / "export" / "dae"
    course_keys = [
        "arrow_straight",
        "arrow_slight_left",
        "arrow_slight_right",
        "arrow_turn_left",
        "arrow_turn_right",
        "arrow_double_left",
        "arrow_double_right",
        "arrow_triple_left",
        "arrow_triple_right",
        "turn_ahead",
        "wrong_way",
        "danger_x",
    ]
    rects = load_sign_layout()["rects"]
    for key in course_keys:
        if key in rects:
            build_signpost(sdir, key, key, post_h=1.65, sign_w=0.40, sign_h=0.68)
    if "wrong_way" in rects:
        build_signpost(sdir, "sign_wrong_way", "wrong_way", post_h=1.65, sign_w=0.40, sign_h=0.68)
    if "danger_x" in rects:
        build_signpost(sdir, "sign_danger_x", "danger_x", post_h=1.65, sign_w=0.40, sign_h=0.68)

    lps = ROOT / "lap-signs" / "export" / "dae"
    for n in range(1, 11):
        key = f"lap_{n:02d}"
        if key in rects:
            build_signpost(lps, f"lapsign_{n:02d}", key, post_h=1.5, sign_w=0.5, sign_h=0.4)

    pit = ROOT / "pits" / "export" / "dae"
    for ex in ("exit", "exit_left", "exit_right", "exit_up"):
        if ex in rects:
            build_signpost(pit, ex, ex, post_h=1.5, sign_w=0.7, sign_h=0.45)

    # Pit mats — thin ground boxes
    ptex = ROOT / "pits" / "textures"
    for name, size, texn in (
        ("mat_checkered_2x1", (2.0, 1.0), "mat_checkered.png"),
        ("mat_checkered_3x2", (3.0, 2.0), "mat_checkered.png"),
        ("mat_orange_trim_2x1", (2.0, 1.0), "mat_orange_trim.png"),
        ("mat_orange_trim_4x2", (4.0, 2.0), "mat_orange_trim.png"),
        ("mat_pitstall_3x2", (3.0, 2.0), "mat_pitstall.png"),
        ("mat_pitstall_4x2", (4.0, 2.0), "mat_pitstall.png"),
        ("mat_rubber_2x1", (2.0, 1.0), "mat_rubber.png"),
        ("mat_rubber_3x1_5", (3.0, 1.5), "mat_rubber.png"),
    ):
        tp = ptex / texn
        if tp.exists():
            build_mat(pit, name, size, tp)

    # Feather flags — pole collider only
    fdir = ROOT / "feather-flags" / "export" / "dae"
    ftex = ROOT / "feather-flags" / "textures"
    for color in ("orange", "black", "white", "navy"):
        fp = ftex / f"flag_blank_{color}.png"
        if fp.exists():
            build_feather_flag(fdir, f"featherflag_blank_{color}", fp)

    print("DONE: collision-enabled props rebuilt")


if __name__ == "__main__":
    main()
