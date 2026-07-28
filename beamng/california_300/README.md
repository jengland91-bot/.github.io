# California 300 — ready-to-copy BeamNG package

I can’t create folders on your Windows PC from here, so this package is ready for you to copy.

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
