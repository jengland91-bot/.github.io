"""
Chain-link fence panels and gates for BeamNG.
Run: blender --background --python batch_export_chainlink.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "chainlink.blend"

# Modular panels along +X
PANELS = {
    "chainlink_2m": ("chainlink.png", 2.0, 1.8),
    "chainlink_3m": ("chainlink.png", 3.0, 1.8),
    "chainlink_6m": ("chainlink.png", 6.0, 1.8),
    "chainlink_green_3m": ("chainlink_green.png", 3.0, 1.8),
    "chainlink_dark_3m": ("chainlink_dark.png", 3.0, 1.8),
    "chainlink_tall_3m": ("chainlink.png", 3.0, 2.4),
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


def make_mat(name, color, roughness=0.7, metallic=0.4, image_path=None):
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


def build_panel(mesh_tex: str, width: float, height: float):
    root = bpy.data.objects.new("cl_root", None)
    bpy.context.scene.collection.objects.link(root)
    mesh_m = make_mat("CL_mesh", (0.35, 0.38, 0.4), 0.55, 0.6, TEX / mesh_tex)
    post_m = make_mat("CL_post", (0.3, 0.3, 0.32), 0.4, 0.7, TEX / "fence_post.png")
    parts = []

    post_r = 0.04
    # end posts
    for i, x in enumerate((post_r, width - post_r)):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=post_r, depth=height + 0.15, location=(x, 0, (height + 0.15) / 2)
        )
        post = bpy.context.active_object
        post.name = f"post_{i}"
        apply_object(post)
        post.data.materials.append(post_m)
        parts.append(post)
        # cap
        bpy.ops.mesh.primitive_uv_sphere_add(radius=post_r * 1.2, location=(x, 0, height + 0.12))
        cap = bpy.context.active_object
        cap.name = f"cap_{i}"
        apply_object(cap)
        cap.data.materials.append(post_m)
        parts.append(cap)

    # top rail
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.025, depth=width - post_r * 2, location=(width / 2, 0, height)
    )
    rail = bpy.context.active_object
    rail.name = "top_rail"
    rail.rotation_euler[1] = math.radians(90)
    apply_object(rail)
    rail.data.materials.append(post_m)
    parts.append(rail)

    # mesh plane (thin)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(width / 2, 0, height / 2))
    mesh = bpy.context.active_object
    mesh.name = "mesh"
    mesh.scale = (width - post_r * 4, 0.02, height * 0.92)
    apply_object(mesh)
    mesh.data.materials.append(mesh_m)
    uv_smart(mesh)
    parts.append(mesh)

    for p in parts:
        p.parent = root
    return root


def build_gate(mesh_tex: str, width=1.2, height=1.8):
    """Single swing gate panel (same as panel but narrower + latch stub)."""
    root = build_panel(mesh_tex, width, height)
    # rename conceptually - add latch
    post_m = make_mat("CL_latch", (0.25, 0.25, 0.25), 0.4, 0.8)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(width - 0.05, -0.06, height * 0.55))
    latch = bpy.context.active_object
    latch.name = "latch"
    latch.scale = (0.08, 0.12, 0.04)
    apply_object(latch)
    latch.data.materials.append(post_m)
    latch.parent = root
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
    for tex, _, _ in PANELS.values():
        if not (TEX / tex).exists() or not (TEX / "fence_post.png").exists():
            print("Missing textures", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    count = 0
    for name, (tex, w, h) in PANELS.items():
        clear_all()
        root = build_panel(tex, w, h)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            first = False
        export_dae(root, name)
        count += 1

    clear_all()
    root = build_gate("chainlink.png", 1.2, 1.8)
    export_dae(root, "chainlink_gate_1m")
    count += 1

    # corner post alone for custom builds
    clear_all()
    root = bpy.data.objects.new("post_root", None)
    bpy.context.scene.collection.objects.link(root)
    post_m = make_mat("CL_post", (0.3, 0.3, 0.32), 0.4, 0.7, TEX / "fence_post.png")
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.05, depth=2.0, location=(0, 0, 1.0))
    post = bpy.context.active_object
    apply_object(post)
    post.data.materials.append(post_m)
    post.parent = root
    export_dae(root, "chainlink_post")
    count += 1

    print(f"DONE: exported {count} chainlink props")


if __name__ == "__main__":
    main()
