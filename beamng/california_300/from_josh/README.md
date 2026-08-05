# MapNG exports from Josh (Aug 2026)

Drive folder: https://drive.google.com/drive/folders/1mXVKDzIMhNKA0uHalEWK_cCcZiTYVpS8

## Received
- `heightmap_34.7453_-117.1046 (1|2).png` — 16384² 16-bit USGS 1m (duplicates)
- `texture_34.7453_-117.1046 (1).png` — 8192² satellite
- `osm_texture_34.7453_-117.1046 (1).png` — 8192² OSM overlay

## Integrated into level
- Height → downsampled to `import/heightmap_4096.png` and baked into `theTerrain.ter` (maxHeight 900, squareSize 4)
- Satellite → `art/terrains/mapng_satellite_*.jpg` on `desert_base` (unique map, TexSize 16384)

Large source PNGs are gitignored; keep them locally or on Drive.
