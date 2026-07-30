# How to paint real satellite ground on Parker 400 (BeamNG)

The map already has **real hills** (SRTM). This guide adds **real-looking desert color** on top.

You do **not** need Google Earth Pro. QGIS, USGS, or even a browser screenshot works. Export an image, drop it in a folder, then paint in BeamNG.

---

## What you are making

One big top-down photo of the Parker desert that matches our map square.

Our BeamNG world is a **65.536 km × 65.536 km** square centered on the race.  
Your satellite image should cover **that same square**.

### Exact map corners (copy these)

| Corner | Latitude | Longitude |
|---|---|---|
| Southwest | `33.791781` | `-114.252473` |
| Southeast | `33.791781` | `-113.544084` |
| Northwest | `34.380498` | `-114.252851` |
| Northeast | `34.380498` | `-113.539519` |
| Center | `34.086139` | `-113.897239` |

---

## Don’t have Google Earth Pro?

**Best pick for BeamNG:** [MapNG](https://mapng.com/) — made for this. Exports heightmap + satellite texture ready for World Editor.

Other free options:

| Program | Best for | Difficulty |
|---|---|---|
| **[MapNG](https://mapng.com/)** | Heightmap + satellite for BeamNG in one tool | Easy |
| **QGIS** | Exact corners + Esri export | Medium |
| **USGS National Map Downloader** | Official US aerial (NAIP) downloads | Easy |
| **Bing Maps / Google Maps in browser** | Quick screenshot (lower quality) | Easy |
| **SAS.Planet** | Popular with sim racers / map makers | Medium |

---

## Option MapNG (recommended) — https://mapng.com/

Use a **desktop browser** (MapNG needs mouse/keyboard).

### Why this works well for Parker 400

MapNG can give you:

1. **16-bit heightmap** (real elevation — USGS 1 m in the US if available, or global DEM)
2. **Satellite texture** (Esri imagery) — this replaces the Google Earth paint step
3. Optional BeamNG `.ter` / experimental level ZIP

Keep our package for the **official race line** (your CTUTV GPX → DecalRoad). MapNG won’t know the Parker race course; OSM roads are not the same as the race.

### Settings that match our map

Our level is a **65,536 m** square around Parker.

| Goal | MapNG setting |
|---|---|
| Cover the full CTUTV loop | Area must include corners below (~65 km square) |
| Match shipped map | **4096** resolution → about **16 m per pixel** |
| Sharper HD later | **8192** resolution → about **8 m per pixel** |
| Elevation | Prefer **USGS** if offered for Arizona; else global DEM |
| Textures | Export **Satellite** (and Hybrid if you want) |

### Exact area to select in MapNG

Center near: `34.086139, -113.897239` (Parker / Shea Rd area)

Cover all four corners:

| Corner | Lat | Lon |
|---|---|---|
| SW | `33.791781` | `-114.252473` |
| SE | `33.791781` | `-113.544084` |
| NW | `34.380498` | `-114.252851` |
| NE | `34.380498` | `-113.539519` |

If MapNG’s single tile can’t stretch that far at 1 m/px: that’s normal. For a ~65 km map you want **coarser m/px** (8–16), not 1 m/px. Use **Batch / tile grid** in MapNG if you want multiple high-res tiles later.

### What to export

Download at least:

- `heightmap` 16-bit PNG
- `satellite` texture PNG

Optional: `.ter` or level ZIP if MapNG offers it.

### How to use the exports with our Parker 400 level

1. Install our Parker 400 ZIP as usual (`INSTALL_PARKER_400.bat`).
2. Copy MapNG files into:
   ```
   %LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400\import\
   ```
   e.g. `mapng_heightmap.png`, `mapng_satellite.png`
3. Also copy the satellite PNG into:
   ```
   ...\levels\parker_400\art\terrains\parker400_base_color.png
   ```
4. In BeamNG → F11 → Import Terrain:
   - Use MapNG’s heightmap
   - **Meters per Pixel** = world size ÷ resolution  
     (for full 65536 m @ 4096 → **16**; @ 8192 → **8**)
   - **Max Height** = whatever MapNG reports for relief (or start with **1500** and adjust)
   - Position **-32768, -32768, 0** if you kept our world size
5. Ctrl+S
6. Send me the MapNG heightmap + satellite (or a screenshot of your MapNG export settings) and I can wire textures + re-align the DecalRoad if the origin shifted.

### Important

- If MapNG’s export box isn’t **exactly** our corners, the race line may sit slightly off the washes. Fixable — just tell me the MapNG bounds you used.
- Don’t replace the DecalRoad with OSM roads; keep the GPX race corridor.

---

## Option A — Google Earth Pro (if you have it)

### 1) Install / open Google Earth Pro (desktop)

Phone/web Google Earth is harder for exact exports. Use **Google Earth Pro** on PC if you already have it.

### 2) Load the race course

1. File → **Open**
2. Pick:
   `beamng/parker_400/source/reference/p400/2026_Parker_400_CTUTV_Final_Racer_File.kml`
3. The purple race line should appear around Parker, AZ.

### 3) Clean the view

Turn OFF clutter so the ground is clean:

- Layers: uncheck Roads, Borders, Labels, Places, 3D Buildings, etc.
- Leave **Imagery** on
- View → turn off grid / atmosphere if it looks weird
- Tilt to **straight down** (look straight at the ground, not angled)

### 4) Frame the exact map square

1. Search or fly to center: `34.086139, -113.897239`
2. Zoom out until you can see roughly the whole loop with desert around it
3. Use the corner coords above as a checklist — your view should include all four corners
4. Tip: drop temporary placemarks at the four corners so you know the box

### 5) Save a high-res image

1. File → **Save** → **Save Image**
2. Resolution: as high as Pro allows (ideally **4K / maximum**)
3. Map Options: turn off title, legend, scale, compass if possible
4. Save as something like:
   `parker400_satellite_base.jpg`

Good enough sizes:

- Minimum useful: **2048 × 2048**
- Better: **4096 × 4096**
- Ideal later: square crop matching the map (same aspect, north up)

### 6) Crop / square it (important)

BeamNG base color maps work best as a **square**, north-up image of the **same ground** as the heightmap.

In any image editor (Paint.NET, Photoshop, GIMP, Photopea.com):

1. Crop to a square covering those four corners
2. North should be **up**
3. Export PNG or JPG as:
   `parker400_base_color.png`

If the crop is slightly off, the course will still drive fine — paint will just look shifted. We can fix alignment later.

### 7) Put the file in the BeamNG level

Copy your image into:

```
%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400\art\terrains\
```

Name it something clear, e.g.:

```
parker400_base_color.png
```

Also drop a copy in the repo (optional, for us to wire permanently):

```
beamng/parker_400/levels/parker_400/art/terrains/parker400_base_color.png
```

---

## Option A2 — QGIS (best free replacement for Earth Pro)

1. Install [QGIS](https://qgis.org) (Windows installer is fine).
2. Open QGIS → Browser panel → **XYZ Tiles** → right‑click → New Connection.
3. Name: `Esri World Imagery`  
   URL:
   ```
   https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
   ```
4. Double‑click that layer so satellite appears.
5. Project → Import/Export → **Export Map to Image**
6. Extent → calculate from the four corner coords (or draw a box around Parker covering them).
7. Resolution: aim for **2048** or **4096** px square, north up.
8. Save as `parker400_base_color.png` and continue at **§ Put the file in the BeamNG level** above.

Optional: Layer → Add Layer → Add Vector Layer → open the Parker KML so the race line shows while you frame the export.

---

## Option A3 — USGS National Map (no special map app)

1. Open [USGS National Map Downloader](https://apps.nationalmap.gov/downloader/).
2. Zoom to Parker, AZ / draw a box using the corner coords.
3. Dataset: **Imagery - NAIP** (aerial photos).
4. Find → download the overlapping tiles.
5. Open the downloaded images in any viewer, stitch/crop to a square north‑up image, save as `parker400_base_color.png`.

Good for official US aerial; files can be large.

---

## Option A4 — Browser only (quick & dirty)

1. Open [Bing Maps](https://www.bing.com/maps) or Google Maps.
2. Switch to **Aerial / Satellite**.
3. Go to `34.086139, -113.897239`, zoom out to cover the loop.
4. Fullscreen screenshot (Windows: `Win+Shift+S` or Snipping Tool).
5. Crop square in Photopea / Paint.
6. Quality won’t match QGIS/USGS, but it’s enough to test paint in BeamNG.

---

## Option B — Esri / NAIP notes (licensing)

If you plan to **publish** the mod publicly, prefer **USGS NAIP** or other open imagery over Google Earth screenshots. For private/personal use, any of the options above are fine.

Target size for BeamNG base colormap: **2048² or 4096²**.

---

## In BeamNG — paint it on the terrain

After the image is in `art/terrains/`:

### 1) Open the level

Freeroam → **Parker 400** → press **F11** (World Editor)

### 2) Wire the texture (first time)

1. Terrain tools → **Terrain Painter**
2. Open **Terrain Material Library**
3. Use existing materials:
   - `desert_base` — open desert
   - `course_pack` — race ribbon
   - `rock_slope` — hillsides
4. For true satellite look, we replace/augment `desert_base`’s **base** albedo with your `parker400_base_color.png`

If you only want to try paint now without editing JSON:

- Paint `desert_base` everywhere
- Paint `course_pack` along the gold race line
- Paint `rock_slope` on steep hills

That already looks better than flat color.

### 3) Paint layers

Suggested order:

1. Fill whole map with `desert_base`
2. Soft brush `course_pack` along the DecalRoad / race corridor
3. `rock_slope` on mesas / steep SRTM slopes
4. Ctrl+S to save

### 4) Import reminder (if terrain looks flat)

If hills are missing, re-import heightmap preset:

- File: `levels/parker_400/import/p400_gpx_scale.preset.json`
- **Meters per Pixel = 16**
- **Max Height = 1500**
- Position **-32768, -32768, 0**

---

## What to send me when you’re done exporting

Drop these in chat / uploads and I can wire them into the materials for you:

1. `parker400_base_color.png` (or `.jpg`) — square satellite crop  
2. Optional: note of the four corners you actually used if different from the table  
3. Optional: higher-res DEM GeoTIFF later for sharper whoops

---

## Common mistakes

| Problem | Fix |
|---|---|
| Image is tilted / perspective | Export straight-down only |
| Course doesn’t line up with photo | Re-crop using the four corner coords |
| Looks blurry up close | Normal — satellite is a distant base; detail textures handle near ground |
| File huge / BeamNG slow | Resize to 2048 or 4096 square |
| Can’t find levels folder | Run `OPEN_LEVELS_FOLDER.bat` in the install ZIP |

---

## You do not need yet

- Blender
- Coding
- Rebuilding the heightmap

Just: **Google Earth export → square crop → drop in `art/terrains/` → tell me and I’ll finish the material hookup.**
