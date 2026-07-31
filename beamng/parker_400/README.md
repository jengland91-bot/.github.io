# Parker 400 — BeamNG package

Desert race map for BeamNG.drive built from the **2026 Parker 400 C/T/UTV Final Racer** GPS files (GPX / KML / USR).

**Level folder:** `parker_400`  
**Scale:** true **1:1** (1 map meter = 1 real meter)  
**Course:** ~125.8 mi / 202.4 km loop around Parker, AZ

**Full beginner guide:** [`docs/STEP_BY_STEP_BUILD.md`](docs/STEP_BY_STEP_BUILD.md)

## Install into BeamNG **0.39 / 0.39.1**

After the 0.39 update, Freeroam often **ignores** a loose `levels\parker_400` folder.  
Install as a **mod zip** instead.

### Recommended (Freeroam fix)

1. Download [`mods_drop_in/parker_400.zip`](mods_drop_in/parker_400.zip)
2. Launcher → **Manage User Folder** → **Open**
3. Put the zip in **`mods\`** (do **not** unzip)
4. Enable mod → full restart → Freeroam → search **parker**

Guide: [`INSTALL_FOR_039.md`](INSTALL_FOR_039.md) · troubleshooting: [`FIX_INSTALL.md`](FIX_INSTALL.md)

### Full package + bat

1. Download `Parker_400_Install.zip` (`p400.html`)
2. Extract → run `FIX_AND_INSTALL.bat` or `INSTALL_PARKER_400.bat`
3. Confirms install path: `...\current\mods\parker_400.zip`

### In BeamNG after install

1. Freeroam → **Parker 400**
2. World Editor (F11) → Terrain tools → Import Terrain
3. **Load preset** `import/p400_gpx_scale.preset.json`
4. Confirm **Meters per Pixel = 16**, **Max Height = 1500**, position **-32768, -32768**
5. Import → Ctrl+S

## Scale (locked to GPX 1:1)

| Setting | Value |
|---|---|
| World size | **65536 × 65536 m** |
| Heightmap | `import/heightmap_4096.png` |
| squareSize | **16** (HD rebuild: **8**) |
| maxHeight | **1500** |
| Terrain position | **-32768, -32768, 0** |
| Geo scale | **1.0×** real Parker footprint |

## What’s in the level

- SRTM elevation under the full CTUTV course area
- DecalRoad `p400_ctutv_course` from the official race line
- Main Pit pad + spawns at Main Pit / Start Line
- Course markers: pits, VCPs, dangers, speed zones, start/finish
- Desert terrain materials (reuseable pack)
- Google Earth paint notes: `docs/EARTH_PAINT_GUIDE.md`
- Source GPS: `source/reference/p400/`

## Rebuild from GPS

```bash
cd beamng/parker_400
python3 scripts/convert_p400_to_map.py
python3 scripts/bake_srtm_heightmap.py
python3 scripts/bake_level.py
```

## Bring next (optional)

**Clearest MapNG instructions:** [`docs/MAPNG_EASY.md`](docs/MAPNG_EASY.md)  
**Match GPX ↔ MapNG / Google Earth:** [`docs/MATCH_GPX_TO_MAPNG.md`](docs/MATCH_GPX_TO_MAPNG.md)  
**Alignment KML:** [`source/reference/p400/parker400_mapng_frame.kml`](source/reference/p400/parker400_mapng_frame.kml)

- MapNG for satellite / sharper local terrain ([mapng.com](https://mapng.com/))
- Google Earth photo can replace/blend satellite color; use MapNG/USGS for real hills
- USGS 10 m or 1 m DEM for whoops (or MapNG USGS + batch stitch)
- Qualifying / Youth / Motorcycle / Unlimited GPS variants
- Pit lane props, banners, start-gate mesh
