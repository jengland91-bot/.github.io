"""
Build concrete K-rail / Jersey barrier sections for BeamNG.
Blank/swappable concrete texture + stripe / color presets.

Typical NJ barrier profile, modular lengths.

Run:
  blender --background --python batch_export_krails.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "k_rails.blend"

# Cross-section (X = lateral, Z = up), extruded along Y for length
# Approximate Jersey barrier: wide base, tapered mid, narrow top
# Heights ~0.81 m (32"), base width ~0.61 m
PROFILE = [
    # left side bottom -> top, then right side top -> bottom
    (-0.305, 0.00),
    (-0.305, 0.08),
    (-0.22, 0.08),
    (-0.15, 0.45),
    (-0.10, 0.45),
    (-0.075, 0.81),
    (0.075, 0.81),
    (0.10, 0.45),
    (0.15, 0.45),
    (0.22, 0.08),
    (0.305, 0.08),
    (0.305, 0.00),
]

VARIANTS = {
    # name: (texture, length_m)
    "krail_blank_2m": ("krail.png", 2.0),
    "krail_blank_3m": ("krail.png", 3.0),
    "krail_blank_6m": ("krail.png", 6.0),
    "krail_concrete_2m": ("krail_concrete.png", 2.0),
    "krail_concrete_3m": ("krail_concrete.png", 3.0),
    "krail_stripe_2m": ("krail_stripe.png", 2.0),
    "krail_stripe_3m": ("krail_stripe.png", 3.0),
    "krail_orange_2m": ("krail_orange.png", 2.0),
    "krail_orange_3m": ("krail_orange.png", 3.0),
    "krail_white_2m": ("krail_white.png", 2.0),
    "krail_dark_2m": ("krail_dark.png", 2.0),
    "krail_dark_3m": ("krail_dark.png", 3.0),
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


def make_mat(name, color, image_path=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def build_krail(length: float, tex_name: str):
    root = bpy.data.objects.new("krail_root", None)
    bpy.context.scene.collection.objects.link(root)

    # Build mesh with bmesh: front profile + back profile extruded along Y
    mesh = bpy.data.meshes.new("krail_mesh")
    obj = bpy.data.objects.new("krail", mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()
    # Two rings of verts
    y0, y1 = 0.0, length
    front = [bm.verts.new((x, y0, z)) for x, z in PROFILE]
    back = [bm.verts.new((x, y1, z)) for x, z in PROFILE]
    bm.verts.ensure_lookup_table()
    n = len(PROFILE)

    # Cap faces
    bm.faces.new(list(reversed(front)))  # outward -Y
    bm.faces.new(back)

    # Side quads
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([front[i], front[j], back[j], back[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Bevel edges slightly for less razor-sharp concrete
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = 0.012
    mod.segments = 2
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(30)
    bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")

    mat = make_mat("KRAIL", (0.65, 0.64, 0.60), TEX / tex_name)
    obj.data.materials.append(mat)

    # Origin at ground center of section (Y along length, start at 0)
    # Move so geometric center X=0 already; shift empty at start
    obj.parent = root
    # Place root so barrier sits centered optionally — keep left end at 0 for modular stacking along +Y
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
    for tex, _ in VARIANTS.values():
        if not (TEX / tex).exists():
            print(f"Missing {tex}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    for name, (tex, length) in VARIANTS.items():
        clear_all()
        root = build_krail(length, tex)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
            first = False
        export_dae(root, name)

    # Ensure master blank texture name present for easy recolor of blank variants
    src = TEX / "krail.png"
    if src.exists():
        (OUT / "krail.png").write_bytes(src.read_bytes())

    print(f"DONE: exported {len(VARIANTS)} k-rails")


if __name__ == "__main__":
    main()
