# Parker 400 — Desert Bushes & Trees

Scatter flora for the desert course. Uses the shared **vegetation atlas**, dedicated **Colmesh** colliders, and LOD chains.

## Files (`export/dae/`)

### Bushes
| File | Approx size |
|------|-------------|
| `creosote_small/med/large.dae` | 0.9–1.9 m tall |
| `scrub_small/med.dae` | Low dry scrub |

### Cacti
| File | Notes |
|------|--------|
| `saguaro_small.dae` | ~2.2 m, no arms |
| `saguaro_tall.dae` | ~5.5 m column |
| `saguaro_armed.dae` | ~4.8 m, 2 arms |
| `saguaro_multi.dae` | ~6.2 m, 3 arms |

### Ocotillo & trees
| File | Notes |
|------|--------|
| `ocotillo_med/tall.dae` | Stem clusters |
| `mesquite_small/med/large.dae` | Trunk + canopy cards |

## Drop into BeamNG

```text
levels/YourParkerMap/art/shapes/props/flora/
```

Place as **TSStatic**. Origin is at **ground base** (terrain snap / foliage tools).

Set **collisionType** = `Collision Mesh` — colliders are simple cylinders/capsules (not leaf cards).

## Tech

- Textures: `vegetation_atlas_2048.png` + `vegetation_orm_2048.png` (see `../TEXTURES.md`)
- LODs: `_a800` / `_a200` / `_a50` billboard (see `../GEOMETRY_LODS.md`)
- Collision: trunk/bush capsules only (see `../COLLISION.md`)

## Rebuild

```bash
/tmp/blender-4.2.9-linux-x64/blender --background --python beamng-props/desert-flora/batch_export_flora.py
```
