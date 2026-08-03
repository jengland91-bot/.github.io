# Real elevation (SRTM) — Parker 400

Bakes **real ground height** under the 2026 Parker 400 C/T/UTV footprint from AWS Skadi SRTM 1-arcsec tiles:

- `N33W115`, `N33W114`, `N34W115`, `N34W114`

## Why maxHeight = 1500

Along the race line, relief is roughly **450–550 m**, but the full 65 km map square includes higher desert peaks (**~110–1400 m** SRTM). BeamNG’s `maxHeight` must cover the whole heightmap or distant hills get crushed. **1500 m** leaves headroom.

## Why 65536 m / squareSize 8

The official CTUTV loop spans ~**55.4 × 28.5 km**. BeamNG’s practical max heightmap is **8192²**, so:

| Setting | Value |
|---|---|
| Heightmap | **4096 × 4096** shipped (8192 HD optional) |
| squareSize | **16 m** shipped (**8 m** HD) |
| World | **65536 × 65536 m** |
| Geographic scale | **1.0** (true 1:1) |

## Regenerate

```bash
python3 scripts/convert_p400_to_map.py
python3 scripts/bake_srtm_heightmap.py
python3 scripts/bake_level.py
```

`.hgt` tiles download on demand and are gitignored.
