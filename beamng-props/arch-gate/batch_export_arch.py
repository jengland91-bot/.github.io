"""
Build a fully blank / recolorable inflatable arch.
Swap arch_tube.png, arch_block.png, arch_logo.png to change colors & branding.

Run:
  blender --background --python batch_export_arch.py
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
BLEND_OUT = ROOT / "export" / "arch_gates.blend"

CLEAR_W = 7.0
CLEAR_H = 4.6
TUBE_R = 0.55
BLOCK_W = 3.2
BLOCK_H = 1.35
BLOCK_D = 0.85

# One blank arch + optional preset recolors (still editable via PNG overwrite)
VARIANTS = {
    "arch_blank": ("arch_tube.png", "arch_block.png", "arch_logo.png"),
    "arch_preset_yellow_black": (
        "arch_tube_yellow.png",
        "arch_block_black.png",
        "arch_logo_black.png",
    ),
    "arch_preset_orange_black": (
        "arch_tube_orange.png",
        "arch_block_black.png",
        "arch_logo_black.png",
    ),
    "arch_preset_white_navyish": (
        "arch_tube_white.png",
        "arch_block_gray.png",
        "arch_logo_black.png",
    ),
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


def make_mat(name, color, roughness=0.55, metallic=0.0, image_path=None):
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
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.35
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
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


def apply_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def add_bevel(obj, width=0.04, segments=3):
    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(25)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)


def cylinder_between(p0, p1, radius, name, verts=16):
    p0 = Vector(p0)
    p1 = Vector(p1)
    mid = (p0 + p1) / 2
    direction = p1 - p0
    length = direction.length
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=length, location=mid
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    apply_object(obj)
    return obj


def rounded_block(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    apply_object(obj)
    add_bevel(obj, width=0.12, segments=4)
    return obj


def build_arch(tube_tex: str, block_tex: str, logo_tex: str):
    root_empty = bpy.data.objects.new("arch_root", None)
    bpy.context.scene.collection.objects.link(root_empty)

    tube_mat = make_mat("ARCH_tube", (0.9, 0.9, 0.9), 0.5, 0.0, TEX / tube_tex)
    block_mat = make_mat("ARCH_block", (0.7, 0.7, 0.7), 0.55, 0.0, TEX / block_tex)
    logo_mat = make_mat("ARCH_logo", (0.4, 0.4, 0.4), 0.45, 0.0, TEX / logo_tex)

    half_w = CLEAR_W / 2 + TUBE_R
    leg_top_z = CLEAR_H + TUBE_R * 0.3
    block_z = CLEAR_H + BLOCK_H / 2 + 0.15
    arm_inner_x = BLOCK_W / 2 + TUBE_R * 0.2
    arm_top_z = block_z + BLOCK_H / 2 + TUBE_R * 0.4

    parts = []

    for side, sx in (("L", -half_w), ("R", half_w)):
        leg = cylinder_between(
            (sx, 0, TUBE_R), (sx, 0, leg_top_z), TUBE_R, f"arch_leg_{side}", verts=18
        )
        leg.data.materials.append(tube_mat)
        uv_smart(leg)
        parts.append(leg)

        arm = cylinder_between(
            (sx, 0, leg_top_z),
            (math.copysign(arm_inner_x, sx), 0, arm_top_z),
            TUBE_R * 0.95,
            f"arch_arm_{side}",
            verts=18,
        )
        arm.data.materials.append(tube_mat)
        uv_smart(arm)
        parts.append(arm)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=20, radius=TUBE_R * 1.35, depth=0.12, location=(sx, 0, 0.06)
        )
        foot = bpy.context.active_object
        foot.name = f"arch_foot_{side}"
        apply_object(foot)
        add_bevel(foot, 0.03, 2)
        foot.data.materials.append(tube_mat)
        parts.append(foot)

    block = rounded_block("arch_block", (BLOCK_W, BLOCK_D, BLOCK_H), (0, 0, block_z))
    block.data.materials.append(block_mat)
    uv_smart(block)
    parts.append(block)

    for i, y in enumerate((-BLOCK_D / 2 - 0.02, BLOCK_D / 2 + 0.02)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y, block_z))
        plate = bpy.context.active_object
        plate.name = f"arch_logo_plate_{i}"
        plate.scale = (BLOCK_W * 0.88, 0.025, BLOCK_H * 0.72)
        apply_object(plate)
        add_bevel(plate, 0.02, 2)
        plate.data.materials.append(logo_mat)
        uv_smart(plate)
        parts.append(plate)

    for side, sx in (("L", -1), ("R", 1)):
        conn = cylinder_between(
            (sx * (BLOCK_W / 2), 0, arm_top_z - TUBE_R * 0.2),
            (sx * arm_inner_x, 0, arm_top_z),
            TUBE_R * 0.85,
            f"arch_conn_{side}",
            verts=16,
        )
        conn.data.materials.append(tube_mat)
        uv_smart(conn)
        parts.append(conn)

    for p in parts:
        p.parent = root_empty
    return root_empty


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
        # Keep shared simple names for the blank arch; presets copy their own
        use_texture_copies=True,
        export_global_forward_selection="Y",
        export_global_up_selection="Z",
        apply_global_orientation=True,
    )
    print(f"exported {path}")


def main():
    for tube, block, logo in VARIANTS.values():
        for f in (tube, block, logo):
            if not (TEX / f).exists():
                print(f"Missing {f}", file=sys.stderr)
                sys.exit(1)

    reset_scene()
    first = True
    for name, (tube, block, logo) in VARIANTS.items():
        clear_all()
        root = build_arch(tube, block, logo)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
            first = False
        export_dae(root, name)

    # Ensure blank arch folder has the three master swappable names clearly present
    for master in ("arch_tube.png", "arch_block.png", "arch_logo.png"):
        src = TEX / master
        dst = OUT / master
        if src.exists():
            dst.write_bytes(src.read_bytes())

    print(f"DONE: exported {len(VARIANTS)} arch gates (fully recolorable)")


if __name__ == "__main__":
    main()
