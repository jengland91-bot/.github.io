# Physics Collision Meshes (BeamNG / Torque)

**Never use the detailed visual mesh for game physics.** Complex visuals cause hitching and vehicle clipping. Every prop DAE rebuilt by `rebuild_with_collision.py` ships a separate ultra-simple collider.

## Hierarchy (required)

```
base00
  start01              <- visual meshes (LOD names like *_a800)
  collision-1
    Colmesh_<name>-1   <- dedicated collision only (-1 = non-rendered)
```

## Rules used in this pack

| Prop type | Collider |
|-----------|----------|
| K-rails / hay walls | One bevel-free box (low face count — bumpers slide, no snagging) |
| Tire stacks / rocks | 8-sided cylinder / capsule around the volume |
| Fence posts & signs | Thin cylinder post + thin sign box |
| Chain-link / netting / ribbon | One thin wall box per panel |
| Porta-potties / light body | Single bounding box (+ thin mast box) |
| Arch gate (drive-through) | **Split** convex boxes: left leg + right leg + header (never one concave hull) |
| EZ-Up tent | Four pole boxes + roof slab (opening under canopy stays clear) |

## World Editor

When placing as **TSStatic**:

1. Set **collisionType** = `Collision Mesh` (not Visible Mesh / Bounds).
2. Do not enable collision on the visual LOD mesh alone.

## Rebuild

```bash
/tmp/blender-4.2.9-linux-x64/blender --background --python beamng-props/rebuild_with_collision.py
```

Shared helpers live in `beamng-props/_shared/beamng_export.py` (`box_collider`, `cylinder_collider`, `wrap_beamng_hierarchy`).
