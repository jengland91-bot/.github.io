# How to paint real satellite ground on Parker 400 (BeamNG)

The map already has **real hills** (SRTM). This guide adds **real-looking desert color** on top.

You do **not** need coding for the Google Earth part. Just export an image, drop it in a folder, then paint in BeamNG World Editor.

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

## Option A — Google Earth Pro (easiest for you)

### 1) Install / open Google Earth Pro (desktop)

Phone/web Google Earth is harder for exact exports. Use **Google Earth Pro** on PC.

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

## Option B — Esri / NAIP (cleaner for mods, a bit more work)

If Google Earth licensing worries you for a public mod:

1. Go to [USGS National Map Downloader](https://apps.nationalmap.gov/downloader/) or an Esri imagery export tool
2. Draw a box using the same four corners
3. Download imagery GeoTIFF / JPEG
4. Same as above: square crop, north up, drop into `art/terrains/`

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
