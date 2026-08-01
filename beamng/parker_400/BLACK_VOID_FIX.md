# Black void fix (BeamNG 0.39.1)

If Freeroam loads Parker 400 but the world is **black**, do this in order.

## 1) Use the UNPACKED installer (most reliable)

**Easiest — one file with both:**

1. Download [Parker400_Download_Both.zip](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/Parker400_Download_Both.zip)
2. Extract it (you get `parker_400.zip` + `INSTALL_UNPACKED.bat`)
3. Run **`INSTALL_UNPACKED.bat`**
4. Confirm it prints terrain size ≈ **50331692** bytes
5. Fully quit BeamNG → start → Freeroam → **parker**

Or download the two pieces separately into the same folder:

- [parker_400.zip](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip)
- [INSTALL_UNPACKED.bat](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/INSTALL_UNPACKED.bat)

Correct result path:

```
...\BeamNG.drive\current\mods\unpacked\parker_400\levels\parker_400\theTerrain.ter
```

## 2) Delete old broken copies

Remove these if they exist:

- `mods\parker_400.zip` (old/corrupt)
- `levels\parker_400\` (loose copy — ignored / stale)
- `temp\art\terrainMaterialCache\` (stale material cache)

Launcher → **Clear cache** (or delete `temp`) then restart.

## 3) Confirm the file is really there

Open:

`mods\unpacked\parker_400\levels\parker_400\`

You must see:

| File | Approx size |
|------|-------------|
| `theTerrain.ter` | ~48 MB (50331692 bytes) |
| `info.json` | small |
| `main\items.level.json` | ~80 KB |
| `art\terrains\parker400_base_color.jpg` | ~29 MB (8192 HD sat) |

If `theTerrain.ter` is missing, the download was incomplete — download again.

## 4) Console check in-game

1. Load the map
2. Press **`~`** (tilde) for console
3. Look for lines with `parker_400`, `theTerrain`, `TerrainBlock`, `material`

Send those lines if it is still black.

## Hills but pink/gray checkerboard ground

That means terrain loaded, but materials failed (BeamNG warning texture).

1. Re-download **Parker400_Download_Both.zip** (latest)
2. Run `INSTALL_UNPACKED.bat` again (it wipes the old unpack)
3. Delete `temp\art\terrainMaterialCache` (or Clear cache once)
4. Restart → load Parker 400 again

Latest package uses matching 4096 PBR texture-set + full Esri satellite base.

## Hills load but ground looks fake / course only on minimap

That is the old package (low-res sat, no painted course ribbon).

1. Re-download **Parker400_Download_Both.zip** (latest from this branch)
2. Run **`RUN_INSTALL.cmd`** (keeps the window open) or `INSTALL_UNPACKED.bat`
3. Delete `temp\art\terrainMaterialCache` (or Clear cache once)
4. Restart → spawn **Main Pit / Staging**
5. You should see:
   - Real Parker satellite desert color (not flat brown tiles)
   - Tan packed-dirt corridor painted on the GPX line
   - Dark asphalt DecalRoad on top of that corridor (same line as the minimap)

## What we fixed in the latest package

1. Shipped pre-baked `theTerrain.ter` (missing before = empty world)
2. Matching PBR texture-set (4096 base / 1024 macro+detail) + `materialTextureSet`
3. HD Esri World Imagery satellite (`parker400_base_color.jpg` 8192², ~8 m/px)
4. GPX course burned into sat + painted `course_pack` + wider DecalRoad
5. Unpacked install path so the big `.ter` cannot be skipped inside a zip
