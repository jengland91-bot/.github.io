#!/usr/bin/env python3
"""
Build a Blender terrain mesh from export/heightmap_8bit.png (or 16-bit).

  /tmp/blender-4.2.9-linux-x64/blender --background --python apply_heightmap_blender.py

Creates:
  export/parker_terrain.blend
  export/parker_terrain.dae   (optional TSStatic mega-mesh — usually use as heightmap in BeamNG instead)
  export/parker_terrain_preview.png  (top-down render optional — skipped in background)
"""

from __future__ import annotations

from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
EXPORT = ROOT / "export"
HEIGHT = EXPORT / "heightmap_8bit.png"
# Prefer 16-bit if Blender can load it
HEIGHT16 = EXPORT / "heightmap_16bit.png"

# Parker-scale desert chunk (meters). Adjust to your map size.
SIZE_M = 1024.0
HEIGHT_M = 80.0  # peak-to-valley exaggeration
SUBDIV = 255  # grid resolution (verts per side - 1). 255 → 256×256 verts


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0

    hm = HEIGHT16 if HEIGHT16.exists() else HEIGHT
    if not hm.exists():
        raise SystemExit(f"Missing heightmap — run rgb_to_heightmap.py first ({hm})")

    # Plane covering SIZE_M × SIZE_M, origin at center, Z-up
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=SUBDIV,
        y_subdivisions=SUBDIV,
        size=SIZE_M,
        location=(0, 0, 0),
    )
    terrain = bpy.context.active_object
    terrain.name = "parker_terrain"

    # Load height image
    img = bpy.data.images.load(str(hm))
    img.colorspace_settings.name = "Non-Color"

    tex = bpy.data.textures.new("HeightTex", type="IMAGE")
    tex.image = img

    disp = terrain.modifiers.new("Displace", type="DISPLACE")
    disp.texture = tex
    disp.texture_coords = "UV"
    disp.mid_level = 0.0
    disp.strength = HEIGHT_M

    # Ensure UVs 0–1 on grid
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    # Grid already has generated UVs in recent Blender — project bounds
    me = terrain.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    # Map by vertex XY
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            co = me.vertices[vi].co
            u = (co.x / SIZE_M) + 0.5
            v = (co.y / SIZE_M) + 0.5
            uv[li].uv = (u, v)

    bpy.ops.object.modifier_apply(modifier=disp.name)

    # Drop so lowest point sits near Z=0
    zs = [v.co.z for v in me.vertices]
    zmin = min(zs)
    for v in me.vertices:
        v.co.z -= zmin
    me.update()

    EXPORT.mkdir(parents=True, exist_ok=True)
    blend = EXPORT / "parker_terrain.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    print(f"wrote {blend}")

    # Also export DAE (large) for reference / sculpt base — BeamNG levels usually
    # use the heightmap PNG/RAW in Terrain Block, not this mesh.
    dae = EXPORT / "parker_terrain_mesh.dae"
    bpy.ops.object.select_all(action="DESELECT")
    terrain.select_set(True)
    bpy.context.view_layer.objects.active = terrain
    bpy.ops.wm.collada_export(
        filepath=str(dae),
        selected=True,
        apply_modifiers=True,
        use_texture_copies=True,
        export_global_forward_selection="Y",
        export_global_up_selection="Z",
        apply_global_orientation=True,
    )
    print(f"wrote {dae}")
    print("DONE blender terrain")


if __name__ == "__main__":
    main()
