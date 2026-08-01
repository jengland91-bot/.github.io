# Closer ground detail — multiple pics / Google Earth

One satellite image over a **65 km** map can’t match phone zoom. Phone zoom is roughly **0.1–0.5 m/px**; our shipped unique sat is about **5 m/px**. Matching the phone for the whole loop would be hundreds of gigabytes.

## Yes — multiple pics help

BeamNG still uses **one** full-map ground photo (unique sat). Extra pics help when you **stitch them into that photo** (or into a sharper rebuild). Separate random JPGs painted as different materials won’t line up with GPS unless they’re georeferenced.

| Method | Best for | Effort |
|---|---|---|
| **MapNG batch tiles** | Sharp patches along the course | Medium — best quality |
| **Google Earth Pro Save Image** (several tiles) | Main Pit, VCPs, favorite washes | Easy |
| **USGS NAIP / QGIS** | Official US aerial ~1 m | Medium |
| **Detail/macro textures** (already in materials) | Close-up grit everywhere | Automatic — not real satellite |

---

## Option 1 — Google Earth Pro (easiest for you)

Use **desktop Google Earth Pro** (not phone).

1. File → Open →  
   `source/reference/p400/2026_Parker_400_CTUTV_Final_Racer_File.kml`
2. Tilt **straight down**, turn off labels/roads/atmosphere.
3. Fly to a spot you care about (Main Pit, a wash, a VCP).
4. Zoom so the view covers roughly **2–8 km** across (not the whole race).
5. File → Save → **Save Image** at max resolution.
6. Note the **center lat/lon** (look at the status bar / placemark) and roughly how many **km wide** the view is.

### Drop files here

```
beamng/parker_400/import/sat_tiles/
```

Example:

```
import/sat_tiles/
  main_pit.jpg
  wash_east.jpg
  tiles.json
```

`tiles.json`:

```json
{
  "tiles": [
    {
      "file": "main_pit.jpg",
      "lat": 34.1500,
      "lon": -114.2900,
      "widthMeters": 4000,
      "heightMeters": 4000
    },
    {
      "file": "wash_east.jpg",
      "lat": 34.0861,
      "lon": -113.8972,
      "widthMeters": 6000,
      "heightMeters": 6000
    }
  ]
}
```

Then (or send me the folder / zip):

```bash
python3 scripts/stitch_sat_tiles.py
python3 scripts/pack_mod_zip.py
```

That **burns your sharper patches into** `parker400_base_color.jpg` while keeping the rest of the desert from the full-loop Esri bake.

Tips for GE tiles:

- North **up**, no tilt  
- Overlap neighboring tiles a bit  
- Same sun/season if you can (GE imagery varies)  
- Prefer a few **important** spots over trying to tile the whole 126 miles by hand  

Windows shortcut: `scripts\OPEN_SAT_TILE_FOLDERS.bat`

---

## Option 2 — MapNG batch (best quality)

1. [mapng.com](https://mapng.com/) → Batch / tile grid over the Parker box  
2. Export **Satellite** tiles (8192 / high zoom)  
3. Zip them + any bounds info → send to me **or** drop into `import/sat_tiles/` with a `tiles.json` listing each tile’s center + size  
4. I stitch into the unique sat (same as above)

One MapNG tile ≈ **8 km**. A grid of those along the course is exactly how you beat “one download” softness.

---

## Option 3 — What we can’t do in one GitHub zip

| Target | Rough unique-sat size | Ship on GitHub? |
|---|---|---|
| ~5 m/px (current) | ~30 MB JPG | Yes |
| ~1 m/px full loop | ~ several GB | No |
| Phone-like ~0.25 m/px | enormous | No |

So: **full loop stays medium-res**; **hotspots** get your GE/MapNG patches.

---

## Already improved without extra pics

Terrain materials use tiling **detail/normal** maps up close so dirt isn’t only soft sat pixels. That’s not Google Earth detail — it’s close-range texture so driving doesn’t look like a blurred photo.
