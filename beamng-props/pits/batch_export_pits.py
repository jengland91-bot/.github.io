"""
Build EXIT signs and pit mats. Export Collada (.dae).

Run:
  blender --background --python batch_export_pits.py
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
BLEND_OUT = ROOT / "export" / "pits.blend"

POST_H = 1.5
POST_W = 0.09
SIGN_W = 0.70
SIGN_H = 0.45
SIGN_T = 0.03

# Pit mat sizes (meters)
MATS = {
    "mat_rubber_2x1": ("mat_rubber.png", 2.0, 1.0),
    "mat_rubber_3x1_5": ("mat_rubber.png", 3.0, 1.5),
    "mat_checkered_2x1": ("mat_checkered.png", 2.0, 1.0),
    "mat_checkered_3x2": ("mat_checkered.png", 3.0, 2.0),
    "mat_orange_trim_2x1": ("mat_orange_trim.png", 2.0, 1.0),
    "mat_orange_trim_4x2": ("mat_orange_trim.png", 4.0, 2.0),
    "mat_pitstall_3x2": ("mat_pitstall.png", 3.0, 2.0),
    "mat_pitstall_4x2": ("mat_pitstall.png", 4.0, 2.0),
}

EXITS = {
    "exit": "exit.png",
    "exit_up": "exit_up.png",
    "exit_left": "exit_left.png",
    "exit_right": "exit_right.png",
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


def apply_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def add_bevel(obj, width=0.002, segments=1):
    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(30)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)


def load_image(path: Path):
    for img in bpy.data.images:
        if img.name == path.name:
            return img
    return bpy.data.images.load(str(path))


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


def new_root(name):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = name
    return root


def build_exit(tex_name: str):
    root = new_root("exit_root")
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, POST_H / 2))
    post = bpy.context.active_object
    post.name = "exit_post"
    post.scale = (POST_W, POST_W, POST_H)
    apply_object(post)
    add_bevel(post, 0.002, 1)

    bpy.ops.mesh.primitive_cone_add(
        vertices=4, radius1=POST_W * 0.7, depth=0.16, location=(0, 0, -0.06)
    )
    tip = bpy.context.active_object
    tip.name = "exit_tip"
    tip.rotation_euler[2] = math.radians(45)
    apply_object(tip)

    wood = make_mat("PIT_wood", (0.35, 0.22, 0.12), 0.85, 0.0, TEX / "post_wood.png")
    post.data.materials.append(wood)
    tip.data.materials.append(wood)

    y = -(POST_W / 2 + SIGN_T / 2 + 0.004)
    z = 1.25
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y, z))
    sign = bpy.context.active_object
    sign.name = "exit_sign"
    sign.scale = (SIGN_W, SIGN_T, SIGN_H)
    apply_object(sign)
    add_bevel(sign, 0.002, 2)
    sm = make_mat("PIT_exit", (0.1, 0.5, 0.3), 0.45, 0.05, TEX / tex_name)
    sign.data.materials.append(sm)
    uv_smart(sign)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y + 0.004, z))
    frame = bpy.context.active_object
    frame.name = "exit_frame"
    frame.scale = (SIGN_W + 0.02, SIGN_T * 0.4, SIGN_H + 0.02)
    apply_object(frame)
    frame.data.materials.append(make_mat("PIT_frame", (0.9, 0.9, 0.9), 0.4, 0.1))

    for obj in (post, tip, sign, frame):
        obj.parent = root
    return root


def build_mat(tex_name: str, size_x: float, size_y: float):
    root = new_root("mat_root")
    # very thin mat sitting on ground (z slightly above 0 to avoid z-fight)
    thickness = 0.015
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, thickness / 2))
    mat_obj = bpy.context.active_object
    mat_obj.name = "pit_mat"
    mat_obj.scale = (size_x, size_y, thickness)
    apply_object(mat_obj)
    mm = make_mat("PIT_mat", (0.15, 0.15, 0.16), 0.9, 0.0, TEX / tex_name)
    mat_obj.data.materials.append(mm)
    uv_smart(mat_obj)
    mat_obj.parent = root
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
    for f in list(EXITS.values()) + [v[0] for v in MATS.values()] + ["post_wood.png"]:
        if not (TEX / f).exists():
            print(f"Missing {f}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    count = 0

    for name, tex in EXITS.items():
        clear_all()
        root = build_exit(tex)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
            first = False
        export_dae(root, name)
        count += 1

    for name, (tex, sx, sy) in MATS.items():
        clear_all()
        root = build_mat(tex, sx, sy)
        export_dae(root, name)
        count += 1

    print(f"DONE: exported {count} pit props")


if __name__ == "__main__":
    main()
