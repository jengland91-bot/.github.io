# Real elevation (SRTM)

Bakes **real ground height** under the CA300 footprint from SRTM 1-arcsec tile `N34W118`.

## Why maxHeight = 900
Course/footprint relief is roughly **700–800 m**. BeamNG’s `maxHeight` must cover that or hills get crushed.

## Regenerate
```bash
python3 source/reference/elevation/bake_srtm_heightmap.py
# or via the full pipeline:
python3 source/generate_heightmap.py
```

The `.hgt` file is downloaded on demand and gitignored.
