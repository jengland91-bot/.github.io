"""
Porta-potties for pits / spectator areas.
Blank body + logo. Color presets included.

Run: blender --background --python batch_export_portapotties.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "porta_potties.blend"

# Typical porta ~1.1 x 1.1 x 2.3 m
W, D, H = 1.1, 1.15, 2.3

VARIANTS = {
    "portapotty_blank": ("pp_body.png", "pp_door.png", "pp_logo.png"),
    "portapotty_blue": ("pp_body_blue.png", "pp_door_blue.png", "pp_logo.png"),
    "portapotty_gray": ("pp_body_gray.png", "pp_door_gray.png", "pp_logo.png"),
    "portapotty_green": ("pp_body_green.png", "pp_door_green.png", "pp_logo.png"),
    "portapotty_orange": ("pp_body_orange.png", "pp_door_orange.png", "pp_logo.png"),
    "portapotty_white": ("pp_body_white.png", "pp_door_white.png", "pp_logo.png"),
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


def add_bevel(obj, width=0.015, segments=2):
    mod = obj.modifiers.new("Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(30)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)


def box(name, loc, scale, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    apply_object(obj)
    if bevel:
        add_bevel(obj, bevel, 2)
    obj.data.materials.append(mat)
    uv_smart(obj)
    return obj


def build_potty(body_tex, door_tex, logo_tex):
    root = bpy.data.objects.new("pp_root", None)
    bpy.context.scene.collection.objects.link(root)

    body_m = make_mat("PP_body", (0.25, 0.4, 0.65), 0.55, 0.0, TEX / body_tex)
    door_m = make_mat("PP_door", (0.25, 0.4, 0.65), 0.55, 0.0, TEX / door_tex)
    logo_m = make_mat("PP_logo", (0.8, 0.8, 0.8), 0.5, 0.0, TEX / logo_tex)
    roof_m = make_mat("PP_roof", (0.15, 0.15, 0.15), 0.6, 0.0, TEX / "pp_roof.png")
    parts = []

    # Main body shell
    body = box("body", (0, 0, H / 2), (W, D, H), body_m, 0.03)
    parts.append(body)

    # Door on -Y face
    door = box(
        "door",
        (0, -D / 2 - 0.02, H * 0.48),
        (W * 0.72, 0.04, H * 0.78),
        door_m,
        0.01,
    )
    parts.append(door)

    # Roof overhang slightly larger
    roof = box("roof", (0, 0, H + 0.04), (W * 1.06, D * 1.06, 0.08), roof_m, 0.01)
    parts.append(roof)

    # Side logo panels
    for i, x in enumerate((-W / 2 - 0.015, W / 2 + 0.015)):
        logo = box(
            f"logo_{i}",
            (x, 0.05, H * 0.62),
            (0.025, D * 0.55, 0.45),
            logo_m,
            0.005,
        )
        parts.append(logo)

    # Base skid / feet
    for i, (x, y) in enumerate([(-0.35, -0.4), (0.35, -0.4), (-0.35, 0.4), (0.35, 0.4)]):
        foot = box(f"foot_{i}", (x, y, 0.03), (0.2, 0.2, 0.06), roof_m, 0.005)
        parts.append(foot)

    # Vent stack on roof
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.06, depth=0.25, location=(0.25, 0.25, H + 0.18)
    )
    vent = bpy.context.active_object
    vent.name = "vent"
    apply_object(vent)
    vent.data.materials.append(roof_m)
    parts.append(vent)

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
    for body, door, logo in VARIANTS.values():
        for f in (body, door, logo, "pp_roof.png"):
            if not (TEX / f).exists():
                print(f"Missing {f}", file=sys.stderr)
                sys.exit(1)

    reset_scene()
    first = True
    for name, (body, door, logo) in VARIANTS.items():
        clear_all()
        root = build_potty(body, door, logo)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            first = False
        export_dae(root, name)

    # double unit (two side by side)
    clear_all()
    root = bpy.data.objects.new("pp_double_root", None)
    bpy.context.scene.collection.objects.link(root)
    a = build_potty("pp_body_blue.png", "pp_door_blue.png", "pp_logo.png")
    b = build_potty("pp_body_blue.png", "pp_door_blue.png", "pp_logo.png")
    # reparent children of a/b under double root with offset
    for obj in list(a.children):
        obj.parent = root
    for obj in list(b.children):
        obj.location.x += W + 0.15
        obj.parent = root
    bpy.data.objects.remove(a, do_unlink=True)
    bpy.data.objects.remove(b, do_unlink=True)
    export_dae(root, "portapotty_double_blue")

    for master in ("pp_body.png", "pp_door.png", "pp_logo.png"):
        src = TEX / master
        if src.exists():
            (OUT / master).write_bytes(src.read_bytes())

    print(f"DONE: exported {len(VARIANTS) + 1} porta-potties")


if __name__ == "__main__":
    main()
