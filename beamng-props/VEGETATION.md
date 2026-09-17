# Vegetation & Alpha Performance

Off-road maps draw a lot of foliage. **Transparent overdraw** (many overlapping alpha quads) hurts more than a few extra opaque tris.

## Rules used in `desert-flora/`

### 1. Cut meshes to the leaf silhouette
Leaf/canopy pieces are **irregular outlines** that hug the opaque leaf blobs — not full rectangles with empty transparent corners.

Atlas leaf tiles (`creosote_leaf`, `dry_bush`) have **real alpha cutouts** (opaque leaf clusters only).

### 2. Limit overlapping sprays
Creosote / canopy use **3–4** silhouette cards, not stacks of 6–8 large quads.

### 3. Single-sided in Blender — Two-Sided in BeamNG
Do **not** duplicate faces to fake double-sided leaves (that doubles polycount and overdraw).

In BeamNG material editor for `ParkerVegFoliage`:

1. Open the shape / material
2. Enable **Two-Sided** / **Double-Sided**
3. Use **alpha clip / punch-through** (not soft blend) when possible

Bark / saguaro / ocotillo stay opaque (`ParkerVegBark`) — no alpha needed.

## Rebuild

```bash
python3 beamng-props/build_atlases.py
/tmp/blender-4.2.9-linux-x64/blender --background --python beamng-props/desert-flora/batch_export_flora.py
```

Also see `TEXTURES.md`, `GEOMETRY_LODS.md`, `COLLISION.md`.
