"""
Build low-poly desert rocks in several sizes/shapes.
Run:
  blender --background --python batch_export_rocks.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures"
OUT = ROOT / "export" / "dae"
BLEND_OUT = ROOT / "export" / "rocks.blend"

# name -> (texture, scale_xyz approx meters, seed)
ROCKS = {
    "rock_small_tan_a": ("rock_tan.png", (0.55, 0.45, 0.35), 11),
    "rock_small_tan_b": ("rock_tan.png", (0.40, 0.50, 0.30), 12),
    "rock_small_red_a": ("rock_red.png", (0.50, 0.40, 0.32), 13),
    "rock_med_tan_a": ("rock_tan.png", (1.4, 1.1, 0.85), 21),
    "rock_med_tan_b": ("rock_tan.png", (1.2, 1.5, 0.95), 22),
    "rock_med_gray_a": ("rock_gray.png", (1.3, 1.0, 0.90), 23),
    "rock_med_red_a": ("rock_red.png", (1.5, 1.2, 1.0), 24),
    "rock_large_tan_a": ("rock_tan.png", (3.2, 2.4, 1.8), 31),
    "rock_large_gray_a": ("rock_gray.png", (2.8, 3.0, 2.0), 32),
    "rock_large_dark_a": ("rock_dark.png", (3.5, 2.6, 2.2), 33),
    "rock_boulder_tan": ("rock_tan.png", (5.0, 4.2, 3.0), 41),
    "rock_boulder_red": ("rock_red.png", (4.5, 4.8, 3.2), 42),
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
    bsdf.inputs["Roughness"].default_value = 0.92
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def build_rock(tex_name: str, scale, seed: int):
    rng = random.Random(seed)
    root = bpy.data.objects.new("rock_root", None)
    bpy.context.scene.collection.objects.link(root)

    # Icosphere base, then displace verts for rocky silhouette
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.5, location=(0, 0, 0.5))
    rock = bpy.context.active_object
    rock.name = "rock_mesh"

    # Non-uniform scale for oblong rocks
    rock.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Displace vertices in local space
    mesh = rock.data
    for v in mesh.vertices:
        # flatten bottom a bit so it sits on ground
        noise = (
            rng.uniform(-0.12, 0.18)
            + 0.08 * math.sin(v.co.x * 7.1 + seed)
            + 0.06 * math.cos(v.co.y * 5.3 - seed)
        )
        # push outward mostly
        nrm = v.co.normalized() if v.co.length > 1e-6 else Vector((0, 0, 1))
        v.co += nrm * noise * (0.35 + 0.25 * abs(nrm.z))
        if v.co.z < 0.02:
            v.co.z = rng.uniform(0.0, 0.04)

    mesh.update()

    # Recalc normals + UV
    bpy.context.view_layer.objects.active = rock
    rock.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.03)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Sit on ground: move so lowest z = 0
    min_z = min((rock.matrix_world @ v.co).z for v in rock.data.vertices)
    rock.location.z -= min_z

    mat = make_mat(f"ROCK_{seed}", (0.5, 0.4, 0.3), TEX / tex_name)
    rock.data.materials.append(mat)
    rock.parent = root
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
    for tex, _, _ in ROCKS.values():
        if not (TEX / tex).exists():
            print(f"Missing {tex}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True
    for name, (tex, scale, seed) in ROCKS.items():
        clear_all()
        root = build_rock(tex, scale, seed)
        if first:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
            first = False
        export_dae(root, name)

    print(f"DONE: exported {len(ROCKS)} rocks")


if __name__ == "__main__":
    main()
