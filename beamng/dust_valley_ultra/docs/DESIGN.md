# Dust Valley Ultra — Design

## Goal

A **mid-to-big** Ultra 4 park that feels like a **fast desert**: long sandy speed sections, whoops, valleys, and jumps on the main line, with **rock trails parked off to the sides** so you can peel off for technical driving without killing the desert flow.

## Map scale

| Setting | Value |
| --- | --- |
| World size | 4096 m × 4096 m |
| Heightmap resolution | 2048 × 2048 |
| squareSize | 2 m |
| Target maxHeight | ~180 m |
| Origin / terrain corner | TerrainBlock typically at `[-2048, -2048, 0]` |

Coordinates in `items.level.json` spawns assume a centered park (roughly −2048…+2048 on X/Y).

## Driving fantasy

1. Leave the **pits**, hammer the desert loop.
2. Hit the **whoops** — keep momentum, don’t get bucked offline.
3. Commit the **valley cut** — walls close in, speed stays high.
4. South **jump line** for tabletops / step-ups.
5. Anytime: bail to **east** or **NW rock trails** for Ultra 4 technical work, then rejoin the sand.

## Minimap trail colors

The in-game minimap (`levels/dust_valley_ultra/minimap/terrain.png`) draws **each trail in its own color**:

| Trail | Color | Hex |
| --- | --- | --- |
| Main Ultra 4 loop | Gold | `#F2C747` |
| Whoops field | Orange | `#F27326` |
| Valley speed cut | Blue | `#408CDC` |
| Jump / tabletop line | Red | `#E63746` |
| East rock trail | Purple | `#A85CDC` |
| NW rock trail | Teal | `#28BEAF` |
| Pits / staging | Green | `#32C86E` |

Source of truth: `source/trail_colors.json` (regenerated with the heightmap script).

## Zone breakdown

### 1. Main desert loop (gold)

- Wide packed-sand corridor, soft berm edges.
- Primary Ultra 4 racing line.
- Keep props light so high-speed sightlines stay clean.

### 2. Whoops field (orange)

- West / southwest of the loop.
- Rhythmic sine whoops along the travel direction.
- Good for suspension torture and throttle control.

### 3. Valley cut (blue)

- North-central carved wash.
- Lower floor, raised walls — a speed funnel.
- Pair later with DecalRoad dirt if you want a clearer racing line.

### 4. Jump line (red)

- Southern arc of tabletops + lips.
- Designed as terrain shapes first; you can refine lips in Terrain Editor with Set Height / Slope brushes.

### 5. Rock trails (purple east / teal NW)

- **East ridge (purple):** longer rocky shelf trail parallel to the loop.
- **Northwest (teal):** tighter climb / broken rock.
- Narrower troughs carved through high-frequency rock noise so there’s a readable line without flattening the whole ridge.

### 6. Pits / staging (green)

- Flat SW pad for grid, recovery, and photo spawns.
- Default spawn: `spawns_pits`.

## Spawn list

| Name | Role |
| --- | --- |
| `spawns_pits` | Default staging |
| `spawns_whoops` | Whoops entry |
| `spawns_valley` | Valley speed section |
| `spawns_jumps` | Jump line |
| `spawns_rocks_east` | East rock trail |
| `spawns_rocks_nw` | NW rock trail |

After heightmap import, always re-check spawn Z heights in World Editor.

## Material / groundmodel direction

Use BeamNG terrain materials named to match groundmodels where possible:

| Area | Look | Suggested ground feel |
| --- | --- | --- |
| Loop + pits | Light tan sand / packed dirt | dirt / sand aliases |
| Whoops | Soft sand | sand |
| Valley floor | Harder wash dirt | dirt / gravel |
| Rock trails | Broken rock + gravel | rock / gravel |
| Berms | Slightly darker dirt | dirt |

Exact material names should match aliases in `art/groundmodels.json` so tire friction feels right.

## Props / atmosphere (later pass)

Keep the first playable lean:

1. Terrain + materials + spawns
2. A few rock TSStatics on the side trails (or Forest items)
3. Sparse desert shrubs — don’t clog the fast line
4. Hot dry TOD, light dust fog (`fogDensity` already nudged warm in LevelInfo)
5. Optional race checkpoints / quickrace once the nav line exists

## What this package cannot do alone

BeamNG’s driveable terrain lives in a binary `.ter` created by the engine/World Editor. We provide:

- design + heightmap source
- `info.json` metadata
- spawn / environment scene stubs

You import the heightmap once in-game to produce the `.ter`, then iterate sculpt/paint there.

## Next build iterations (suggested order)

1. Import heightmap → drive the loop once
2. Soften any spikes on whoops / jump lips
3. Paint sand vs rock materials
4. Place rock meshes on side trails
5. Add DecalRoad race ribbon if AI/quickrace is desired
6. Capture real `preview.png` + minimap screenshot
7. Package `levels/dust_valley_ultra` as the mod zip
