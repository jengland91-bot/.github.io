"""
Shared BeamNG static-mesh export helpers.

Hierarchy (required by Torque/BeamNG Collada importer):

  base00
    start01          <- visual meshes parented here (LOD names end with letter+pixels, e.g. _a800)
    collision-1      <- optional empty
      Colmesh_*-1    <- dedicated collision meshes (-1 = non-rendered)

Rules:
  - Collision meshes MUST be far simpler than visuals (boxes/cylinders, no bevels)
  - Prefer multiple convex Colmesh pieces over one concave hull (drive-through arches, tents)
  - Keep K-rail / tire wall colliders bevel-free and low-face so bumpers slide
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


def new_empty(name: str, parent=None):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0.25
    bpy.context.scene.collection.objects.link(empty)
    if parent is not None:
        empty.parent = parent
    return empty


def make_collision_mat():
    """Invisible-ish material for colliders (engine ignores render via -1 suffix anyway)."""
    name = "Colmesh_Material"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 1.0, 1.0)  # magenta debug
    bsdf.inputs["Alpha"].default_value = 0.15
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 1.0
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def apply_object(obj):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


def box_collider(name: str, loc, size, parent=None):
    """
    Axis-aligned box collider. size = full dimensions (x,y,z).
    NO bevels. Named Colmesh_<name>-1
    """
    obj_name = f"Colmesh_{name}-1"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = obj_name
    obj.data.name = obj_name
    obj.scale = size
    apply_object(obj)
    obj.data.materials.append(make_collision_mat())
    if parent is not None:
        obj.parent = parent
    return obj


def cylinder_collider(name: str, loc, radius, depth, parent=None, verts=8, rot=(0, 0, 0)):
    """Simple cylinder/capsule-ish collider (8 sides default). NO bevels."""
    obj_name = f"Colmesh_{name}-1"
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc
    )
    obj = bpy.context.active_object
    obj.name = obj_name
    obj.data.name = obj_name
    obj.rotation_euler = rot
    apply_object(obj)
    obj.data.materials.append(make_collision_mat())
    if parent is not None:
        obj.parent = parent
    return obj


def wrap_beamng_hierarchy(visual_objects, collider_builders, visual_lod_name: str = "mesh_a800"):
    """
    visual_objects: list of Blender objects (meshes) that are the visible prop
    collider_builders: list of callables taking (collision_parent) and creating Colmesh_*-1 children

    Returns base00 empty (export root).
    """
    # Unparent visuals from any old root
    for obj in visual_objects:
        obj.parent = None

    base00 = new_empty("base00")
    start01 = new_empty("start01", parent=base00)
    collision = new_empty("collision-1", parent=base00)

    # Parent visuals under start01; ensure LOD-style name on a root visual empty if many parts
    if len(visual_objects) == 1:
        vis = visual_objects[0]
        # Rename mesh object for LOD
        base = visual_lod_name
        vis.name = base
        if vis.data:
            vis.data.name = base
        vis.parent = start01
    else:
        # Keep individual names but parent all to start01; also create a named empty holder
        holder = new_empty(visual_lod_name, parent=start01)
        for obj in visual_objects:
            obj.parent = holder

    for builder in collider_builders:
        builder(collision)

    return base00


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    # children_recursive may not include nested empties' meshes on older API — walk manually
    def walk(o):
        for c in o.children:
            c.select_set(True)
            walk(c)

    walk(root)
    bpy.context.view_layer.objects.active = root


def export_dae(root, filepath: Path):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    select_hierarchy(root)
    bpy.ops.wm.collada_export(
        filepath=str(filepath),
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
    print(f"exported {filepath}")


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    # keep images/materials that scripts may reuse across exports in one blender run
