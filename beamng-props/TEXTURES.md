# Texture Atlasing & ORM (Draw Calls)

Desert maps show hundreds of props at once. **Unique materials / textures on screen** (draw calls) often cost more than polygon count.

## Atlases (2048×2048)

| Atlas | Contents | Albedo | ORM |
|-------|----------|--------|-----|
| **Sign** | Miles 1–100, course arrows, danger, laps, exits, wood, metal | `atlases/sign_atlas_2048.png` | `atlases/sign_orm_2048.png` |
| **Vegetation** | Rocks + creosote / saguaro / bush / sand tiles | `atlases/vegetation_atlas_2048.png` | `atlases/vegetation_orm_2048.png` |

UV rectangles: `*_atlas_layout.json` (Blender V=0 at bottom).

All mile / course / lap / exit sign meshes share **one** `ParkerSignAtlas` material — different UV islands on the same sheet. Rocks share **one** `ParkerVegAtlas` material.

## ORM channel packing

One RGB texture instead of three grayscale maps:

| Channel | Map |
|---------|-----|
| **R** | Ambient Occlusion (AO) |
| **G** | Roughness |
| **B** | Metallic |

Blender Principled setup (also in rebuild): albedo × AO → Base Color; G → Roughness; B → Metallic. ORM is Non-Color data.

## Rebuild

```bash
# 1) Pack atlases from source textures
python3 beamng-props/build_atlases.py

# 2) Export DAEs (copies atlas + ORM next to each DAE folder)
/tmp/blender-4.2.9-linux-x64/blender --background --python beamng-props/rebuild_with_collision.py
```

Source art remains in each kit’s `textures/` folder for editing; re-run `build_atlases.py` after changes.

## BeamNG note

Collada from Blender binds the **albedo atlas** into the DAE (`library_images`).  
`*_orm_2048.png` is copied beside each export for PBR setup in the shape/material editor:

- colorMap / diffuse → `sign_atlas_2048.png` or `vegetation_atlas_2048.png`
- ORM / packed map → matching `*_orm_2048.png` (R=AO, G=Roughness, B=Metallic)

The albedo atlas alone already cuts texture binds vs one PNG per mile marker.
