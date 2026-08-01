"""
Batch-build LAP 1–10 signs and export Collada (.dae).
Run:
  blender --background --python batch_export_laps.py
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
BLEND_OUT = ROOT / "export" / "lap_signs.blend"
MILE_TEX = ROOT.parent / "mile-marker" / "textures"

POST_HEIGHT = 1.45
POST_WIDTH = 0.10
SIGN_W = 0.42
SIGN_H = 0.28
SIGN_T = 0.03


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "METERS"


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
        if img.name == path.name:
            return img
        try:
            if Path(bpy.path.abspath(img.filepath)).resolve() == path.resolve():
                return img
        except Exception:
            pass
    return bpy.data.images.load(str(path))


def tex(name: str) -> Path:
    p = TEX / name
    if p.exists():
        return p
    alt = MILE_TEX / name
    return alt if alt.exists() else p


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
    img_node = None
    if image_path and Path(image_path).exists():
        img_node = nodes.new("ShaderNodeTexImage")
        img_node.image = load_image(Path(image_path))
        links.new(img_node.outputs["Color"], bsdf.inputs["Base Color"])
    return mat, img_node


def clear_meshes():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def build_lap(n: int):
    clear_meshes()

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, POST_HEIGHT / 2))
    post = bpy.context.active_object
    post.name = "lap_post"
    post.scale = (POST_WIDTH, POST_WIDTH, POST_HEIGHT)
    apply_object(post)
    add_bevel(post, 0.003, 2)

    bpy.ops.mesh.primitive_cone_add(
        vertices=4, radius1=POST_WIDTH * 0.72, depth=0.18, location=(0.0, 0.0, -0.08)
    )
    tip = bpy.context.active_object
    tip.name = "lap_tip"
    tip.rotation_euler[2] = math.radians(45)
    apply_object(tip)

    wood, _ = make_mat("LAP_wood", (0.35, 0.22, 0.12), 0.85, 0.0, tex("post_wood.png"))
    post.data.materials.append(wood)
    tip.data.materials.append(wood)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 1.07))
    band = bpy.context.active_object
    band.name = "lap_band"
    band.scale = (0.112, 0.112, 0.04)
    apply_object(band)
    metal, _ = make_mat(
        "LAP_metal",
        (0.55, 0.57, 0.60),
        0.35,
        0.85,
        tex("sign_metal.png") if tex("sign_metal.png").exists() else None,
    )
    band.data.materials.append(metal)

    y = -(POST_WIDTH / 2 + SIGN_T / 2 + 0.005)
    z = 1.24
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y, z))
    sign = bpy.context.active_object
    sign.name = "lap_sign"
    sign.scale = (SIGN_W, SIGN_T, SIGN_H)
    apply_object(sign)
    add_bevel(sign, 0.0025, 2)

    front_tex = tex(f"lap_{n:02d}.png")
    if not front_tex.exists():
        raise FileNotFoundError(front_tex)
    sign_mat, _ = make_mat("LAP_sign", (0.92, 0.93, 0.90), 0.45, 0.1, front_tex)
    sign.data.materials.append(sign_mat)

    bpy.context.view_layer.objects.active = sign
    sign.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    sign.select_set(False)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y + 0.004, z))
    frame = bpy.context.active_object
    frame.name = "lap_frame"
    frame.scale = (SIGN_W + 0.02, SIGN_T * 0.45, SIGN_H + 0.02)
    apply_object(frame)
    frame_mat, _ = make_mat("LAP_frame", (0.08, 0.08, 0.08), 0.55, 0.2)
    frame.data.materials.append(frame_mat)

    bolts = []
    by = -(POST_WIDTH / 2 + SIGN_T + 0.008)
    bolt_mat, _ = make_mat("LAP_bolt", (0.25, 0.25, 0.26), 0.3, 0.9)
    for i, (x, bz) in enumerate([(-0.16, 1.14), (0.16, 1.14), (-0.16, 1.34), (0.16, 1.34)]):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.008, depth=0.01, location=(x, by, bz)
        )
        b = bpy.context.active_object
        b.name = f"lap_bolt_{i}"
        b.rotation_euler[0] = math.radians(90)
        apply_object(b)
        b.data.materials.append(bolt_mat)
        bolts.append(b)

    for obj in [tip, band, sign, frame, *bolts]:
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


def export_dae(root, n: int):
    OUT.mkdir(parents=True, exist_ok=True)
    select_hierarchy(root)
    path = OUT / f"lapsign_{n:02d}.dae"
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
    for n in range(1, 11):
        if not tex(f"lap_{n:02d}.png").exists():
            print(f"Missing lap_{n:02d}.png", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    for n in range(1, 11):
        root = build_lap(n)
        if n == 1:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
        export_dae(root, n)

    print("DONE: exported lap signs 1-10")


if __name__ == "__main__":
    main()
