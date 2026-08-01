"""
Portable towable light tower / light standard for BeamNG.
Raised mast with 4 floodlights. Blank body + logo for branding.

Run:
  blender --background --python batch_export_lights.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "light_towers.blend"

VARIANTS = {
    # name: body_tex, logo_tex, mast_height
    "lighttower_blank_raised": ("lt_body.png", "lt_logo.png", 7.5),
    "lighttower_white_raised": ("lt_body_white.png", "lt_logo.png", 7.5),
    "lighttower_yellow_raised": ("lt_body_yellow.png", "lt_logo.png", 7.5),
    "lighttower_orange_raised": ("lt_body_orange.png", "lt_logo.png", 7.5),
    "lighttower_blank_mid": ("lt_body.png", "lt_logo.png", 5.0),
}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "METERS"


def clear_all():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def load_image(path: Path):
    for img in bpy.data.images:
        if img.name == path.name:
            return img
    return bpy.data.images.load(str(path))


def make_mat(name, color, roughness=0.6, metallic=0.0, image_path=None):
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
    # Make lenses read as glowing
    if "Emission Color" in bsdf.inputs and "lens" in name.lower():
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.95, 0.8, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 12.0
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if "lens" in name.lower() and "Emission Color" in bsdf.inputs:
            links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    return mat


def apply_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def uv_smart(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)


def add_bevel(obj, width=0.01, segments=2):
    mod = obj.modifiers.new("Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(30)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)


def box(name, loc, scale, mat, bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    apply_object(obj)
    if bevel:
        add_bevel(obj, bevel, 2)
    obj.data.materials.append(mat)
    uv_smart(obj)
    return obj


def cyl(name, loc, radius, depth, mat, rot=(0, 0, 0), verts=12):
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


def build_tower(body_tex: str, logo_tex: str, mast_h: float):
    root = bpy.data.objects.new("lighttower_root", None)
    bpy.context.scene.collection.objects.link(root)
    parts = []

    body_m = make_mat("LT_body", (0.85, 0.85, 0.84), 0.55, 0.05, TEX / body_tex)
    logo_m = make_mat("LT_logo", (0.8, 0.8, 0.8), 0.5, 0.0, TEX / logo_tex)
    black_m = make_mat("LT_black", (0.1, 0.1, 0.1), 0.4, 0.7, TEX / "lt_metal_black.png")
    gray_m = make_mat("LT_gray", (0.55, 0.55, 0.55), 0.45, 0.5, TEX / "lt_metal_gray.png")
    lens_m = make_mat("LT_lens", (1.0, 0.95, 0.8), 0.2, 0.0, TEX / "lt_lens.png")
    tire_m = make_mat("LT_tire", (0.05, 0.05, 0.05), 0.9, 0.0, TEX / "lt_tire.png")

    # --- Trailer deck / chassis ---
    # Body sits roughly from y=-0.3 to y=1.6, mast at front ~ y=-0.1
    chassis = box("chassis", (0, 0.6, 0.18), (1.05, 2.3, 0.12), black_m, 0.008)
    parts.append(chassis)

    # Generator housing
    body = box("body", (0, 0.75, 0.75), (1.0, 1.7, 1.05), body_m, 0.02)
    parts.append(body)

    # Logo plates both sides
    for i, x in enumerate((-0.52, 0.52)):
        logo = box(
            f"logo_{i}",
            (x, 0.85, 0.85),
            (0.02, 0.9, 0.55),
            logo_m,
            0.005,
        )
        parts.append(logo)

    # Front vents hint box
    vent = box("vent", (0, -0.05, 0.75), (0.85, 0.08, 0.5), black_m, 0.005)
    parts.append(vent)

    # Hitch tongue
    tongue = box("tongue", (0, -1.15, 0.28), (0.12, 1.1, 0.08), black_m, 0.005)
    parts.append(tongue)
    hitch = cyl("hitch", (0, -1.7, 0.28), 0.05, 0.12, black_m, rot=(0, math.radians(90), 0))
    parts.append(hitch)

    # Wheels (single axle toward rear)
    for i, x in enumerate((-0.62, 0.62)):
        tire = cyl(
            f"tire_{i}",
            (x, 1.35, 0.28),
            0.28,
            0.18,
            tire_m,
            rot=(0, math.radians(90), 0),
            verts=16,
        )
        parts.append(tire)
        fender = box(f"fender_{i}", (x, 1.35, 0.55), (0.22, 0.55, 0.12), black_m, 0.01)
        parts.append(fender)

    # Outrigger jacks — front and rear corners
    for i, (x, y) in enumerate([(-0.55, -0.5), (0.55, -0.5), (-0.55, 1.6), (0.55, 1.6)]):
        leg = cyl(f"jack_{i}", (x, y, 0.25), 0.03, 0.5, gray_m)
        parts.append(leg)
        foot = cyl(f"foot_{i}", (x, y, 0.04), 0.08, 0.04, gray_m)
        parts.append(foot)

    # --- Mast (telescoping look: nested boxes) ---
    mast_base_z = 1.35
    seg_h = mast_h / 3
    for i, (s, zoff) in enumerate(
        [
            (0.12, mast_base_z + seg_h * 0.5),
            (0.10, mast_base_z + seg_h * 1.4),
            (0.08, mast_base_z + seg_h * 2.25),
        ]
    ):
        seg = box(
            f"mast_{i}",
            (0, -0.15, zoff),
            (s, s, seg_h * 1.05),
            black_m,
            0.005,
        )
        parts.append(seg)

    # Winch box at mast base
    winch = box("winch", (0.2, -0.15, 1.45), (0.25, 0.25, 0.25), black_m, 0.008)
    parts.append(winch)

    # Cable run
    cable = cyl(
        "cable",
        (0.08, -0.15, mast_base_z + mast_h * 0.45),
        0.015,
        mast_h * 0.85,
        black_m,
        verts=8,
    )
    parts.append(cable)

    # Crossbar at top
    top_z = mast_base_z + mast_h * 0.95
    bar = box("crossbar", (0, -0.15, top_z), (1.6, 0.08, 0.08), black_m, 0.005)
    parts.append(bar)

    # 4 floodlights in 2x2
    positions = [
        (-0.45, -0.15, top_z + 0.25, math.radians(-15)),
        (0.45, -0.15, top_z + 0.25, math.radians(-15)),
        (-0.45, -0.35, top_z + 0.15, math.radians(20)),
        (0.45, -0.35, top_z + 0.15, math.radians(20)),
    ]
    for i, (x, y, z, tilt) in enumerate(positions):
        housing = box(f"light_h_{i}", (x, y, z), (0.35, 0.18, 0.28), black_m, 0.01)
        housing.rotation_euler[0] = tilt
        apply_object(housing)
        parts.append(housing)
        # lens on front (-Y-ish)
        lens = box(
            f"light_l_{i}",
            (x, y - 0.1, z),
            (0.30, 0.03, 0.24),
            lens_m,
            0.005,
        )
        lens.rotation_euler[0] = tilt
        apply_object(lens)
        parts.append(lens)

    for p in parts:
        p.parent = root

    # Sit on ground: shift so lowest point ~0 (jacks/tires already near 0)
    return root


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root


def export_dae(root, name):
    OUT.mkdir(parents=True, exist_ok=True)
    select_hierarchy(root)
    path = OUT / f"{name}.dae"
    bpy.ops.wm.collada_export(
        filepath=str(path),
        selected=True,
        apply_modifiers=True,
        include_children=True,
        include_armatures=False,
        include_shapekeys=False,
        use_texture_copies=True,
        export_global_forward_selection="Y",
        export_global_up_selection="Z",
        apply_global_orientation=True,
    )
    print(f"exported {path}")


def main():
    for body, logo, _ in VARIANTS.values():
        for f in (body, logo, "lt_metal_black.png", "lt_metal_gray.png", "lt_lens.png", "lt_tire.png"):
            if not (TEX / f).exists():
                print(f"Missing {f}", file=sys.stderr)
                sys.exit(1)

    reset_scene()
    first = True
    for name, (body, logo, mast_h) in VARIANTS.items():
        clear_all()
        root = build_tower(body, logo, mast_h)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            first = False
        export_dae(root, name)

    for master in ("lt_body.png", "lt_logo.png"):
        src = TEX / master
        if src.exists():
            (OUT / master).write_bytes(src.read_bytes())

    print(f"DONE: exported {len(VARIANTS)} light towers")


if __name__ == "__main__":
    main()
