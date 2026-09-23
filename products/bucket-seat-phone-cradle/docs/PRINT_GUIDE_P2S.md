# Bambu Lab P2S — print guide (SOLID v5)

## Slice these first

1. `01_cradle_evo.stl` alone — confirm it loads, slices, and shows a filled body (not hollow open surfaces).
2. Then `02` or `03` for your rail, or `06`+`08` for Evolve 40 mm tube.

## Settings that work

| | Cradle | Backs / legs | Clamps |
|-|--------|--------------|--------|
| Layer | 0.20 mm | 0.20 mm | 0.20 mm |
| Walls | 4 | 4 | 5 |
| Infill | 25% gyroid | 30% | 40% |
| Material | PETG preferred | PETG | PETG |
| Supports | Tree if needed on underside of wings | Usually none | Tree in C-clamp throat if needed |
| Orientation | Flat on rear boss OR upright on base | Plate flat on bed | Split face on bed |

## Fit

- Phone pocket ≈ **92 × 18 × 70 mm**
- Charge notch at bottom center
- Backs use **4× M3 on 30 mm square**
- Tube clamp bore ≈ **40.4 mm** (Evolve-style tube)

## If Studio says “non-manifold”

v5 meshes are solid voxel CSG. Tiny open-edge counts are normal and usually still print. Use Studio’s “Fix model” if needed, then slice again.
