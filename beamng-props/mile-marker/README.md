# Parker 400 — Mile Markers 1–100

Ready-to-place BeamNG mile markers. **No Blender work required** — exports are already built.

## Quick drop-in (tomorrow on your PC)

1. Copy this folder into your map:

```text
beamng-props/mile-marker/export/dae/
```

→ into something like:

```text
levels/YourParkerMap/art/shapes/props/milemarkers/
```

2. Open your map in World Editor (`F11`)
3. Place a **TSStatic** for each mile you need, e.g.:
   - `milemarker_001.dae`
   - `milemarker_002.dae`
   - …
   - `milemarker_100.dae`

Each `.dae` already has its matching sign texture beside it (`mile_001.png`, wood, metal).

**Collision:** Dedicated 8-sided post cylinder + thin sign box (`Colmesh_*-1`). In World Editor set **collisionType** = `Collision Mesh` (not Visible Mesh). See `../COLLISION.md`.

## What’s in this kit

| Path | Contents |
|------|----------|
| `export/dae/milemarker_001.dae` … `milemarker_100.dae` | 100 finished markers |
| `export/dae/*.png` | Sign + wood + metal textures used by the DAEs |
| `export/milemarkers_1_to_100.blend` | Blender source (official Blender 4.x) |
| `textures/` | Full texture set (also used by scripts) |
| `batch_export_markers.py` | Rebuild/export script if you change the design |
| `build_mile_marker.py` | Single-marker interactive Blender script |
| `generate_textures.py` | Regenerates Mile 1–100 sign art |

## Specs

- Units: **meters**, Z-up
- Post ≈ **1.45 m** tall
- Origin at the **ground** under the post
- Sign faces **-Y** (rotate in World Editor as needed)
- Look: wood post, metal band, framed cream sign, desert orange stripe, “MILE N”

## Rebuild (optional)

```bash
python3 generate_textures.py
blender --background --python batch_export_markers.py
```

(Needs a Blender build with Collada export — official Blender from blender.org, not all Linux distro packages.)
