"""
Orange plastic safety netting rolls / fence sections.
Run: blender --background --python batch_export_netting.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "safety_netting.blend"

SECTIONS = {
    "safetynet_orange_2m": ("safety_orange.png", "safety_stake.png", 2.0, 1.1),
    "safetynet_orange_3m": ("safety_orange.png", "safety_stake.png", 3.0, 1.1),
    "safetynet_orange_5m": ("safety_orange.png", "safety_stake.png", 5.0, 1.1),
    "safetynet_orange_tall_3m": ("safety_orange.png", "safety_stake.png", 3.0, 1.5),
    "safetynet_yellow_3m": ("safety_yellow.png", "safety_stake.png", 3.0, 1.1),
    "safetynet_orange_wood_3m": ("safety_orange.png", "safety_stake_wood.png", 3.0, 1.1),
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


def build_section(net_tex, stake_tex, width, height):
    root = bpy.data.objects.new("net_root", None)
    bpy.context.scene.collection.objects.link(root)
    net_m = make_mat("NET", (0.9, 0.4, 0.1), 0.65, 0.0, TEX / net_tex)
    stake_m = make_mat("STAKE", (0.8, 0.35, 0.1), 0.7, 0.0, TEX / stake_tex)
    parts = []

    # stakes every ~1.5m including ends
    spacing = 1.5
    xs = [0.03]
    x = spacing
    while x < width - 0.1:
        xs.append(x)
        x += spacing
    xs.append(width - 0.03)

    for i, x in enumerate(xs):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.025, depth=height + 0.2, location=(x, 0, (height + 0.2) / 2 - 0.05)
        )
        stake = bpy.context.active_object
        stake.name = f"stake_{i}"
        apply_object(stake)
        stake.data.materials.append(stake_m)
        parts.append(stake)
        # pointed tip below
        bpy.ops.mesh.primitive_cone_add(
            vertices=6, radius1=0.025, depth=0.15, location=(x, 0, -0.05)
        )
        tip = bpy.context.active_object
        tip.name = f"tip_{i}"
        apply_object(tip)
        tip.data.materials.append(stake_m)
        parts.append(tip)

    # netting sheet
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(width / 2, 0, height / 2))
    net = bpy.context.active_object
    net.name = "netting"
    net.scale = (width - 0.08, 0.015, height)
    apply_object(net)
    net.data.materials.append(net_m)
    uv_smart(net)
    parts.append(net)

    for p in parts:
        p.parent = root
    return root


def export_dae(root, name):
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for o in root.children_recursive:
        o.select_set(True)
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


def main():
    for net, stake, _, _ in SECTIONS.values():
        if not (TEX / net).exists() or not (TEX / stake).exists():
            print("Missing textures", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    for name, (net, stake, w, h) in SECTIONS.items():
        clear_all()
        root = build_section(net, stake, w, h)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            first = False
        export_dae(root, name)

    print(f"DONE: exported {len(SECTIONS)} safety netting props")


if __name__ == "__main__":
    main()
