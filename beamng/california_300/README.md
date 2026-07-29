# California 300 — BeamNG package

Desert race park for BeamNG.drive, built around the **2024 California 300 Race Ready** GPX.

**Name:** California 300 only (`california_300`)  
**Not used:** Dust Valley / `dust_valley_ultra` (retired name)

## Install into BeamNG (do this)

### Easiest download (ZIP — works when .bat opens in a browser)

Open this page and tap **Download Install ZIP**:

https://jengland91-bot.github.io/ca300.html

Or direct ZIP:

https://jengland91-bot.github.io/beamng/california_300/California_300_Install.zip

1. Extract the ZIP
2. Double-click `INSTALL_CALIFORNIA_300.bat`
3. Follow `DO_THIS_NOW.txt`

### In BeamNG after install

1. Freeroam → **California 300**
2. Import Terrain → **Load preset** `ca300_gpx_scale.preset.json`
3. Confirm **Meters per Pixel = 4**, **Max Height = 900**
4. Import → Ctrl+S

## Scale (locked to GPX)

| Setting | Value |
|---|---|
| World size | **16384 × 16384 m** |
| Heightmap | `import/heightmap_4096.png` |
| squareSize | **4** |
| maxHeight | **900** |
| Terrain position | **-8192, -8192, 0** |
| Geo scale | **~0.9666×** real CA300 footprint |

## What’s in the level

- SRTM elevation under the CA300 course area
- DecalRoad `ca300_race_ready` + pit row from GPX
- Spawns at pits / course start
- Google Earth paint notes: `docs/EARTH_PAINT_GUIDE.md`
- Course GPX/KML: `source/reference/ca300/`

## After a BeamNG update

Major updates may move `levels` into a backup folder. Re-run `INSTALL_CALIFORNIA_300.bat` or copy `california_300` back into:

`%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\`
