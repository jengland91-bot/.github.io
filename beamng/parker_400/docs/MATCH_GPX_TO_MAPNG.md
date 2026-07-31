# Match your GPX to MapNG (and Google Earth)

## Short answers

1. **Yes — match MapNG to the GPX** using the frame KML below (orange box = our BeamNG world).
2. **Google Earth topo:** use GE for **looks** (satellite color). Keep **MapNG/USGS/SRTM** for **hills**. Mixing GE elevation into BeamNG is messy; mixing GE photos on top of our heightmap is fine.

---

## 1) Make sure MapNG is on the right spot

### File to open
```
beamng/parker_400/source/reference/p400/parker400_mapng_frame.kml
```

This file has:
- **Orange box** = exact BeamNG / GPX map square (65.536 km)
- **Gold line** = official 2026 CTUTV race from your GPX
- **Corner pins** with lat/lon

### In MapNG
1. Open https://mapng.com/ (desktop browser)
2. If MapNG can import KML/GeoJSON, load `parker400_mapng_frame.kml`  
   If not: search `34.086139, -113.897239` and zoom until you see Parker + the desert east of the Colorado River
3. Your MapNG selection should **cover the whole orange box**
4. Check that the race line area (big desert loop east of Parker) sits inside your selection

### Corner checklist (same as GPX frame)

| Corner | Lat | Lon |
|---|---|---|
| SW | `33.791781` | `-114.252473` |
| SE | `33.791781` | `-113.544084` |
| NW | `34.380498` | `-114.252851` |
| NE | `34.380498` | `-113.539519` |
| Center | `34.086139` | `-113.897239` |

### In Google Earth (web or Pro)
1. File → Open → `parker400_mapng_frame.kml`  
   **or** open the full racer KML: `2026_Parker_400_CTUTV_Final_Racer_File.kml`
2. You should see the same loop we baked (gold line in our preview)
3. If MapNG’s box matches this view, you’re pulling the right area

### Already matched for you
Our package already used the GPX to lock:
- heightmap
- Esri satellite (`parker400_base_color.png`)
- DecalRoad race line

So if you just install our ZIP, alignment is already done.

---

## 2) Can you mix Google Earth topography?

| What from Google Earth | Mix into BeamNG? | Notes |
|---|---|---|
| **Satellite / aerial photo** | **Yes** | Great as a color layer (or blended with our Esri base) |
| **3D “topo” / terrain mesh** | **Not easily** | GE doesn’t export a clean BeamNG heightmap |
| **Elevation numbers** | Prefer **MapNG USGS / SRTM / USGS NED** | Those become 16-bit PNG heightmaps BeamNG understands |

### Best mix (recommended)
- **Hills (topo):** keep ours (SRTM) or MapNG **USGS** heightmap  
- **Looks (skin):** Google Earth screenshot **or** our Esri satellite **or** MapNG satellite  
- **Race line:** always the **GPX DecalRoad** (not OSM, not GE roads)

### How to drop a Google Earth photo on top
1. In Google Earth, open `parker400_mapng_frame.kml`
2. Frame the **orange box**, look straight down
3. Save image / screenshot, crop to that box (square, north up)
4. Save as `parker400_base_color.png`
5. Replace:
   ```
   levels\parker_400\art\terrains\parker400_base_color.png
   ```
6. In BeamNG paint `desert_base` again

You can also send me the GE image and I’ll blend it with the Esri base (GE for close detail, Esri for the wide desert, etc.).

### What not to do
- Don’t use Google Earth’s 3D exaggeration as your BeamNG height — scale will be wrong  
- Don’t pick a MapNG tile that only covers Main Pit and expect the whole 126‑mile loop inside it  

---

## Quick decision guide

| You want… | Do this |
|---|---|
| Right area, no fuss | Install our ZIP (already GPX-matched) |
| Confirm MapNG area | Open `parker400_mapng_frame.kml` + cover the orange box |
| Better hills | MapNG USGS heightmap (or send batch tiles) |
| Different satellite look | Google Earth photo cropped to the orange box |
| Both | Height from MapNG/USGS + color from Google Earth |
