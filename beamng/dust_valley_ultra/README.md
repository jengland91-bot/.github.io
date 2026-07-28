# Dust Valley Ultra

Mid-to-big **fast desert Ultra 4** map for BeamNG.drive.

- **Size:** 4 km × 4 km (`4096` m)
- **Feel:** open desert speed, whoops, valley cut, jumps
- **Side content:** technical rock trails off the main loop
- **Default spawn:** pits / staging (southwest)

This repo ships the design, a 16-bit heightmap, spawn metadata, and World Editor build steps. BeamNG still needs a binary `.ter` terrain created/imported in the World Editor (that step is in-game).

## Layout

| Zone | What it is |
| --- | --- |
| Main desert loop | Fast Ultra 4 sand corridor with soft berms |
| Whoops field | West/SW rhythmic whoops on the loop |
| Valley cut | North speed wash / carved valley |
| Jump line | South tabletops and lips |
| East + NW rock trails | Technical rocky shelves off to the side |
| Pits | Flat staging pad |

Color overview: [`source/layout_overview.png`](source/layout_overview.png)

**Minimap:** each trail is a different color (gold loop, orange whoops, blue valley, red jumps, purple east rocks, teal NW rocks, green pits). See [`source/trail_colors.json`](source/trail_colors.json).

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

BeamNG stores terrain in a binary `.ter` file. Use the heightmap we generated:

1. In BeamNG, open **World Editor**.
2. Create a **Starter Level**, rename/move it to `levels/dust_valley_ultra` (or copy our `info.json` + `main/` into your new level folder).
3. Terrain Editor → **Heightmap Import**.
4. Import `source/heightmap_2048.png` with:
   - **Resolution:** 2048
   - **squareSize:** `2` (world = 4096 m)
   - **maxHeight:** about `180`
5. Save the level (this writes the `.ter`).
6. Paint materials:
   - loop / whoops / valley floor → desert sand / dirt groundmodels
   - rock trails → rock / gravel groundmodels
7. Nudge spawn spheres so their Z sits just above terrain.
8. Export a `preview.png` screenshot into the level folder.
9. Optional: copy `source/layout_overview.png` to `levels/dust_valley_ultra/minimap/terrain.png` as a temporary minimap.

Full author notes: [`docs/DESIGN.md`](docs/DESIGN.md)

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
│   ├── heightmap_2048.png
│   ├── layout_overview.png
│   └── ...
└── levels/dust_valley_ultra/
    ├── info.json
    └── main/items.level.json
```
