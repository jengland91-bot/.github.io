# Dust Valley Ultra — Design

## Goal

A **big** Ultra 4 desert park with:

1. An outer **~20 mile long course** for full Ultra 4 desert racing
2. A **~5 mile short course** in the middle for practice / sprint sessions
3. Whoops, valleys, jumps on the long course
4. Rock trails parked off to the sides

## Map scale

| Setting | Value |
| --- | --- |
| World size | 16384 m × 16384 m (~10.2 mi across) |
| Heightmap resolution | 4096 × 4096 |
| squareSize | 4 m |
| Target maxHeight | ~280 m |
| Origin / terrain corner | TerrainBlock typically at `[-8192, -8192, 0]` |
| Long course | ~20.5 miles (design polyline) |
| Short course | ~4.9 miles (design polyline) |

Coordinates in `items.level.json` spawns assume a centered park (roughly −8192…+8192 on X/Y).

## Difficulty

- **Design / heightmap / minimap:** straightforward — this package.
- **Getting it driveable in BeamNG:** one World Editor heightmap import.
- **Keeping ~20.0 mi exact after sculpting:** extra pass with DecalRoads + distance check.
- **Performance:** 4 m samples are the practical compromise for a 16 km park; finer grids (2 m @ 8192) are heavier.

## Driving fantasy

1. Leave the **pits**, choose long or short.
2. **Short course (cyan):** tight middle loop for warm-ups and short-course style runs.
3. **Long course (gold):** hammer the outer desert — whoops west, valley north, jumps south.
4. Anytime: peel to **east / NW rock trails**, then rejoin the sand.

## Minimap trail colors

| Trail | Color | Hex | Approx length |
| --- | --- | --- | --- |
| Long course | Gold | `#F2C747` | ~20.5 mi |
| Short course | Cyan | `#5AD2FF` | ~4.9 mi |
| Whoops field | Orange | `#F27326` | feature |
| Valley speed cut | Blue | `#408CDC` | feature |
| Jump / tabletop line | Red | `#E63746` | feature |
| East rock trail | Purple | `#A85CDC` | feature |
| NW rock trail | Teal | `#28BEAF` | feature |
| Pits / staging | Green | `#32C86E` | feature |

Source of truth: `source/trail_colors.json` / `source/course_lengths.json`.

## Spawn list

| Name | Role |
| --- | --- |
| `spawns_pits` | Default staging |
| `spawns_long_course` | Outer ~20 mi start |
| `spawns_short_course` | Inner ~5 mi start |
| `spawns_whoops` | Whoops entry |
| `spawns_valley` | Valley speed section |
| `spawns_jumps` | Jump line |
| `spawns_rocks_east` | East rock trail |
| `spawns_rocks_nw` | NW rock trail |

After heightmap import, always re-check spawn Z heights in World Editor.

## Material / groundmodel direction

| Area | Look | Suggested ground feel |
| --- | --- | --- |
| Long + short courses + pits | Light tan packed dirt/sand | dirt / sand |
| Whoops | Soft sand | sand |
| Valley floor | Harder wash dirt | dirt / gravel |
| Rock trails | Broken rock + gravel | rock / gravel |
| Berms | Slightly darker dirt | dirt |

## Props / atmosphere (later pass)

1. Terrain + materials + spawns
2. Rock TSStatics / Forest on side trails only
3. Sparse desert shrubs — don’t clog either race line
4. Hot dry TOD, light dust fog
5. Optional quickrace definitions: `long_course` and `short_course`

## Next build iterations

1. Import heightmap → drive short course, then long course
2. Soften whoops / jump lips as needed
3. Paint sand vs rock materials
4. Place rock meshes on side trails
5. Add DecalRoad ribbons if you want AI / measured race distance
6. Capture real `preview.png` + verify minimap alignment
7. Package `levels/dust_valley_ultra` as the mod zip
