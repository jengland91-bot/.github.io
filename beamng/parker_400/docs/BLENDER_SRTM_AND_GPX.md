# Blender SRTM + GPX on minimap / World Editor

How to export BlenderGIS elevation into Parker 400, and how the race GPX
shows on the Freeroam minimap and in World Editor.

## A) Get Blender SRTM into the map files

### 1. In Blender — download hills
1. GIS → Web geodata → Basemap → Google Satellite → OK  
2. Center on map center: **34.086139, -113.897239**  
3. Zoom out to a big square (~65 km if you can)  
4. GIS → Web geodata → **Get elevation (SRTM)**  
5. Server: OpenTopography SRTM 30m + your free API key → OK  
6. Wait until object **`srtm`** appears (bumpy grey mesh)

### 2. Make the mesh dense (important)
1. Select **`srtm`**  
2. Modifiers (blue wrench):  
   - **DEM** Subdivision → Levels Viewport **8** (or 9–10 if PC allows)  
   - Render = same number  
3. Apply **DEM** (▼ → Apply)  
4. Apply **DEM.001** Displace (▼ → Apply)  
5. Modifiers list should be empty  
6. Tilt view — hills must still be 3D

### 3. Export
1. Select only **`srtm`**  
2. File → Export → **glTF 2.0 (.glb)**  
3. Enable **Selection Only**  
4. Save as `parker400_terrain.glb`

### 4. Put it in the Parker files
Copy the file to:

```text
beamng/parker_400/import/parker400_terrain.glb
```

(On Windows after you clone/extract the repo, that’s the `import` folder next to `levels` and `scripts`.)

### 5. Bake it into BeamNG terrain
From `beamng/parker_400`:

```bat
python scripts\bake_blender_glb.py
python scripts\bake_ter.py
python scripts\bake_water.py
python scripts\bake_forest_scatter.py
python scripts\bake_level.py
python scripts\bake_minimap.py
python scripts\pack_mod_zip.py
```

Or run `scripts\rebuild_all.sh` (it auto-runs the Blender bake if the `.glb` is present).

### 6. Install the new zip
Use `Parker400_Download_Both.zip` → `RUN_INSTALL.cmd` → Freeroam **Parker 400**.  
Clear terrain material cache if ground looks old.

**Notes**
- Blender mesh covers the center band; USGS fills uncovered edges  
- Denser subdivision (8–10) = better washes  
- Do **not** stretch Scale Z — keep real height  


## B) GPX / race line on the minimap

The official course GPX is already converted to:

- `source/reference/p400/p400_map_course.json` (UVs + miles)

`scripts/bake_minimap.py` draws that line as a **thick gold trail** onto:

- `levels/parker_400/minimap/terrain.png`

`info.json` points Freeroam at that minimap.  
Rebuild anytime with:

```bat
python scripts\bake_minimap.py
python scripts\pack_mod_zip.py
```

In-game: open the circular minimap / big map — you should see the gold loop.


## C) Race line in World Editor

BeamNG does **not** load the raw `.gpx` in World Editor.  
The playable/editable line is a **DecalRoad** built from the GPX:

- Scene Tree → **MissionGroup** → **LevelObjects** → **Roads**  
- **`p400_ctutv_course`** = full CT/UTV GPX line  
- **`p400_main_pit`** = pit stub  

### How to see / edit it
1. Launch level in World Editor (F11)  
2. Open Scene Tree  
3. Select **`p400_ctutv_course`**  
4. You should see the road spline / nodes through the desert  
5. `hiddenInNavi` is **false** so it can also show in nav where the engine allows  

If the ribbon is hard to see: select the DecalRoad and check the Roads group isn’t hidden; zoom near Main Pit first.

### After you move nodes
Save the level, or re-export nodes and re-run `bake_level.py` if you maintain roads from the bake scripts.


## Quick checklist

| Want | Do |
|---|---|
| Blender hills in game | Export applied `srtm` → `import/parker400_terrain.glb` → bake scripts above |
| Gold GPX on minimap | `bake_minimap.py` (already in shipped zip) |
| Line in World Editor | Select DecalRoad `p400_ctutv_course` under Roads |
| New install zip | `pack_mod_zip.py` → `Parker400_Download_Both.zip` |
