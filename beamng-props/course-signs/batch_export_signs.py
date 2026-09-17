"""
Batch-build Parker 400 course signs and export Collada (.dae).
Includes arrow markers (WRONG WAY on back), wrong-way, and danger X.

Run:
  /path/to/blender --background --python batch_export_signs.py
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
BLEND_OUT = ROOT / "export" / "course_signs.blend"
MILE_TEX = ROOT.parent / "mile-marker" / "textures"

POST_HEIGHT = 1.55
POST_WIDTH = 0.09
SIGN_W = 0.55
SIGN_H = 0.55
SIGN_T = 0.03

# name -> (front_texture, back_texture or None)
SIGNS = {
    "arrow_straight": ("arrow_straight.png", "arrow_back_wrong_way.png"),
    "arrow_slight_left": ("arrow_slight_left.png", "arrow_back_wrong_way.png"),
    "arrow_slight_right": ("arrow_slight_right.png", "arrow_back_wrong_way.png"),
    "arrow_turn_left": ("arrow_turn_left.png", "arrow_back_wrong_way.png"),
    "arrow_turn_right": ("arrow_turn_right.png", "arrow_back_wrong_way.png"),
    "arrow_double_left": ("arrow_double_left.png", "arrow_back_wrong_way.png"),
    "arrow_double_right": ("arrow_double_right.png", "arrow_back_wrong_way.png"),
    "arrow_triple_left": ("arrow_triple_left.png", "arrow_back_wrong_way.png"),
    "arrow_triple_right": ("arrow_triple_right.png", "arrow_back_wrong_way.png"),
    "sign_wrong_way": ("sign_wrong_way.png", None),
    "sign_danger_x": ("sign_danger_x.png", None),
}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"


def apply_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def add_bevel(obj, width=0.003, segments=2):
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
        if Path(bpy.path.abspath(img.filepath)).resolve() == path.resolve() or img.name == path.name:
            return img
    return bpy.data.images.load(str(path))


def make_mat(name, color, roughness=0.7, metallic=0.0, image_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    img_node = None
    if image_path and Path(image_path).exists():
        img_node = nodes.new("ShaderNodeTexImage")
        img_node.image = load_image(Path(image_path))
        links.new(img_node.outputs["Color"], bsdf.inputs["Base Color"])
    return mat, img_node


def tex_path(name: str) -> Path:
    p = TEX / name
    if p.exists():
        return p
    alt = MILE_TEX / name
    if alt.exists():
        return alt
    return p


def clear_objects():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    # keep images/materials lightly cleaned for swaps
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def build_sign(front_tex: str, back_tex: str | None):
    clear_objects()

    # Post
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, POST_HEIGHT / 2))
    post = bpy.context.active_object
    post.name = "sign_post"
    post.scale = (POST_WIDTH, POST_WIDTH, POST_HEIGHT)
    apply_object(post)
    add_bevel(post, 0.0025, 2)

    bpy.ops.mesh.primitive_cone_add(
        vertices=4, radius1=POST_WIDTH * 0.7, depth=0.16, location=(0.0, 0.0, -0.07)
    )
    tip = bpy.context.active_object
    tip.name = "sign_tip"
    tip.rotation_euler[2] = math.radians(45)
    apply_object(tip)

    wood_mat, _ = make_mat(
        "CS_wood",
        (0.35, 0.22, 0.12),
        roughness=0.85,
        image_path=tex_path("post_wood.png"),
    )
    post.data.materials.append(wood_mat)
    tip.data.materials.append(wood_mat)

    # Metal band
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 1.12))
    band = bpy.context.active_object
    band.name = "sign_band"
    band.scale = (0.11, 0.11, 0.035)
    apply_object(band)
    metal_mat, _ = make_mat(
        "CS_metal",
        (0.55, 0.57, 0.60),
        roughness=0.35,
        metallic=0.85,
        image_path=tex_path("sign_metal.png") if tex_path("sign_metal.png").exists() else None,
    )
    band.data.materials.append(metal_mat)

    # Front plate
    y_front = -(POST_WIDTH / 2 + SIGN_T / 2 + 0.004)
    z = 1.30
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_front, z))
    front = bpy.context.active_object
    front.name = "sign_front"
    front.scale = (SIGN_W, SIGN_T, SIGN_H)
    apply_object(front)
    add_bevel(front, 0.002, 2)

    front_mat, _ = make_mat(
        "CS_front",
        (0.9, 0.6, 0.2),
        roughness=0.45,
        metallic=0.1,
        image_path=tex_path(front_tex),
    )
    front.data.materials.append(front_mat)

    # UV unwrap front
    bpy.context.view_layer.objects.active = front
    front.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    front.select_set(False)

    children = [tip, band, front]

    # Back plate (WRONG WAY) for arrows
    if back_tex:
        y_back = POST_WIDTH / 2 + SIGN_T / 2 + 0.004
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_back, z))
        back = bpy.context.active_object
        back.name = "sign_back"
        back.scale = (SIGN_W, SIGN_T, SIGN_H)
        apply_object(back)
        add_bevel(back, 0.002, 2)
        back_mat, _ = make_mat(
            "CS_back",
            (0.7, 0.15, 0.15),
            roughness=0.45,
            metallic=0.1,
            image_path=tex_path(back_tex),
        )
        back.data.materials.append(back_mat)
        bpy.context.view_layer.objects.active = back
        back.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")
        back.select_set(False)
        children.append(back)
    else:
        # thin backer for single-sided signs
        y_back = POST_WIDTH / 2 + 0.008
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_back, z))
        backer = bpy.context.active_object
        backer.name = "sign_backer"
        backer.scale = (SIGN_W * 0.98, 0.012, SIGN_H * 0.98)
        apply_object(backer)
        backer.data.materials.append(metal_mat)
        children.append(backer)

    # Frame rim on front
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_front - 0.002, z))
    frame = bpy.context.active_object
    frame.name = "sign_frame"
    frame.scale = (SIGN_W + 0.025, SIGN_T * 0.4, SIGN_H + 0.025)
    apply_object(frame)
    frame_mat, _ = make_mat("CS_frame", (0.08, 0.08, 0.08), roughness=0.55, metallic=0.2)
    frame.data.materials.append(frame_mat)
    children.append(frame)

    for obj in children:
        obj.parent = post

    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.view_layer.objects.active = post
    post.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    post.location = Vector((0.0, 0.0, 0.0))
    post.select_set(False)
    return post


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root


def export_dae(root, name: str):
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
    # ensure textures exist
    missing = []
    for front, back in SIGNS.values():
        if not tex_path(front).exists():
            missing.append(front)
        if back and not tex_path(back).exists():
            missing.append(back)
    if missing:
        print("Missing textures:", missing, file=sys.stderr)
        sys.exit(1)

    reset_scene()
    first = True
    for name, (front, back) in SIGNS.items():
        root = build_sign(front, back)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
            first = False
        export_dae(root, name)

    print(f"DONE: exported {len(SIGNS)} course signs")


if __name__ == "__main__":
    main()
