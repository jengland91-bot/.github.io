# Parker 400 — Step-by-step build (BeamNG)

Follow this in order. Don’t skip ahead.

---

## What you need (download these)

### 1) Required — our Parker 400 install (**BeamNG 0.39 / 0.39.1**)

**Best for Freeroam (recommended):** download the mod zip only:

- **File:** [`mods_drop_in/parker_400.zip`](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip)
- Put it in: `%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods\` (**do not unzip**)
- Full guide: [`INSTALL_FOR_039.md`](../INSTALL_FOR_039.md)

Or use the full package + bat:

- **File:** `Parker_400_Install.zip`  
- **From:** `p400.html` on the site, or GitHub `beamng/parker_400/Parker_400_Install.zip`

Inside the full package:
| File | What it is |
|---|---|
| `mods_drop_in/parker_400.zip` | **0.39 Freeroam mod** (preferred) |
| `levels/parker_400/` | Level files (used to rebuild the mod) |
| `import/heightmap_4096.png` | **Hills** (full course) |
| `import/p400_gpx_scale.preset.json` | Import settings |
| `art/terrains/parker400_base_color.png` | Satellite ground color |
| `INSTALL_PARKER_400.bat` / `FIX_AND_INSTALL.bat` | Install into `mods\` |

### 2) Optional — MapNG satellite (only if you want to replace the ground photo)
From [mapng.com](https://mapng.com/) after Generate:
- **Satellite** `.jpg` / `.png` → yes  
- **Heightmap** → **no** (yours was broken; use ours)

MapNG settings if you redo sat:
- 8192, m/px **8**, center near `34.086139, -113.897239`, USGS, Sat layer  
- Download **Satellite** only

### 3) Do NOT need for first playable map
- Google Earth Pro  
- Nearmap  
- onX exports  
- MapNG BeamNG Level Export zip  
- MapNG Hybrid / OSM textures  

---

## Step-by-step — build & run

### Step 1 — Install as a mod (required on 0.39.1)
**Fast path (no bat):**
1. Download [`parker_400.zip`](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip)
2. BeamNG launcher → **Manage User Folder** → **Open**
3. Copy the zip into the **`mods`** folder (leave it zipped)
4. Delete any old `levels\parker_400` folder if you made one earlier
5. Fully quit BeamNG and start again; enable the mod if asked

**Or with the install package:**
1. Download `Parker_400_Install.zip` → Extract All
2. Double-click **`FIX_AND_INSTALL.bat`** (or `INSTALL_PARKER_400.bat`)
3. It installs to:
   ```
   %LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods\parker_400.zip
   ```
   Loose `levels\parker_400` copies are **ignored** by Freeroam after the 0.39 update — that is why the map was missing.

### Step 2 — Open in BeamNG
1. Launch **BeamNG.drive**
2. **Freeroam** → search **parker** → **Parker 400**  
3. You should see **desert hills + satellite ground** (pre-baked `theTerrain.ter`)

If it is **black**, re-download the latest `parker_400.zip` (old packages were missing the `.ter` file).

### Step 3 — Drive
1. Spawn at **Main Pit / Staging** (default) or **Start Line**  
2. Follow the DecalRoad race corridor = official 2026 CTUTV GPX line  

### Optional — re-import / re-paint (only if needed)
1. **F11** → Terrain tools → Import → `import/p400_gpx_scale.preset.json`  
   (16 m/px, maxHeight 1500, pos -32768,-32768)  
2. Terrain Painter → **`desert_base`** → Ctrl+S

---

## Optional — replace satellite with your MapNG photo

1. Take your MapNG **Satellite** file from Downloads  
2. Rename/copy to:
   ```
   %LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400\art\terrains\parker400_base_color.png
   ```
3. Overwrite when asked  
4. In BeamNG, paint **`desert_base`** again  
5. Ctrl+S  

---

## Quick “did it work?” checklist

- [ ] Level shows up as **Parker 400**  
- [ ] After import, ground has real hills (not flat)  
- [ ] Desert color shows after painting `desert_base`  
- [ ] Gold/race DecalRoad follows the Parker loop  
- [ ] Start/Main Pit spawn works  

---

## If something’s wrong

| Problem | Fix |
|---|---|
| No hills | Re-import preset; check squareSize **16**, maxHeight **1500** |
| Flat color / wrong texture | Paint `desert_base`; confirm `parker400_base_color.png` exists in `art\terrains\` |
| Can’t find levels folder | Run `OPEN_LEVELS_FOLDER.bat` from the ZIP |
| MapNG heightmap only a corner | Ignore it — use our `heightmap_4096.png` |

---

## Bottom line

**Download:** `Parker_400_Install.zip` only to start.  
**Build:** Install bat → F11 → import preset → paint `desert_base` → save → drive.  
**Optional later:** swap in MapNG Satellite for a different ground photo.
