# Geometry, Transforms & LODs (BeamNG)

Desert maps have long sightlines — hundreds of props can be on screen at once. Every DAE from `rebuild_with_collision.py` follows these rules.

## Apply All Transforms

Before export, every mesh gets **location + rotation + scale** baked (`Ctrl+A` → All Transforms). Unapplied scale/rotation causes physics and placement bugs in-engine.

## Pivot at the base

Object origin is the **bottom-center** of the prop (flush with ground). Terrain snap and foliage tools place vegetation, posts, and buildings correctly.

## LOD chain (Torque naming)

Under `start01`, meshes are named with a **letter + pixel size** (underscore alone is treated as negative → invisible):

| LOD | Name suffix | Role |
|-----|-------------|------|
| LOD0 | `_a800` | Close-up, full detail |
| LOD1 | `_a200` | Medium distance, ~50% tris (Decimate) |
| LOD2 | `_a50` | Far, crossed-card billboard (~8 tris) |
| Cull | `nulldetail20` | Stop drawing when smaller than ~20 px |

Hierarchy:

```
base00
  start01
    propname_a800
    propname_a200
    propname_a50
    nulldetail20
  collision-1
    Colmesh_*-1
```

## Rebuild

```bash
/tmp/blender-4.2.9-linux-x64/blender --background --python beamng-props/rebuild_with_collision.py
```

Helpers: `beamng-props/_shared/beamng_export.py`  
Also see `COLLISION.md` for physics meshes.

## Typical prop sizes (meters)

| Prop | Approx. size | Collision |
|------|--------------|-----------|
| Mile marker plate | ~0.38 × 0.62 (portrait) | Thin box + post cylinder |
| Course / turn / TURN AHEAD | ~0.40 × 0.68 (portrait) | Thin box + post cylinder |

