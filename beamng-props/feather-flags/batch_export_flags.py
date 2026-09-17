"""
Build blank feather/teardrop flags and export Collada (.dae).
Run:
  blender --background --python batch_export_flags.py
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
BLEND_OUT = ROOT / "export" / "feather_flags.blend"

# Real-ish event feather flag ~3.5–4.5m tall including pole
FLAG_HEIGHT = 3.6
FLAG_WIDTH = 0.85
FLAG_THICK = 0.012
POLE_RADIUS = 0.018
POLE_HEIGHT = 3.75

VARIANTS = {
    "featherflag_blank_orange": "flag_blank_orange.png",
    "featherflag_blank_black": "flag_blank_black.png",
    "featherflag_blank_white": "flag_blank_white.png",
    "featherflag_blank_navy": "flag_blank_navy.png",
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


def make_mat(name, color, roughness=0.65, metallic=0.0, image_path=None):
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
    # cloth-ish: slight sheen if available
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.2
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def feather_outline(height=FLAG_HEIGHT, width=FLAG_WIDTH, segments=24):
    """
    2D outline in XZ (Y=thickness later).
    Pole sleeve on -X (left). Feather curves to the right and tapers at top.
    Bottom at z=0.15 (above ground spike), top at z=height.
    """
    z0 = 0.18
    z1 = height
    pts = []

    # Left edge (straight pole sleeve) bottom -> top
    left_x = 0.0
    for i in range(segments + 1):
        t = i / segments
        z = z0 + (z1 - z0) * t
        pts.append((left_x, z))

    # Top curve from pole tip out to feather tip, then down the free edge
    # Free-edge samples from top to bottom
    for i in range(1, segments + 1):
        t = i / segments  # 0 at top ... 1 at bottom
        z = z1 - (z1 - z0) * t
        # Width profile: narrow near top tip, widest mid-upper, taper a bit at bottom
        # Classic feather: max width ~60% down from tip is still wide, tip curves in
        tip_blend = max(0.0, 1.0 - (1.0 - t) * 3.5) if t < 0.22 else 1.0
        # smoother tip using sine
        if t < 0.2:
            tip_factor = math.sin((t / 0.2) * math.pi / 2)
        else:
            tip_factor = 1.0
        # slight bottom inward curve
        bottom_factor = 1.0
        if t > 0.85:
            bottom_factor = 1.0 - ((t - 0.85) / 0.15) * 0.12
        x = width * tip_factor * bottom_factor
        # add gentle S on free edge
        x *= 0.92 + 0.08 * math.sin(t * math.pi)
        pts.append((x, z))

    return pts  # closed ring: up left edge, down right edge


def create_feather_mesh(name="feather_flag"):
    outline = feather_outline()
    # Build thin prism: front and back rings
    half_t = FLAG_THICK / 2
    verts = []
    # front (y=-half), back (y=+half)
    for x, z in outline:
        verts.append((x, -half_t, z))
    for x, z in outline:
        verts.append((x, half_t, z))

    n = len(outline)
    faces = []
    # front face (reverse winding for outward -Y)
    faces.append(list(reversed(range(0, n))))
    # back face
    faces.append(list(range(n, 2 * n)))
    # side quads
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, j + n, i + n])

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Recalc normals
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # UV unwrap: project from front so logo maps cleanly
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Compute bounds of outline for UV
    xs = [p[0] for p in outline]
    zs = [p[1] for p in outline]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)

    # Map each vert UV by its x/z
    vert_uv = {}
    for i, (x, z) in enumerate(outline):
        u = (x - min_x) / (max_x - min_x) if max_x != min_x else 0.0
        v = (z - min_z) / (max_z - min_z) if max_z != min_z else 0.0
        vert_uv[i] = (u, v)
        vert_uv[i + n] = (u, v)

    for face in bm.faces:
        for loop in face.loops:
            vi = loop.vert.index
            if vi in vert_uv:
                loop[uv_layer].uv = vert_uv[vi]

    bm.to_mesh(mesh)
    bm.free()
    obj.select_set(False)
    return obj


def create_pole():
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=POLE_RADIUS,
        depth=POLE_HEIGHT,
        location=(0.0, 0.0, POLE_HEIGHT / 2),
    )
    pole = bpy.context.active_object
    pole.name = "flag_pole"
    # slight tip above flag
    return pole


def create_base_spike():
    bpy.ops.mesh.primitive_cone_add(
        vertices=8,
        radius1=0.05,
        depth=0.22,
        location=(0.0, 0.0, -0.05),
    )
    spike = bpy.context.active_object
    spike.name = "flag_spike"
    return spike


def build_flag(tex_name: str):
    clear_all()
    flag = create_feather_mesh("feather_cloth")
    pole = create_pole()
    spike = create_base_spike()

    flag_mat = make_mat(
        "FF_cloth",
        (0.9, 0.4, 0.15),
        roughness=0.7,
        image_path=TEX / tex_name,
    )
    flag.data.materials.append(flag_mat)

    pole_mat = make_mat(
        "FF_pole",
        (0.12, 0.12, 0.12),
        roughness=0.35,
        metallic=0.7,
        image_path=TEX / "flag_pole.png" if (TEX / "flag_pole.png").exists() else None,
    )
    pole.data.materials.append(pole_mat)
    spike.data.materials.append(pole_mat)

    # Parent under an empty at ground origin for easy placement
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
    root = bpy.context.active_object
    root.name = "featherflag_root"

    # Align flag so pole sleeve sits on pole (+X out from pole)
    flag.location = (POLE_RADIUS * 0.6, 0.0, 0.0)
    pole.parent = root
    spike.parent = root
    flag.parent = root

    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    return root, flag


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root


def export_dae(root, name: str):
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
    for tex in VARIANTS.values():
        if not (TEX / tex).exists():
            print(f"Missing {tex}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    for name, tex in VARIANTS.items():
        root, _flag = build_flag(tex)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
            first = False
        export_dae(root, name)

    print(f"DONE: exported {len(VARIANTS)} feather flags")


if __name__ == "__main__":
    main()
