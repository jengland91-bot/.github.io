"""
Parker 400 mile marker builder for Blender 4.x
================================================
How to use (on your PC):
1. Open Blender (new General file is fine)
2. Switch workspace to "Scripting"
3. Open this file (or paste it)
4. Click Run Script
5. A finished mile marker appears at the world origin
6. File > Export > Collada (.dae) with Selection Only enabled

Optional: change MILE_NUMBER below before running.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector

# --------------- tweakables ---------------
MILE_NUMBER = 1
POST_HEIGHT = 1.45
POST_WIDTH = 0.10
SIGN_WIDTH = 0.42
SIGN_HEIGHT = 0.28
SIGN_THICKNESS = 0.03
COLLECTION_NAME = "MileMarker"
# Set to a folder with mile_XX.png textures, or leave None to use generated colors
TEXTURE_DIR = Path(__file__).resolve().parent / "textures"
# ------------------------------------------


def clear_previous():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

    # Also remove leftover meshes/materials from prior runs
    for name in list(bpy.data.meshes.keys()):
        if name.startswith("MM_"):
            bpy.data.meshes.remove(bpy.data.meshes[name])
    for name in list(bpy.data.materials.keys()):
        if name.startswith("MM_"):
            bpy.data.materials.remove(bpy.data.materials[name])


def ensure_collection():
    col = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(col)
    return col


def link(obj, col):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def apply_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def add_bevel(obj, width=0.004, segments=2):
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

    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-250, 0)
        img = bpy.data.images.load(str(image_path))
        tex.image = img
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    return mat


def create_post(col):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, POST_HEIGHT / 2))
    post = bpy.context.active_object
    post.name = "MM_post"
    post.data.name = "MM_post"
    post.scale = (POST_WIDTH, POST_WIDTH, POST_HEIGHT)
    apply_object(post)
    add_bevel(post, width=0.003, segments=2)

    # Pointed stake tip under ground (visual only, short)
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=POST_WIDTH * 0.72,
        depth=0.18,
        location=(0.0, 0.0, -0.08),
    )
    tip = bpy.context.active_object
    tip.name = "MM_stake_tip"
    tip.data.name = "MM_stake_tip"
    tip.rotation_euler[2] = math.radians(45)
    apply_object(tip)

    wood = TEXTURE_DIR / "post_wood.png"
    mat = make_mat(
        "MM_wood",
        (0.35, 0.22, 0.12),
        roughness=0.85,
        image_path=wood if wood.exists() else None,
    )
    post.data.materials.append(mat)
    tip.data.materials.append(mat)

    link(post, col)
    link(tip, col)
    return post, tip


def create_band(col):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 1.07))
    band = bpy.context.active_object
    band.name = "MM_metal_band"
    band.data.name = "MM_metal_band"
    band.scale = (0.112, 0.112, 0.04)
    apply_object(band)
    add_bevel(band, width=0.002, segments=1)
    metal = TEXTURE_DIR / "sign_metal.png"
    mat = make_mat(
        "MM_metal",
        (0.55, 0.57, 0.60),
        roughness=0.35,
        metallic=0.85,
        image_path=metal if metal.exists() else None,
    )
    band.data.materials.append(mat)
    link(band, col)
    return band


def create_sign(col, mile_number: int):
    # Main plate
    y = -(POST_WIDTH / 2 + SIGN_THICKNESS / 2 + 0.005)
    z = 1.24
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y, z))
    sign = bpy.context.active_object
    sign.name = "MM_sign"
    sign.data.name = "MM_sign"
    sign.scale = (SIGN_WIDTH, SIGN_THICKNESS, SIGN_HEIGHT)
    apply_object(sign)
    add_bevel(sign, width=0.0025, segments=2)

    # Frame / raised rim (slightly larger, thinner in Y so rim shows)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y + 0.004, z))
    frame = bpy.context.active_object
    frame.name = "MM_sign_frame"
    frame.data.name = "MM_sign_frame"
    frame.scale = (SIGN_WIDTH + 0.02, SIGN_THICKNESS * 0.45, SIGN_HEIGHT + 0.02)
    apply_object(frame)

    tex = TEXTURE_DIR / f"mile_{mile_number:02d}.png"
    if not tex.exists():
        tex = TEXTURE_DIR / "sign_blank.png"

    sign_mat = make_mat(
        "MM_sign_face",
        (0.92, 0.90, 0.85),
        roughness=0.45,
        metallic=0.15,
        image_path=tex if tex.exists() else None,
    )
    frame_mat = make_mat("MM_sign_frame_mat", (0.08, 0.08, 0.08), roughness=0.55, metallic=0.2)

    sign.data.materials.append(sign_mat)
    frame.data.materials.append(frame_mat)

    # Unwrap front face for readable texture
    bpy.context.view_layer.objects.active = sign
    sign.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    sign.select_set(False)

    link(sign, col)
    link(frame, col)
    return sign, frame


def create_bolt_heads(col):
    bolts = []
    y = -(POST_WIDTH / 2 + SIGN_THICKNESS + 0.008)
    positions = [(-0.16, 1.14), (0.16, 1.14), (-0.16, 1.34), (0.16, 1.34)]
    mat = make_mat("MM_bolt", (0.25, 0.25, 0.26), roughness=0.3, metallic=0.9)
    for i, (x, z) in enumerate(positions):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.008, depth=0.01, location=(x, y, z)
        )
        b = bpy.context.active_object
        b.name = f"MM_bolt_{i}"
        b.data.name = f"MM_bolt_{i}"
        b.rotation_euler[0] = math.radians(90)
        apply_object(b)
        b.data.materials.append(mat)
        link(b, col)
        bolts.append(b)
    return bolts


def parent_all(root, others):
    for obj in others:
        obj.parent = root


def set_origin_to_base(root):
    # Origin at ground under post
    bpy.context.view_layer.objects.active = root
    root.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    # Force cursor to world origin first
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    root.location = Vector((0.0, 0.0, 0.0))
    root.select_set(False)


def setup_scene_units():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"


def main():
    setup_scene_units()
    clear_previous()
    col = ensure_collection()

    # Clean default cube if present
    for obj in list(bpy.data.objects):
        if obj.name == "Cube" and obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    post, tip = create_post(col)
    band = create_band(col)
    sign, frame = create_sign(col, MILE_NUMBER)
    bolts = create_bolt_heads(col)

    parent_all(post, [tip, band, sign, frame, *bolts])
    set_origin_to_base(post)

    # Select the finished marker for easy export
    bpy.ops.object.select_all(action="DESELECT")
    post.select_set(True)
    bpy.context.view_layer.objects.active = post

    print(
        f"Mile marker {MILE_NUMBER} ready. "
        "Select the post (children included) and export Collada (.dae)."
    )


if __name__ == "__main__":
    main()
