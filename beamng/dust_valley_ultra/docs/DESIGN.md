# Dust Valley Ultra — Design

## Goal

A **CA300-focused** desert race park: one race line based on the **2024 California 300 Race Ready** GPX, plus pit row and danger-inspired terrain. No short course — the map is about that course and the desert around it.

## Map scale

| Setting | Value |
| --- | --- |
| World size | 16384 m × 16384 m (~10.2 mi across) |
| Heightmap resolution | 4096 × 4096 |
| squareSize | 4 m |
| Target maxHeight | ~280 m |
| Course source | 2024 CA300 C/T/U Race Ready GPX |
| Course length | ~74 mi source (~68 mi downsampled corridor) |
| Fit scale | ~0.97× geographic |

## What’s on the map

1. **CA300 course** (gold) — main race corridor  
2. **Pit row** (green) — staging  
3. **Danger markers** — g-outs, rocks, washouts, faces, poles from the official danger file  
4. **Open desert freeroam** — everything else

## Spawns

| Name | Role |
| --- | --- |
| `spawns_pits` | Default staging / start-finish |
| `spawns_course` | On the race line |

## Next passes

1. Import heightmap in World Editor  
2. Soften danger hits that feel too sharp  
3. Paint packed dirt on the race ribbon  
4. Place rock props only where CA300 marks rocks/boulders  
5. Optional: DecalRoad ribbon + race miles / VCP checkpoints from the GPX waypoints  
