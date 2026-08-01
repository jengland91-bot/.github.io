"""
Hay bales — rectangular and round, single and stacked.
Run: blender --background --python batch_export_hay.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "hay_bales.blend"

# Typical small square bale ~1.0 x 0.45 x 0.35 m; large ~2.4 round
RECT = (1.0, 0.45, 0.35)  # x, y, z
ROUND_R = 0.75
ROUND_D = 1.2


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


def make_mat(name, color, image_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.95
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
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


def add_bevel(obj, width=0.02, segments=2):
    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(40)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)


def rect_bale(mat, loc=(0, 0, 0), rot_z=0):
    sx, sy, sz = RECT
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc[0], loc[1], loc[2] + sz / 2))
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    obj.rotation_euler[2] = rot_z
    apply_object(obj)
    add_bevel(obj, 0.025, 2)
    obj.data.materials.append(mat)
    uv_smart(obj)
    return obj


def round_bale(mat, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20, radius=ROUND_R, depth=ROUND_D, location=(loc[0], loc[1], ROUND_R)
    )
    obj = bpy.context.active_object
    obj.rotation_euler[0] = math.radians(90)  # lie on side
    apply_object(obj)
    # after rotate apply, lift to sit on ground
    min_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
    obj.location.z -= min_z
    obj.data.materials.append(mat)
    uv_smart(obj)
    return obj


def export_dae(root, name):
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
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


def wrap(objs, name):
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for o in objs:
        o.parent = root
    return root


def main():
    for f in ("hay_gold.png", "hay_dry.png", "hay_green.png"):
        if not (TEX / f).exists():
            print(f"Missing {f}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    exports = []

    def one(name, builder):
        clear_all()
        root = builder()
        export_dae(root, name)
        exports.append(name)

    # singles
    one(
        "haybale_rect_gold",
        lambda: wrap([rect_bale(make_mat("H", (0.8, 0.7, 0.3), TEX / "hay_gold.png"))], "r"),
    )
    one(
        "haybale_rect_dry",
        lambda: wrap([rect_bale(make_mat("H", (0.7, 0.6, 0.3), TEX / "hay_dry.png"))], "r"),
    )
    one(
        "haybale_round_gold",
        lambda: wrap([round_bale(make_mat("H", (0.8, 0.7, 0.3), TEX / "hay_gold.png"))], "r"),
    )

    # stack of 2
    def stack2():
        mat = make_mat("H", (0.8, 0.7, 0.3), TEX / "hay_gold.png")
        a = rect_bale(mat, (0, 0, 0))
        b = rect_bale(mat, (0, 0, RECT[2]))
        return wrap([a, b], "s2")

    one("haybale_stack_2", stack2)

    # stack of 3 pyramid-ish (2 bottom + 1 top)
    def stack3():
        mat = make_mat("H", (0.8, 0.7, 0.3), TEX / "hay_gold.png")
        a = rect_bale(mat, (-0.28, 0, 0))
        b = rect_bale(mat, (0.28, 0, 0))
        c = rect_bale(mat, (0, 0, RECT[2]))
        return wrap([a, b, c], "s3")

    one("haybale_stack_3", stack3)

    # wall of 4 in a row
    def wall4():
        mat = make_mat("H", (0.75, 0.65, 0.3), TEX / "hay_dry.png")
        objs = [rect_bale(mat, (0, i * (RECT[1] + 0.02), 0)) for i in range(4)]
        return wrap(objs, "w4")

    one("haybale_wall_4", wall4)

    # greenish fresh
    one(
        "haybale_rect_green",
        lambda: wrap([rect_bale(make_mat("H", (0.55, 0.6, 0.25), TEX / "hay_green.png"))], "r"),
    )

    # save blend of last
    BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    print(f"DONE: exported {len(exports)} hay bales")


if __name__ == "__main__":
    main()
