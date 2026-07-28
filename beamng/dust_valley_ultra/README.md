# Dust Valley Ultra

Big **fast desert Ultra 4** map for BeamNG.drive.

- **Park size:** ~16.4 km across (`16384` m / ~10.2 miles)
- **Long course:** **2024 CA300 Race Ready** path (~**74 miles**, nearly 1:1 fit) — gold on minimap
- **Short course:** ~**5 miles** inner loop in the middle (cyan)
- **Dangers:** 68 CA300 markers (g-outs, rocks, washouts, poles…) — orange/red on minimap
- **Extras:** pit row, side rock trails
- **Default spawn:** pits / staging

This repo ships the design, a 16-bit heightmap, spawn metadata, and World Editor build steps. BeamNG still needs a binary `.ter` terrain created/imported in the World Editor (that step is in-game).

## Difficulty / feasibility

Making the **bigger dual-course layout** is very doable from the design side — already updated here.

What gets harder in BeamNG as the park grows:

| Piece | Difficulty | Notes |
| --- | --- | --- |
| Design + heightmap + minimap colors | Easy–moderate | Done in this package |
| World Editor heightmap import | Moderate | One-time; use `squareSize=4`, `maxHeight~280` |
| Performance on a 16 km terrain | Moderate | 4 m samples keep memory sane; expect more LOD/prop care |
| Exact measured 20.00 mi race | Harder later | Needs DecalRoads / checkpoints and a driven distance check |
| Fine rock detail everywhere | Harder | 4 m grid is coarser than the old 2 m / 4 km park |

So: **scaling to a literal ~20 mile course with a short course in the middle is realistic.** Perfect race-length certification and dense detailing are the longer follow-ups.

## Layout

| Zone | What it is | Minimap color |
| --- | --- | --- |
| Long course | Outer ~20 mi Ultra 4 desert loop | Gold |
| Short course | Inner ~5 mi practice / sprint loop | Cyan |
| Whoops field | West long-course whoops | Orange |
| Valley cut | North speed wash | Blue |
| Jump line | South tabletops | Red |
| East / NW rock trails | Technical trails off the sides | Purple / Teal |
| Pits | Staging pad | Green |

Color overview: [`source/layout_overview.png`](source/layout_overview.png)

Measured lengths: [`source/course_lengths.json`](source/course_lengths.json) · color key: [`source/trail_colors.json`](source/trail_colors.json)

## Quick install (after terrain is built)

1. Zip so the archive root contains `levels/dust_valley_ultra/`:

```bash
cd beamng/dust_valley_ultra
zip -r DustValleyUltra.zip levels
```

2. Copy `DustValleyUltra.zip` into your BeamNG mods folder, e.g.:
   - Windows: `Documents/BeamNG.drive/mods/`
3. Enable the mod and load **Dust Valley Ultra**.

## Build the terrain in BeamNG (required once)

1. In BeamNG, open **World Editor**.
2. Create a **Starter Level**, rename/move it to `levels/dust_valley_ultra` (or copy our `info.json` + `main/` into your new level folder).
3. Terrain Editor → **Heightmap Import**.
4. Import `source/heightmap_4096.png` with:
   - **Resolution:** 4096
   - **squareSize:** `4` (world = 16384 m)
   - **maxHeight:** about `280`
5. Save the level (this writes the `.ter`).
6. Paint materials:
   - long + short courses → packed desert sand / dirt
   - rock trails → rock / gravel
7. Nudge spawn spheres so their Z sits just above terrain.
8. Export a `preview.png` screenshot into the level folder.

Full author notes: [`docs/DESIGN.md`](docs/DESIGN.md)

Inspiration (ideas only, no asset rip): [`docs/REFERENCE_MAPS.md`](docs/REFERENCE_MAPS.md) — LACR MX, BDR High Desert, Echo Valley, CF Baja 1K.

## Regenerate the heightmap

```bash
python3 source/generate_heightmap.py
```

## Repo layout

```
beamng/dust_valley_ultra/
├── README.md
├── docs/DESIGN.md
├── source/                 # authoring (keep out of final mod zip if you want)
│   ├── generate_heightmap.py
│   ├── heightmap_4096.png
│   ├── layout_overview.png
│   └── ...
└── levels/dust_valley_ultra/
    ├── info.json
    └── main/items.level.json
```
