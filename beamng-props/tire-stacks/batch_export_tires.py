"""
Tire stacks for course barriers / runoff.
Run: blender --background --python batch_export_tires.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "tire_stacks.blend"

TIRE_R = 0.36
TIRE_H = 0.24
WALL = 0.08

STACKS = {
    "tire_single": 1,
    "tire_stack_2": 2,
    "tire_stack_3": 3,
    "tire_stack_4": 4,
    "tire_stack_5": 5,
    "tire_stack_6": 6,
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


def make_mat(name, color, roughness=0.85, metallic=0.0, image_path=None):
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


def make_tire(z, rubber_mat, rim_mat, idx):
    # Outer torus-like: use cylinder annulus approximation — torus is perfect
    bpy.ops.mesh.primitive_torus_add(
        major_radius=TIRE_R - WALL * 0.35,
        minor_radius=WALL,
        major_segments=24,
        minor_segments=10,
        location=(0, 0, z + TIRE_H / 2),
    )
    tire = bpy.context.active_object
    tire.name = f"tire_{idx}"
    # squash torus into tire proportions
    tire.scale = (1.0, 1.0, (TIRE_H * 0.45) / WALL)
    apply_object(tire)
    tire.data.materials.append(rubber_mat)
    uv_smart(tire)

    # simple rim disc
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=TIRE_R - WALL * 1.1,
        depth=0.04,
        location=(0, 0, z + TIRE_H / 2),
    )
    rim = bpy.context.active_object
    rim.name = f"rim_{idx}"
    apply_object(rim)
    rim.data.materials.append(rim_mat)
    return tire, rim


def build_stack(count: int):
    root = bpy.data.objects.new("tire_root", None)
    bpy.context.scene.collection.objects.link(root)
    rubber = make_mat("TIRE_rubber", (0.08, 0.08, 0.08), 0.9, 0.0, TEX / "tire_rubber.png")
    rim = make_mat("TIRE_rim", (0.4, 0.4, 0.42), 0.4, 0.6, TEX / "tire_rim.png")
    for i in range(count):
        z = i * (TIRE_H * 0.92)
        t, r = make_tire(z, rubber, rim, i)
        # slight rotation offset for realism
        t.rotation_euler[2] = math.radians(i * 17)
        apply_object(t)
        t.parent = root
        r.parent = root
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
    for f in ("tire_rubber.png", "tire_rim.png"):
        if not (TEX / f).exists():
            print(f"Missing {f}", file=sys.stderr)
            sys.exit(1)
    reset_scene()
    first = True
    # also a short wall of 3 tires side by side
    extras = []
    for name, count in STACKS.items():
        clear_all()
        root = build_stack(count)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            first = False
        export_dae(root, name)

    # tire row barrier (3 tires on ground)
    clear_all()
    root = bpy.data.objects.new("tire_row_root", None)
    bpy.context.scene.collection.objects.link(root)
    rubber = make_mat("TIRE_rubber", (0.08, 0.08, 0.08), 0.9, 0.0, TEX / "tire_rubber.png")
    rim_m = make_mat("TIRE_rim", (0.4, 0.4, 0.42), 0.4, 0.6, TEX / "tire_rim.png")
    for i, x in enumerate((-0.75, 0.0, 0.75)):
        t, r = make_tire(0, rubber, rim_m, i)
        t.location.x = x
        r.location.x = x
        t.parent = root
        r.parent = root
    export_dae(root, "tire_row_3")

    print(f"DONE: exported {len(STACKS) + 1} tire props")


if __name__ == "__main__":
    main()
