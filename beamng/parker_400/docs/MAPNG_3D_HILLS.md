# MapNG “3D” hills & real washes (Parker 400)

## What MapNG’s 3D preview actually is

MapNG’s 3D view is **elevation data** (a heightmap), not a separate playable mesh you drop into BeamNG.  
For the US desert around Parker, that elevation comes from **USGS 3DEP** (10 m / 1 m where LiDAR exists) — the same family this map now bakes from.

One MapNG generate maxes around **8192 px ≈ 8×8 km**. The full Parker loop world is **65×65 km**, so MapNG cannot export the whole course as a single 1 m 3D tile.

## What we ship now

| Asset | Source | Grid | Notes |
|---|---|---|---|
| `theTerrain.ter` (in zip) | **USGS 3DEP** | 4096 @ **16 m/px** | Install & drive — real hills/washes for the full loop |
| `import/heightmap_8192.png` (rebuild locally) | USGS 3DEP | 8192 @ **8 m/px** | Sharper washes; `.ter` ~200 MB — too big for GitHub zip |

Rebuild DEM anytime:

```bash
python3 scripts/bake_usgs_heightmap.py
python3 scripts/bake_ter.py
python3 scripts/pack_mod_zip.py
```

## Optional — MapNG USGS 1 m for Main Pit only

Use MapNG when you want **insanely sharp** local terrain (~8 km box):

1. Open [mapng.com](https://mapng.com/)
2. Search: `34.150, -114.290` (Main Pit / start area)
3. Elevation: **USGS 1 m** (where available)
4. Size: **8192**, ~1 m/px
5. Export heightmap (+ sat if you want)
6. Drop into:
   - `%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400\import\mapng_heightmap.png`
7. Or run `scripts\OPEN_MAPNG_DROP_FOLDERS.bat`

That HD pit tile will **not** replace the full 126‑mile loop by itself — it’s a local upgrade.

## Optional — sharper full-loop (8 m/px) on your PC

If you rebuild this repo locally (or we give you `heightmap_8192.png` outside GitHub):

1. Copy `heightmap_8192.png` → `levels/parker_400/import/`
2. BeamNG World Editor → Import Terrain  
3. Preset: `import/p400_usgs_hd_8192.preset.json`  
   - **squareSize = 8** · **maxHeight = 1500** · pos **-32768, -32768**
4. Ctrl+S (rewrites `theTerrain.ter` locally — large file)

## Bottom line

- **Want real hills/washes on the whole course:** already in the latest zip (USGS 3DEP).  
- **Want MapNG 1 m “3D” detail:** do a small tile at Main Pit / a wash you care about.  
- **Want sharper full loop:** local 8192 import (not shippable in the GitHub 100 MB zip).
