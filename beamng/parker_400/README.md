# Parker 400 — BeamNG package

Desert race map for BeamNG.drive built from the **2026 Parker 400 C/T/UTV Final Racer** GPS files (GPX / KML / USR).

**Level folder:** `parker_400`  
**Scale:** true **1:1** (1 map meter = 1 real meter)  
**Course:** ~125.8 mi / 202.4 km loop around Parker, AZ

## Install into BeamNG

### Easiest (ZIP)

1. Download `Parker_400_Install.zip` from the site download page (`p400.html`)
2. Extract the ZIP
3. Double-click `INSTALL_PARKER_400.bat`
4. Follow `DO_THIS_NOW.txt`

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

## Next upgrades (bring these when ready)

- Google Earth / Esri satellite base colormap for the footprint
- Higher-res DEM (USGS 1 m / 10 m NED) for whoops and wash detail
- Qualifying / Youth / Motorcycle / Unlimited course variants from their GPS files
- Pit lane props, banners, and start-gate mesh
