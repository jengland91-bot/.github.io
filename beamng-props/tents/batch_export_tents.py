"""
Shade / pit / spectator tents — blank fabric + logo panel for branding.
Run: blender --background --python batch_export_tents.py
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
BLEND_OUT = ROOT / "export" / "tents.blend"

# Pop-up canopy ~3x3m and larger pit tent ~6x3m
VARIANTS = {
    # name: (fabric_tex, logo_tex, size_xy, height)
    "tent_blank_3x3": ("tent_fabric.png", "tent_logo.png", (3.0, 3.0), 2.4),
    "tent_blank_6x3": ("tent_fabric.png", "tent_logo.png", (6.0, 3.0), 2.6),
    "tent_orange_3x3": ("tent_fabric_orange.png", "tent_logo.png", (3.0, 3.0), 2.4),
    "tent_blue_3x3": ("tent_fabric_blue.png", "tent_logo.png", (3.0, 3.0), 2.4),
    "tent_white_3x3": ("tent_fabric_white.png", "tent_logo.png", (3.0, 3.0), 2.4),
    "tent_black_6x3": ("tent_fabric_black.png", "tent_logo.png", (6.0, 3.0), 2.6),
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


def make_mat(name, color, roughness=0.75, metallic=0.0, image_path=None):
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


def build_tent(fabric_tex, logo_tex, size_xy, height):
    root = bpy.data.objects.new("tent_root", None)
    bpy.context.scene.collection.objects.link(root)

    sx, sy = size_xy
    half_x, half_y = sx / 2, sy / 2
    pole_r = 0.03
    eave_z = height * 0.78
    peak_z = height

    fabric = make_mat("TENT_fabric", (0.9, 0.9, 0.9), 0.8, 0.0, TEX / fabric_tex)
    logo_m = make_mat("TENT_logo", (0.75, 0.75, 0.75), 0.7, 0.0, TEX / logo_tex)
    pole_m = make_mat("TENT_pole", (0.2, 0.2, 0.2), 0.35, 0.7, TEX / "tent_pole.png")

    parts = []

    # 4 corner poles
    for i, (x, y) in enumerate(
        [(-half_x, -half_y), (half_x, -half_y), (half_x, half_y), (-half_x, half_y)]
    ):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=10, radius=pole_r, depth=eave_z, location=(x, y, eave_z / 2)
        )
        pole = bpy.context.active_object
        pole.name = f"pole_{i}"
        apply_object(pole)
        pole.data.materials.append(pole_m)
        parts.append(pole)

    # Roof: peaked canopy — four sloped panels as thin boxes approx, or one folded mesh
    # Simple: flat-ish roof with raised center ridge using two panels meeting at peak
    # Front-back ridge along X
    for side, ysign in (("F", -1), ("B", 1)):
        # panel center
        y_mid = ysign * (half_y / 2)
        # create a grid plane and move verts
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y_mid, (eave_z + peak_z) / 2))
        panel = bpy.context.active_object
        panel.name = f"roof_{side}"
        panel.scale = (sx * 1.02, half_y * 1.02, 1)
        apply_object(panel)
        # tilt toward peak (center y=0 higher)
        for v in panel.data.vertices:
            # local y: negative toward outside for F (ysign=-1 means panel in -Y half)
            # After apply, verts in world-ish local
            # Raise edge closer to center (y near 0)
            # panel spans y from ~0 to ysign*half_y
            pass
        # easier approach: rotate panel
        angle = math.atan2(peak_z - eave_z, half_y)
        panel.rotation_euler[0] = -ysign * angle
        # position so outer edge at eave, inner at peak
        # outer edge y = ysign * half_y, z = eave; center edge y=0, z=peak
        # after rotation around X through panel center...
        panel.location = (0, ysign * half_y / 2, (eave_z + peak_z) / 2)
        apply_object(panel)
        # Solidify for thickness
        mod = panel.modifiers.new("Solid", type="SOLIDIFY")
        mod.thickness = 0.03
        bpy.context.view_layer.objects.active = panel
        panel.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        panel.data.materials.append(fabric)
        uv_smart(panel)
        parts.append(panel)

    # Side valance strips (short walls hanging) — optional open sides, just small skirt
    for i, (x, y, rot) in enumerate(
        [
            (0, -half_y, 0),
            (0, half_y, 0),
            (-half_x, 0, math.radians(90)),
            (half_x, 0, math.radians(90)),
        ]
    ):
        length = sx if i < 2 else sy
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, eave_z - 0.15))
        skirt = bpy.context.active_object
        skirt.name = f"skirt_{i}"
        if i < 2:
            skirt.scale = (length * 1.02, 0.025, 0.30)
        else:
            skirt.scale = (0.025, length * 1.02, 0.30)
        apply_object(skirt)
        skirt.data.materials.append(fabric)
        uv_smart(skirt)
        parts.append(skirt)

    # Logo banner on front skirt / peak face
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -half_y - 0.04, eave_z - 0.05))
    banner = bpy.context.active_object
    banner.name = "tent_logo_banner"
    banner.scale = (min(sx * 0.7, 3.5), 0.02, 0.55)
    apply_object(banner)
    banner.data.materials.append(logo_m)
    uv_smart(banner)
    parts.append(banner)

    # Cross beams at top (visual)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=pole_r * 0.7, depth=sx, location=(0, 0, eave_z)
    )
    beam = bpy.context.active_object
    beam.name = "beam_x"
    beam.rotation_euler[1] = math.radians(90)
    apply_object(beam)
    beam.data.materials.append(pole_m)
    parts.append(beam)

    for p in parts:
        p.parent = root
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
    needed = {"tent_fabric.png", "tent_logo.png", "tent_pole.png"}
    for _, (fab, logo, _, _) in VARIANTS.items():
        needed.add(fab)
        needed.add(logo)
    for f in needed:
        if not (TEX / f).exists():
            print(f"Missing {f}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    for name, (fab, logo, size, h) in VARIANTS.items():
        clear_all()
        root = build_tent(fab, logo, size, h)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            first = False
        export_dae(root, name)

    # ensure masters present
    for master in ("tent_fabric.png", "tent_logo.png", "tent_pole.png"):
        src = TEX / master
        if src.exists():
            (OUT / master).write_bytes(src.read_bytes())

    print(f"DONE: exported {len(VARIANTS)} tents")


if __name__ == "__main__":
    main()
