# Dust Valley Ultra

**CA300-focused** desert race map for BeamNG.drive.

- **Park size:** ~16.4 km across (`16384` m / ~10.2 miles)
- **Course:** **2024 CA300 Race Ready** path (~**74 miles**, nearly 1:1 fit) — gold on minimap
- **Pit row:** from the same GPX — green
- **Dangers:** 68 CA300 markers (g-outs, rocks, washouts, poles…) — orange/red
- **Freeroam:** open desert around the race line (no short course)

This repo ships the design, a 16-bit heightmap, spawn metadata, and World Editor build steps. BeamNG still needs a binary `.ter` terrain created/imported in the World Editor (that step is in-game).

## Layout

| Zone | What it is | Minimap color |
| --- | --- | --- |
| CA300 course | Full Race Ready race line | Gold |
| Pit row | Staging / pits | Green |
| Dangers | G-outs, rocks, washouts, poles… | Orange / red |
| Open desert | Freeroam around the course | — |

CA300 reference: [`source/reference/ca300/`](source/reference/ca300/)  
Color overview: [`source/layout_overview.png`](source/layout_overview.png)

## Build the terrain in BeamNG (required once)

1. World Editor → create/rename level to `dust_valley_ultra`
2. Terrain Editor → **Heightmap Import** → `source/heightmap_4096.png`
3. Use **squareSize = 4**, **maxHeight ≈ 280**
4. Save (writes `.ter`), paint packed dirt on the race line, nudge spawn Z

Full notes: [`docs/DESIGN.md`](docs/DESIGN.md) · CA300 files: [`source/reference/ca300/README.md`](source/reference/ca300/README.md)

## Regenerate

```bash
python3 source/reference/ca300/convert_ca300_to_map.py
python3 source/generate_heightmap.py
```
