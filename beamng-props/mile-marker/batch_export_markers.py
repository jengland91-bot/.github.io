"""
Batch-build Parker 400 mile markers 1..100 and export Collada (.dae).
Run:
  blender --background --python batch_export_markers.py
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
BLEND_OUT = ROOT / "export" / "milemarkers_1_to_100.blend"

POST_HEIGHT = 1.45
POST_WIDTH = 0.10
SIGN_WIDTH = 0.42
SIGN_HEIGHT = 0.28
SIGN_THICKNESS = 0.03


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


def make_mat(name, color, roughness=0.7, metallic=0.0, image_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    img_node = None
    if image_path and Path(image_path).exists():
        img_node = nodes.new("ShaderNodeTexImage")
        img_node.location = (-250, 0)
        img_node.image = bpy.data.images.load(str(image_path))
        links.new(img_node.outputs["Color"], bsdf.inputs["Base Color"])
    return mat, img_node


def build_marker():
    # Post
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, POST_HEIGHT / 2))
    post = bpy.context.active_object
    post.name = "milemarker_post"
    post.scale = (POST_WIDTH, POST_WIDTH, POST_HEIGHT)
    apply_object(post)
    add_bevel(post, 0.003, 2)

    bpy.ops.mesh.primitive_cone_add(
        vertices=4, radius1=POST_WIDTH * 0.72, depth=0.18, location=(0.0, 0.0, -0.08)
    )
    tip = bpy.context.active_object
    tip.name = "milemarker_tip"
    tip.rotation_euler[2] = math.radians(45)
    apply_object(tip)

    wood_mat, _ = make_mat(
        "MM_wood",
        (0.35, 0.22, 0.12),
        roughness=0.85,
        image_path=TEX / "post_wood.png",
    )
    post.data.materials.append(wood_mat)
    tip.data.materials.append(wood_mat)

    # Band
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 1.07))
    band = bpy.context.active_object
    band.name = "milemarker_band"
    band.scale = (0.112, 0.112, 0.04)
    apply_object(band)
    add_bevel(band, 0.002, 1)
    metal_mat, _ = make_mat(
        "MM_metal",
        (0.55, 0.57, 0.60),
        roughness=0.35,
        metallic=0.85,
        image_path=TEX / "sign_metal.png",
    )
    band.data.materials.append(metal_mat)

    # Sign
    y = -(POST_WIDTH / 2 + SIGN_THICKNESS / 2 + 0.005)
    z = 1.24
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y, z))
    sign = bpy.context.active_object
    sign.name = "milemarker_sign"
    sign.scale = (SIGN_WIDTH, SIGN_THICKNESS, SIGN_HEIGHT)
    apply_object(sign)
    add_bevel(sign, 0.0025, 2)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y + 0.004, z))
    frame = bpy.context.active_object
    frame.name = "milemarker_frame"
    frame.scale = (SIGN_WIDTH + 0.02, SIGN_THICKNESS * 0.45, SIGN_HEIGHT + 0.02)
    apply_object(frame)

    # Start with mile 1 texture; swapped per export
    sign_mat, sign_img_node = make_mat(
        "MM_sign",
        (0.92, 0.90, 0.85),
        roughness=0.45,
        metallic=0.15,
        image_path=TEX / "mile_001.png",
    )
    frame_mat, _ = make_mat("MM_frame", (0.08, 0.08, 0.08), roughness=0.55, metallic=0.2)
    sign.data.materials.append(sign_mat)
    frame.data.materials.append(frame_mat)

    bpy.context.view_layer.objects.active = sign
    sign.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    sign.select_set(False)

    # Bolts
    bolts = []
    by = -(POST_WIDTH / 2 + SIGN_THICKNESS + 0.008)
    bolt_mat, _ = make_mat("MM_bolt", (0.25, 0.25, 0.26), roughness=0.3, metallic=0.9)
    for i, (x, z) in enumerate([(-0.16, 1.14), (0.16, 1.14), (-0.16, 1.34), (0.16, 1.34)]):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.008, depth=0.01, location=(x, by, z)
        )
        b = bpy.context.active_object
        b.name = f"milemarker_bolt_{i}"
        b.rotation_euler[0] = math.radians(90)
        apply_object(b)
        b.data.materials.append(bolt_mat)
        bolts.append(b)

    children = [tip, band, sign, frame, *bolts]
    for obj in children:
        obj.parent = post

    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.view_layer.objects.active = post
    post.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    post.location = Vector((0.0, 0.0, 0.0))
    post.select_set(False)

    return post, sign_mat, sign_img_node


def set_sign_texture(sign_img_node, mile: int):
    path = TEX / f"mile_{mile:03d}.png"
    if not path.exists():
        path = TEX / f"mile_{mile:02d}.png"
    if not path.exists():
        raise FileNotFoundError(path)
    # Reuse images if already loaded
    img = None
    for existing in bpy.data.images:
        if Path(existing.filepath).resolve() == path.resolve() or existing.name == path.name:
            img = existing
            break
    if img is None:
        img = bpy.data.images.load(str(path))
    sign_img_node.image = img


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root


def export_dae(root, mile: int):
    OUT.mkdir(parents=True, exist_ok=True)
    select_hierarchy(root)
    path = OUT / f"milemarker_{mile:03d}.dae"
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
    reset_scene()
    root, sign_mat, sign_img_node = build_marker()
    if sign_img_node is None:
        print("ERROR: sign image node missing", file=sys.stderr)
        sys.exit(1)

    # Save a master .blend with mile 1 texture loaded
    set_sign_texture(sign_img_node, 1)
    BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    print(f"saved {BLEND_OUT}")

    for mile in range(1, 101):
        set_sign_texture(sign_img_node, mile)
        export_dae(root, mile)

    print("DONE: exported mile markers 1-100")


if __name__ == "__main__":
    main()
