# Fix California 300 map scale / paths for BeamNG
# Run on your Windows PC (double-click FIX_SCALE.bat)

$ErrorActionPreference = "Continue"
$beamRoot = Join-Path $env:LOCALAPPDATA "BeamNG\BeamNG.drive"
$current = Join-Path $beamRoot "current"
$levels = Join-Path $current "levels"
$target = Join-Path $levels "california_300"

Write-Host "========================================"
Write-Host " California 300 scale fixer"
Write-Host "========================================"
Write-Host ""
Write-Host "User: $env:USERNAME"
Write-Host "BeamNG current: $current"
Write-Host ""

if (-not (Test-Path $current)) {
  Write-Host "ERROR: BeamNG current folder not found."
  Write-Host "Open BeamNG once, close it, then run again."
  Read-Host "Press Enter to close"
  exit 1
}

New-Item -ItemType Directory -Force -Path $levels | Out-Null
New-Item -ItemType Directory -Force -Path $target | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $target "import") | Out-Null

# Recover california_300 / theTerrain.ter from cleanup backups next to current
function Find-MapSources {
  $hits = @()
  if (Test-Path $beamRoot) {
    Get-ChildItem -Path $beamRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
      $cand = Join-Path $_.FullName "levels\california_300"
      if (Test-Path (Join-Path $cand "theTerrain.ter")) { $hits += $cand }
      $cand2 = Join-Path $_.FullName "california_300"
      if (Test-Path (Join-Path $cand2 "theTerrain.ter")) { $hits += $cand2 }
      $ter = Get-ChildItem -Path $_.FullName -Filter "theTerrain.ter" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 3
      foreach ($t in $ter) {
        $dir = Split-Path $t.FullName -Parent
        if ($hits -notcontains $dir) { $hits += $dir }
      }
    }
  }
  return $hits
}

if (-not (Test-Path (Join-Path $target "theTerrain.ter"))) {
  Write-Host "Looking in BeamNG backups for your terrain..."
  $sources = Find-MapSources
  foreach ($src in $sources) {
    if ($src -eq $target) { continue }
    Write-Host "Found terrain source: $src"
    Write-Host "Copying missing files into current levels\california_300 ..."
    Copy-Item -Path (Join-Path $src "*") -Destination $target -Recurse -Force -ErrorAction SilentlyContinue
    break
  }
}

# Copy heightmap from common download locations if missing
$hmDest = Join-Path $target "import\heightmap_4096.png"
if (-not (Test-Path $hmDest)) {
  $hmCandidates = @(
    (Join-Path $env:USERPROFILE "Desktop\heightmap_4096.png"),
    (Join-Path $env:USERPROFILE "Desktop\california_300\heightmap_4096.png"),
    (Join-Path $env:USERPROFILE "Desktop\california_300\import\heightmap_4096.png"),
    (Join-Path $env:USERPROFILE "OneDrive\Desktop\heightmap_4096.png"),
    (Join-Path $env:USERPROFILE "OneDrive\Desktop\california_300\import\heightmap_4096.png"),
    (Join-Path $env:USERPROFILE "Downloads\heightmap_4096.png"),
    (Join-Path $target "heightmap_4096.png")
  )
  foreach ($c in $hmCandidates) {
    if (Test-Path $c) {
      Copy-Item $c $hmDest -Force
      Write-Host "Copied heightmap to: $hmDest"
      break
    }
  }
}

# Patch JSON text: template paths -> california_300, force scale fields where present
function Patch-TextFile([string]$path) {
  if (-not (Test-Path $path)) { return $false }
  $raw = Get-Content -Path $path -Raw -ErrorAction SilentlyContinue
  if ($null -eq $raw) { return $false }
  $orig = $raw
  $raw = $raw -replace '/levels/template/', '/levels/california_300/'
  $raw = $raw -replace '\\levels\\template\\', '\levels\california_300\'
  $raw = $raw -replace '"squareSize"\s*:\s*[0-9.]+', '"squareSize": 4.0'
  $raw = $raw -replace '"maxHeight"\s*:\s*[0-9.]+', '"maxHeight": 900.0'
  # Common TerrainBlock position patterns (array form)
  $raw = $raw -replace '"position"\s*:\s*\[\s*-?512\s*,\s*-?512\s*,\s*[0-9.+-]+\s*\]', '"position": [-8192, -8192, 0]'
  $raw = $raw -replace '"position"\s*:\s*\[\s*-?2048\s*,\s*-?2048\s*,\s*[0-9.+-]+\s*\]', '"position": [-8192, -8192, 0]'
  $raw = $raw -replace '"position"\s*:\s*\[\s*8192\s*,\s*8192\s*,\s*[0-9.+-]+\s*\]', '"position": [-8192, -8192, 0]'
  if ($raw -ne $orig) {
    Set-Content -Path $path -Value $raw -Encoding UTF8
    return $true
  }
  return $false
}

Write-Host ""
Write-Host "Patching level JSON files for GPX scale (squareSize=4, maxHeight=900)..."
$patched = 0
Get-ChildItem -Path $target -Include *.json,*.level.json -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
  if (Patch-TextFile $_.FullName) {
    Write-Host "Patched: $($_.FullName)"
    $patched++
  }
}

# Ensure a correct companion terrain json if present
$terrainJson = Join-Path $target "theTerrain.terrain.json"
if (Test-Path $terrainJson) {
  Patch-TextFile $terrainJson | Out-Null
  # Also force datafile path if the file is simple enough
  try {
    $tj = Get-Content $terrainJson -Raw | ConvertFrom-Json
    if ($tj.datafile) { $tj.datafile = "levels/california_300/theTerrain.ter" }
    if ($tj.PSObject.Properties.Name -contains "squareSize") { $tj.squareSize = 4.0 }
    if ($tj.PSObject.Properties.Name -contains "maxHeight") { $tj.maxHeight = 900.0 }
    $tj | ConvertTo-Json -Depth 30 | Set-Content $terrainJson -Encoding UTF8
    Write-Host "Updated: theTerrain.terrain.json"
  } catch {
    Write-Host "Note: could not fully rewrite theTerrain.terrain.json (left text patches only)"
  }
}

# Desktop shortcut to levels
$shortcutPaths = @(
  (Join-Path $env:USERPROFILE "Desktop\BeamNG Levels.lnk"),
  (Join-Path $env:USERPROFILE "OneDrive\Desktop\BeamNG Levels.lnk")
)
foreach ($sc in $shortcutPaths) {
  $desk = Split-Path $sc -Parent
  if (Test-Path $desk) {
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut($sc)
    $s.TargetPath = $levels
    $s.Description = "BeamNG.drive levels folder"
    $s.Save()
  }
}

# Write a short instruction file next to the map
$readme = @"
CALIFORNIA 300 - SCALE FIX (GPX match)
=====================================

Target scale from CA300 GPX:
- Park: 16384 m x 16384 m (~10.2 miles across)
- Heightmap: heightmap_4096.png
- Meters per Pixel / squareSize: 4
- Max Height: 900
- Terrain position: -8192, -8192, 0

This script fixed file paths and JSON scale fields where possible.
BeamNG still needs ONE import click if the terrain was originally
imported at 1 meter/pixel:

IN BEAMNG:
1. Quit and reopen BeamNG
2. Freeroam -> California 300  (or F11 -> Open Level -> california_300)
3. F11 World Editor
4. Terrain -> Import Terrain
5. Height Map = import/heightmap_4096.png
6. Meters per Pixel = 4
7. Max Height = 900
8. Import
9. Select theTerrain -> position -8192, -8192, 0
10. terrainFile = /levels/california_300/theTerrain.ter
11. Ctrl+S

After a correct import, Inspector Size should be about 16384 x 16384
(not 4096 x 4096 world meters).
"@
Set-Content -Path (Join-Path $target "SCALE_FIX_README.txt") -Value $readme -Encoding UTF8

Write-Host ""
Write-Host "DONE."
Write-Host "Map folder: $target"
if (Test-Path (Join-Path $target "theTerrain.ter")) {
  Write-Host "theTerrain.ter: FOUND"
} else {
  Write-Host "theTerrain.ter: MISSING - restore from backup or re-import heightmap"
}
if (Test-Path $hmDest) {
  Write-Host "heightmap_4096.png: FOUND in import\"
} else {
  Write-Host "heightmap_4096.png: MISSING"
  Write-Host "Download:"
  Write-Host "https://github.com/jengland91-bot/.github.io/raw/cursor/dust-valley-ultra-map-65dc/beamng/california_300/import/heightmap_4096.png"
}
Write-Host "JSON files patched: $patched"
Write-Host ""
Write-Host "Opening map folder + instructions..."
notepad (Join-Path $target "SCALE_FIX_README.txt")
explorer $target
Write-Host ""
Read-Host "Press Enter to close"
