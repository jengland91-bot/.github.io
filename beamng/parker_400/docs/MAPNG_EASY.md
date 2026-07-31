# Easy path: MapNG → full Parker 400 looking good

Yes — there is an easy way. Use **our Parker 400 level for the full race**, and use **MapNG for prettier ground** (satellite / sharper hills). Do **not** throw away the GPX race line.

---

## The one thing to know first

MapNG builds terrain at about **1 meter per pixel**.

| MapNG size | Real ground covered |
|---|---|
| 2048 | ~2 km × 2 km |
| 4096 | ~4 km × 4 km |
| **8192** | **~8 km × 8 km** |

Your Parker CTUTV loop needs about **65 km × 65 km**.

So: **one MapNG export cannot hold the whole race.**  
That’s normal. Full-course maps use a wider, slightly coarser terrain (what we already built).

---

## Easiest path (recommended) — full course looks good

### Goal
Drive the **whole 126‑mile loop** with real hills + satellite color + your official race line.

### Steps

#### 1) Install our Parker 400 map (you may already have this)
1. Download `Parker_400_Install.zip`
2. Run `INSTALL_PARKER_400.bat`
3. BeamNG → Freeroam → **Parker 400**
4. F11 → Import Terrain → load `import/p400_gpx_scale.preset.json`
5. Confirm: **16** m/px, **1500** max height, pos **-32768, -32768**
6. Import → Ctrl+S

You now have the **full course** driveable.

#### 2) Get MapNG files the easy way (for looks)
1. Open **https://mapng.com/** on a PC browser
2. Search: `Parker Arizona` or paste `34.086139, -113.897239`
3. Set resolution to **8192** (biggest)
4. Elevation: **USGS** if available, else Standard
5. Turn **Satellite** export on
6. Generate / preview
7. Download these two files:
   - **Heightmap** (16-bit PNG)
   - **Satellite** (JPG/PNG)

This MapNG tile is only ~8 km — perfect for Main Pit / start area detail.  
For the **whole** loop color, either:

- **A)** Send me those files + say “full course satellite” and I’ll bake a matching full-map satellite for the 65 km square, or  
- **B)** Use MapNG **Batch Job** (Path 3 below) and send me the folder

#### 3) Copy files into BeamNG (simple copy-paste)

Press `Win + R`, paste this, Enter:

```
%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400
```

Then:

| Copy this MapNG file | Into this folder | Rename to |
|---|---|---|
| Heightmap PNG | `import\` | `mapng_heightmap.png` |
| Satellite JPG/PNG | `art\terrains\` | `parker400_base_color.png` |
| Same satellite (optional copy) | `import\` | `mapng_satellite.jpg` |

#### 4) Tell me you’re done
Upload / drop:
- `mapng_heightmap.png`
- `mapng_satellite.jpg` (or png)
- a screenshot of MapNG showing the selected area (optional)

I’ll wire the satellite into materials and keep the **official CTUTV DecalRoad** lined up on the full course.

---

## Path 2 — “I only care about Main Pit / start looking insane”

If you want ultra-detailed dirt near staging first:

1. MapNG center on Main Pit / Start Line (`34.131, -114.166`)
2. Resolution **8192**, USGS elevation, Satellite on
3. Export **BeamNG Level Package** if MapNG offers it  
   **or** export Heightmap + Satellite + `.ter`
4. Install that as a separate small test map in BeamNG
5. Keep our `parker_400` level for the full race

This is the easiest MapNG-only workflow — great for prerunning pits, not the whole lap.

---

## Path 3 — Full course using MapNG Batch (best MapNG quality)

Only if you want MapNG elevation across the **entire** loop.

1. On mapng.com switch to **Batch Job**
2. Build a grid that covers this box:

| Corner | Lat | Lon |
|---|---|---|
| SW | `33.791781` | `-114.252473` |
| SE | `33.791781` | `-113.544084` |
| NW | `34.380498` | `-114.252851` |
| NE | `34.380498` | `-113.539519` |

3. Use **8192** tiles (each ~8 km)
4. Roughly an **8 × 8** grid covers ~65 km (adjust until corners are inside)
5. Shared elevation baseline = ON (if shown)
6. Export heightmap + satellite for all tiles
7. Zip the whole batch folder and send it to me

I’ll stitch it into one BeamNG heightmap + satellite that matches our 1:1 GPX course.

---

## What NOT to do

- Don’t delete our DecalRoad / GPX race line and replace it with OSM roads  
- Don’t expect one 8192 MapNG tile to contain the whole Parker 400  
- Don’t change meters-per-pixel randomly — wrong scale = course won’t match GPS

---

## Cheat sheet (print this)

1. Install **Parker 400** ZIP (full course)  
2. MapNG → Parker AZ → **8192** → USGS → download **heightmap + satellite**  
3. Copy into `levels\parker_400\import\` and `art\terrains\`  
4. Send me the two files  
5. I finish wiring so the full course looks good

That’s the clear / easy way.
