"""
Shared BeamNG static-mesh export helpers.

Hierarchy (required by Torque/BeamNG Collada importer):

  base00
    start01
      <name>_a800          <- LOD0 close-up (full detail)
      <name>_a200          <- LOD1 medium (~50% tris via Decimate)
      <name>_a50           <- LOD2 far (crossed-card billboard, ~8 tris)
      nulldetail20         <- stop rendering when tiny on screen
    collision-1
      Colmesh_*-1          <- dedicated collision (-1 = non-rendered)

Rules:
  - Always Apply All Transforms (location + rotation + scale) before export
  - Origin / pivot at bottom-center (terrain snap / foliage flush)
  - Collision meshes MUST be far simpler than visuals (boxes/cylinders, no bevels)
  - Prefer multiple convex Colmesh pieces over one concave hull
  - LOD pixel sizes MUST be preceded by a letter (_a800 not _800)
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


# Default LOD switch sizes (screen pixels). Larger = used when closer.
LOD0_PX = 800  # close-up / full detail
LOD1_PX = 200  # medium
LOD2_PX = 50   # far billboard
NULL_DETAIL_PX = 20  # cull


def new_empty(name: str, parent=None):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0.25
    bpy.context.scene.collection.objects.link(empty)
    if parent is not None:
        empty.parent = parent
    return empty


def make_collision_mat():
    """Magenta debug material for colliders (engine skips render via -1 suffix)."""
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
    bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 1.0, 1.0)
    bsdf.inputs["Alpha"].default_value = 0.15
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 1.0
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def apply_rot_scale(obj):
    """Apply rotation + scale only (safe while building parts before final pivot)."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)


# Back-compat alias used by rebuild scripts
apply_object = apply_rot_scale


def apply_all_transforms(obj):
    """Ctrl+A → All Transforms (location, rotation, scale). Prevents in-engine scale bugs."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)


def world_bbox(objs):
    """Combined world-space AABB for a list of mesh objects. Returns (min, max) Vectors."""
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mins.x = min(mins.x, w.x)
            mins.y = min(mins.y, w.y)
            mins.z = min(mins.z, w.z)
            maxs.x = max(maxs.x, w.x)
            maxs.y = max(maxs.y, w.y)
            maxs.z = max(maxs.z, w.z)
    return mins, maxs


def origin_to_base_center(objs):
    """
    Set a shared bottom-center pivot for the prop group, then move so origin is at world (0,0,0).
    Flush with ground for terrain snaps / foliage tools.
    """
    mesh_objs = [o for o in objs if o.type == "MESH"]
    if not mesh_objs:
        return

    for obj in mesh_objs:
        obj.parent = None
        apply_rot_scale(obj)

    mins, maxs = world_bbox(mesh_objs)
    pivot = Vector(((mins.x + maxs.x) * 0.5, (mins.y + maxs.y) * 0.5, mins.z))

    # Shift mesh data so pivot becomes local origin, then zero object location
    for obj in mesh_objs:
        inv = obj.matrix_world.inverted()
        local_pivot = inv @ pivot
        for v in obj.data.vertices:
            v.co -= local_pivot
        obj.data.update()
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        apply_all_transforms(obj)


def join_meshes(objs, name: str):
    """Join mesh objects into one. Returns the joined object (or None)."""
    mesh_objs = [o for o in objs if o.type == "MESH"]
    if not mesh_objs:
        return None
    if len(mesh_objs) == 1:
        obj = mesh_objs[0]
        obj.name = name
        if obj.data:
            obj.data.name = name
        return obj

    bpy.ops.object.select_all(action="DESELECT")
    for o in mesh_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objs[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = name
    if joined.data:
        joined.data.name = name
    return joined


def duplicate_object(obj, name: str):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    dup = bpy.context.active_object
    dup.name = name
    if dup.data:
        dup.data = dup.data.copy()
        dup.data.name = name
    return dup


def apply_decimate(obj, ratio: float = 0.5):
    """~50% polygon reduction for LOD1 via Decimate, then apply modifier."""
    ratio = max(0.05, min(1.0, ratio))
    mod = obj.modifiers.new(name="LOD_Decimate", type="DECIMATE")
    mod.ratio = ratio
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def make_billboard(name: str, mins: Vector, maxs: Vector, materials=None):
    """
    LOD2 far mesh: crossed-card planes (~8 tris) covering the prop bbox.
    Two quads through bottom-center, facing +X and +Y.
    """
    cx = (mins.x + maxs.x) * 0.5
    cy = (mins.y + maxs.y) * 0.5
    cz = (mins.z + maxs.z) * 0.5
    w = max(maxs.x - mins.x, maxs.y - mins.y, 0.05)
    h = max(maxs.z - mins.z, 0.05)
    # Slightly pad so silhouette reads at distance
    w *= 1.05
    h *= 1.02
    hw, hh = w * 0.5, h * 0.5

    mesh = bpy.data.meshes.new(name)
    # Two crossed quads (8 verts, 4 faces / 8 tris)
    verts = [
        # plane facing +Y (in XZ)
        (cx - hw, cy, cz - hh),
        (cx + hw, cy, cz - hh),
        (cx + hw, cy, cz + hh),
        (cx - hw, cy, cz + hh),
        # plane facing +X (in YZ)
        (cx, cy - hw, cz - hh),
        (cx, cy + hw, cz - hh),
        (cx, cy + hw, cz + hh),
        (cx, cy - hw, cz + hh),
    ]
    faces = [(0, 1, 2, 3), (4, 5, 6, 7)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    # Simple UVs
    mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active.data
    # Each face 4 loops
    for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)] * 2):
        uv[i].uv = (u, v)

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if materials:
        for m in materials:
            if m is not None:
                obj.data.materials.append(m)
                break
    else:
        mat = bpy.data.materials.get("LOD_Billboard")
        if mat is None:
            mat = bpy.data.materials.new("LOD_Billboard")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.45, 0.42, 0.38, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.9
        obj.data.materials.append(mat)
    apply_all_transforms(obj)
    return obj


def box_collider(name: str, loc, size, parent=None):
    """Axis-aligned box collider. size = full dimensions (x,y,z). NO bevels."""
    obj_name = f"Colmesh_{name}-1"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = obj_name
    obj.data.name = obj_name
    obj.scale = size
    apply_rot_scale(obj)
    obj.data.materials.append(make_collision_mat())
    if parent is not None:
        obj.parent = parent
    return obj


def cylinder_collider(name: str, loc, radius, depth, parent=None, verts=8, rot=(0, 0, 0)):
    """Simple cylinder collider (8 sides default). NO bevels."""
    obj_name = f"Colmesh_{name}-1"
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc
    )
    obj = bpy.context.active_object
    obj.name = obj_name
    obj.data.name = obj_name
    obj.rotation_euler = rot
    apply_rot_scale(obj)
    obj.data.materials.append(make_collision_mat())
    if parent is not None:
        obj.parent = parent
    return obj


def wrap_beamng_hierarchy(
    visual_objects,
    collider_builders,
    visual_lod_name: str = "mesh_a800",
    lod_px=(LOD0_PX, LOD1_PX, LOD2_PX),
    null_detail: int = NULL_DETAIL_PX,
    decimate_ratio: float = 0.5,
    make_far_billboard: bool = True,
):
    """
    Prepare visuals (base pivot + all transforms), build LOD0/1/2 chain, attach colliders.

    visual_lod_name: preferred base name; trailing _aNNN is stripped and re-applied per LOD.
    Colliders are built in the same pre-pivot space as visuals, then shifted together so
    physics and visuals share the bottom-center origin.

    Returns base00 empty (export root).
    """
    # Strip accidental LOD suffix from caller name
    base_name = visual_lod_name
    for marker in ("_a800", "_a400", "_a300", "_a200", "_a100", "_a50"):
        if base_name.endswith(marker):
            base_name = base_name[: -len(marker)]
            break
    if base_name.endswith("_"):
        base_name = base_name[:-1]

    lod0_px, lod1_px, lod2_px = lod_px
    mesh_objs = [o for o in visual_objects if o is not None and o.type == "MESH"]
    for obj in mesh_objs:
        obj.parent = None
        apply_rot_scale(obj)

    base00 = new_empty("base00")
    start01 = new_empty("start01", parent=base00)
    collision = new_empty("collision-1", parent=base00)

    # Build colliders in the SAME coordinate space as the raw visuals
    for builder in collider_builders:
        builder(collision)
    col_meshes = [c for c in collision.children if c.type == "MESH"]

    # Shared bottom-center pivot for visuals + colliders, then bake to (0,0,0)
    origin_to_base_center(mesh_objs + col_meshes)

    mesh_objs = [o for o in mesh_objs if o.name in bpy.data.objects]
    if not mesh_objs:
        return base00

    # Materials for billboard tint
    mats = []
    for o in mesh_objs:
        for m in o.data.materials:
            if m and m not in mats:
                mats.append(m)

    # LOD0 — join into full-detail mesh
    lod0_name = f"{base_name}_a{lod0_px}"
    lod0 = join_meshes(mesh_objs, lod0_name)
    lod0.parent = start01
    apply_all_transforms(lod0)

    # LOD1 — ~50% decimate
    lod1_name = f"{base_name}_a{lod1_px}"
    lod1 = duplicate_object(lod0, lod1_name)
    apply_decimate(lod1, ratio=decimate_ratio)
    apply_all_transforms(lod1)
    lod1.parent = start01

    # LOD2 — crossed-card billboard
    if make_far_billboard:
        lod2_name = f"{base_name}_a{lod2_px}"
        mins, maxs = world_bbox([lod0])
        lod2 = make_billboard(lod2_name, mins, maxs, materials=mats)
        lod2.parent = start01
        apply_all_transforms(lod2)

    # Cull when tiny on screen
    if null_detail and null_detail > 0:
        new_empty(f"nulldetail{null_detail}", parent=start01)

    # Re-parent colliders (origin_to_base_center cleared parents) and bake transforms
    for c in list(bpy.data.objects):
        if c.name.startswith("Colmesh_") and c.type == "MESH":
            c.parent = collision
            apply_all_transforms(c)

    return base00


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)

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
