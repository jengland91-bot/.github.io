"""
Build stakes, caution ribbon spans, and snow fence panels.
Export Collada (.dae) for BeamNG.

Run:
  blender --background --python batch_export_barriers.py
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
BLEND_OUT = ROOT / "export" / "barriers.blend"

# Stake
STAKE_H = 1.15
STAKE_W = 0.06

# Ribbon
RIBBON_H = 0.08
RIBBON_T = 0.008
RIBBON_Z = 0.85  # height of ribbon center on stake

# Snow fence panel
SF_W = 2.0
SF_H = 1.05
SF_T = 0.04
SF_POST_W = 0.08


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


def apply_object(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def add_bevel(obj, width=0.002, segments=1):
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
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and Path(image_path).exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = load_image(Path(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def uv_smart(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)


def new_root(name):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = name
    return root


def make_stake(name, wood=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, STAKE_H / 2))
    stake = bpy.context.active_object
    stake.name = name
    stake.scale = (STAKE_W, STAKE_W, STAKE_H)
    apply_object(stake)
    add_bevel(stake, 0.002, 1)

    bpy.ops.mesh.primitive_cone_add(
        vertices=4, radius1=STAKE_W * 0.7, depth=0.16, location=(0, 0, -0.06)
    )
    tip = bpy.context.active_object
    tip.name = name + "_tip"
    tip.rotation_euler[2] = math.radians(45)
    apply_object(tip)

    if wood:
        mat = make_mat("BR_wood", (0.4, 0.25, 0.12), 0.85, 0.0, TEX / "stake_wood.png")
    else:
        mat = make_mat("BR_metal", (0.45, 0.47, 0.5), 0.35, 0.8, TEX / "stake_metal.png")
    stake.data.materials.append(mat)
    tip.data.materials.append(mat)
    uv_smart(stake)
    return stake, tip


def make_ribbon(length, tex_name, name):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(length / 2, 0, RIBBON_Z))
    rib = bpy.context.active_object
    rib.name = name
    rib.scale = (length, RIBBON_T, RIBBON_H)
    apply_object(rib)
    mat = make_mat("BR_ribbon", (0.9, 0.45, 0.1), 0.55, 0.0, TEX / tex_name)
    rib.data.materials.append(mat)
    uv_smart(rib)
    return rib


def make_snowfence_panel(tex_name, name, width=SF_W):
    # panel cloth/slats
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(width / 2, 0, SF_H / 2 + 0.05))
    panel = bpy.context.active_object
    panel.name = name + "_panel"
    panel.scale = (width - SF_POST_W * 2, SF_T, SF_H)
    apply_object(panel)
    mat = make_mat("BR_sf", (0.6, 0.4, 0.2), 0.75, 0.0, TEX / tex_name)
    panel.data.materials.append(mat)
    uv_smart(panel)

    # end posts
    posts = []
    for i, x in enumerate((SF_POST_W / 2, width - SF_POST_W / 2)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, (SF_H + 0.15) / 2))
        post = bpy.context.active_object
        post.name = f"{name}_post_{i}"
        post.scale = (SF_POST_W, SF_POST_W, SF_H + 0.15)
        apply_object(post)
        wood = make_mat("BR_sf_post", (0.35, 0.22, 0.12), 0.85, 0.0, TEX / "stake_wood.png")
        post.data.materials.append(wood)
        posts.append(post)

        bpy.ops.mesh.primitive_cone_add(
            vertices=4, radius1=SF_POST_W * 0.65, depth=0.18, location=(x, 0, -0.07)
        )
        tip = bpy.context.active_object
        tip.name = f"{name}_tip_{i}"
        tip.rotation_euler[2] = math.radians(45)
        apply_object(tip)
        tip.data.materials.append(wood)
        posts.append(tip)

    return panel, posts


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


def build_and_export(name, builder):
    clear_all()
    root = builder()
    export_dae(root, name)
    return root


def main():
    needed = [
        "stake_wood.png",
        "stake_metal.png",
        "ribbon_caution.png",
        "ribbon_orange.png",
        "ribbon_yellow_black.png",
        "snowfence_wood.png",
        "snowfence_orange.png",
    ]
    for n in needed:
        if not (TEX / n).exists():
            print(f"Missing {n}", file=sys.stderr)
            sys.exit(1)

    reset_scene()
    first = True

    exports = []

    # --- single stakes ---
    def stake_wood():
        root = new_root("stake_wood_root")
        stake, tip = make_stake("stake_wood", wood=True)
        stake.parent = root
        tip.parent = root
        return root

    def stake_metal():
        root = new_root("stake_metal_root")
        stake, tip = make_stake("stake_metal", wood=False)
        stake.parent = root
        tip.parent = root
        return root

    exports.append(("stake_wood", stake_wood))
    exports.append(("stake_metal", stake_metal))

    # --- ribbon-only spans (place between your own stakes) ---
    for length, label in ((2.0, "2m"), (3.0, "3m"), (5.0, "5m")):
        for tex, tag in (
            ("ribbon_caution.png", "caution"),
            ("ribbon_orange.png", "orange"),
            ("ribbon_yellow_black.png", "yellow"),
        ):

            def make(length=length, tex=tex, tag=tag, label=label):
                root = new_root(f"ribbon_{tag}_{label}_root")
                rib = make_ribbon(length, tex, f"ribbon_{tag}_{label}")
                # origin at left end so it stretches along +X from a stake
                rib.location.x = length / 2
                # re-center mesh: move object so left end at 0
                # after apply, location is center; shift root empty instead
                rib.parent = root
                return root

            exports.append((f"ribbon_{tag}_{label}", make))

    # --- stake + ribbon + stake prefabs ---
    for length, label in ((2.0, "2m"), (3.0, "3m")):
        for tex, tag in (("ribbon_caution.png", "caution"), ("ribbon_orange.png", "orange")):

            def make(length=length, tex=tex, tag=tag, label=label):
                root = new_root(f"stake_ribbon_{tag}_{label}_root")
                s1, t1 = make_stake("stake_L", wood=True)
                s1.parent = root
                t1.parent = root
                s2, t2 = make_stake("stake_R", wood=True)
                s2.location.x = length
                t2.location.x = length
                s2.parent = root
                t2.parent = root
                inset = STAKE_W
                span = length - inset
                rib = make_ribbon(span, tex, f"ribbon_{tag}")
                rib.location.x = inset / 2 + span / 2
                rib.parent = root
                return root

            exports.append((f"stake_ribbon_{tag}_{label}", make))

    # --- snow fence panels ---
    for tex, tag in (("snowfence_wood.png", "wood"), ("snowfence_orange.png", "orange")):

        def make(tex=tex, tag=tag):
            root = new_root(f"snowfence_{tag}_root")
            panel, posts = make_snowfence_panel(tex, f"snowfence_{tag}", SF_W)
            panel.parent = root
            for p in posts:
                p.parent = root
            return root

        exports.append((f"snowfence_{tag}_2m", make))

    # half panel for tight spots
    def snowfence_wood_1m():
        root = new_root("snowfence_wood_1m_root")
        panel, posts = make_snowfence_panel("snowfence_wood.png", "snowfence_wood_1m", 1.0)
        panel.parent = root
        for p in posts:
            p.parent = root
        return root

    exports.append(("snowfence_wood_1m", snowfence_wood_1m))

    for i, (name, builder) in enumerate(exports):
        clear_all()
        root = builder()
        if i == 0:
            BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
            print(f"saved {BLEND_OUT}")
        export_dae(root, name)

    print(f"DONE: exported {len(exports)} barrier props")


if __name__ == "__main__":
    main()
