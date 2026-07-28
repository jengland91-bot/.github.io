# California 300 — ready-to-copy BeamNG package

I can’t create folders on your Windows PC from here, so this package is ready for you to copy.

## Fix GPX scale NOW (recommended)

Your map must be **16384 m × 16384 m** to match the 2024 CA300 Race Ready GPX (~74 mi course, ~15.3×15.6 km footprint at ~0.97×).

### 1) Download and run this on your PC

https://github.com/jengland91-bot/.github.io/raw/cursor/dust-valley-ultra-map-65dc/beamng/california_300/scripts/ONE_CLICK_FIX.bat

It installs into:

`%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\california_300`

and downloads:
- `heightmap_4096.png`
- Import preset `ca300_gpx_scale.preset.json` (**squareSize=4**, **maxHeight=900**, pos **-8192,-8192**)
- GPX-baked DecalRoad course + pit row
- `DO_THIS_NOW.txt` checklist

### 2) In BeamNG (one Import click)

1. Open **California 300**
2. F11 → Terrain → **Import Terrain**
3. **Load preset** → `import/ca300_gpx_scale.preset.json`
4. Confirm **Meters per Pixel = 4**, **Max Height = 900**
5. **Import** → **Ctrl+S**

Do **not** use meters/pixel = 1 (that makes a tiny ~4 km map).

## If the `levels` folder “disappears”

BeamNG cleanup moves custom folders into backup dirs next to `current`.

Permanent path (Win+R):

`%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels`

Helpers:
- `scripts/OPEN_LEVELS_FOLDER.bat`
- `scripts/FIX_SCALE.bat`
- `scripts/ONE_CLICK_FIX.bat` ← use this first

## Scale facts (locked to GPX)

| Setting | Value |
|---|---|
| Heightmap | `heightmap_4096.png` (4096×4096, 16-bit) |
| squareSize / m per pixel | **4** |
| maxHeight | **900** (SRTM relief ~795 m) |
| World size | **16384 × 16384 m** |
| Terrain position | **-8192, -8192, 0** |
| Geo scale vs real CA300 | **~0.9666×** |

## Package layout

```
california_300/
  DO_THIS_NOW.txt
  import/
    heightmap_4096.png
    ca300_gpx_scale.preset.json
  levels/california_300/
    info.json
    preview.png
    import/          (same heightmap + preset for in-game paths)
    main/items.level.json   (TerrainBlock + ca300_race_ready DecalRoad)
    minimap/
  scripts/
    ONE_CLICK_FIX.bat
    FIX_SCALE.bat
    OPEN_LEVELS_FOLDER.bat
    bake_gpx_scaled_level.py
```
