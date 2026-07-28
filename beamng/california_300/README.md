# California 300 — ready-to-copy BeamNG package

I can’t create folders on your Windows PC from here, so this package is ready for you to copy.

## If the `levels` folder “disappears”

It usually did **not** get deleted. Windows AppData is easy to click out of.

Permanent path (Win+R, paste, Enter):

`%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels`

Or download and run:

`beamng/california_300/scripts/OPEN_LEVELS_FOLDER.bat`

That opens the folder and puts a **BeamNG Levels** shortcut on your Desktop.

## Fix GPX scale (map too small)

I can’t press Import inside BeamNG on your PC. Run this on Windows instead:

`beamng/california_300/scripts/FIX_SCALE.bat`

It will:
- recreate `levels\california_300` if needed
- recover `theTerrain.ter` from BeamNG cleanup/backup folders when possible
- patch paths from `template` → `california_300`
- force scale fields toward **squareSize=4** / **maxHeight=900**
- open a short checklist for the one Import click BeamNG still needs

Import settings that match the CA300 GPX footprint:
- heightmap: `heightmap_4096.png`
- meters per pixel: **4**
- max height: **900**
- position after import: **-8192, -8192, 0**

## Fastest way on your PC

### 1) Download this folder from GitHub
From branch `cursor/dust-valley-ultra-map-65dc`:

`beamng/california_300/levels/california_300/`

### 2) Put it here
Copy the whole `california_300` folder to:

`C:\Users\Josh England\AppData\Local\BeamNG\BeamNG.drive\current\levels\california_300`

Final path must look like:

`...\levels\california_300\info.json`

### 3) Optional: auto-fix your current messed-up levels folder
If files like `theTerrain.ter` are sitting directly in `levels`, run:

`beamng/california_300/scripts/fix_levels_folder.ps1`

In PowerShell:
```powershell
cd path\to\fix_levels_folder.ps1
powershell -ExecutionPolicy Bypass -File .\fix_levels_folder.ps1
```

### 4) Open in BeamNG
1. F11
2. File → Open Level → `california_300`
3. Terrain → Heightmap Import
4. Use file from:
   `beamng/california_300/import/heightmap_4096.png`
5. Settings:
   - squareSize = **4**
   - maxHeight = **900**
6. Save

That’s it.
