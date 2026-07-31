# Parker 400 — Step-by-step build (BeamNG)

Follow this in order. Don’t skip ahead.

---

## What you need (download these)

### 1) Required — our Parker 400 install
Download the install ZIP from the project:

- **File:** `Parker_400_Install.zip`  
- **From:** `p400.html` on the site, or the GitHub PR / `beamng/parker_400/Parker_400_Install.zip`

Inside it you already get:
| File | What it is |
|---|---|
| `levels/parker_400/` | The BeamNG level |
| `import/heightmap_4096.png` | **Hills** (full course) |
| `import/p400_gpx_scale.preset.json` | Import settings |
| `art/terrains/parker400_base_color.png` | Satellite ground color (already included) |
| `INSTALL_PARKER_400.bat` | One-click install |

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

### Step 1 — Install the level
1. Unzip `Parker_400_Install.zip`
2. Double-click **`INSTALL_PARKER_400.bat`**
3. It copies the level to:
   ```
   %LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400
   ```

### Step 2 — Open in BeamNG
1. Launch **BeamNG.drive**
2. **Freeroam** → find **Parker 400** → load it  
   (First load may look flat until you import the heightmap)

### Step 3 — Import the heightmap (hills)
1. Press **F11** (World Editor)
2. Open **Terrain tools** → **Import Terrain** / Heightmap Import
3. **Load preset:**
   ```
   levels\parker_400\import\p400_gpx_scale.preset.json
   ```
4. Confirm these numbers:

| Setting | Value |
|---|---|
| Heightmap | `heightmap_4096.png` |
| Meters per Pixel | **16** |
| Max Height | **1500** |
| Position | **-32768, -32768, 0** |

5. Click **Import**
6. **Ctrl + S** to save the level

### Step 4 — Paint the ground (satellite look)
1. Still in World Editor (F11)
2. **Terrain Painter**
3. Select material **`desert_base`**
4. Paint over the whole map (big brush)
5. Optional: paint **`course_pack`** lightly along the race ribbon
6. **Ctrl + S**

### Step 5 — Drive
1. Exit World Editor / freeroam respawn  
2. Spawn at **Main Pit / Staging** (default) or **Start Line**  
3. Follow the DecalRoad race corridor = official 2026 CTUTV GPX line  

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
