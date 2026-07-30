# ONE CLICK: install GPX-scaled California 300 into BeamNG user folder
# Downloads heightmap + Import preset + level files from GitHub, then opens instructions.

$ErrorActionPreference = "Continue"
$branch = "cursor/dust-valley-ultra-map-65dc"
$base = "https://raw.githubusercontent.com/jengland91-bot/.github.io/$branch/beamng/california_300"
$beamRoot = Join-Path $env:LOCALAPPDATA "BeamNG\BeamNG.drive"
$current = Join-Path $beamRoot "current"
$levels = Join-Path $current "levels"
$target = Join-Path $levels "california_300"

Write-Host "========================================"
Write-Host " INSTALL California 300 into BeamNG"
Write-Host "========================================"
Write-Host "Map name: California 300  (folder: california_300)"
Write-Host "Old name Dust Valley is retired."
Write-Host "User: $env:USERNAME"
Write-Host "Target: $target"
Write-Host ""

if (-not (Test-Path $current)) {
  Write-Host "ERROR: BeamNG folder missing: $current"
  Write-Host "Open BeamNG once, close it, run again."
  Read-Host "Press Enter"
  exit 1
}

New-Item -ItemType Directory -Force -Path "$target\import" | Out-Null
New-Item -ItemType Directory -Force -Path "$target\main" | Out-Null
New-Item -ItemType Directory -Force -Path "$target\minimap" | Out-Null
New-Item -ItemType Directory -Force -Path "$target\art" | Out-Null

function Get-GitFile([string]$rel, [string]$dest) {
  $url = "$base/$rel"
  Write-Host "Download: $rel"
  try {
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    return $true
  } catch {
    Write-Host "  FAILED: $url"
    Write-Host "  $($_.Exception.Message)"
    return $false
  }
}

# Recover existing theTerrain.ter from backups if present (keep user's prior import)
function Find-TerrainBackup {
  if (-not (Test-Path $beamRoot)) { return $null }
  $hit = Get-ChildItem -Path $beamRoot -Filter "theTerrain.ter" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 1MB } |
    Sort-Object Length -Descending |
    Select-Object -First 1
  if ($hit) { return $hit.FullName }
  return $null
}

if (-not (Test-Path "$target\theTerrain.ter")) {
  $bak = Find-TerrainBackup
  if ($bak) {
    Write-Host "Recovering terrain from: $bak"
    Copy-Item $bak "$target\theTerrain.ter" -Force
    $jsonBak = [IO.Path]::ChangeExtension($bak, ".terrain.json")
    if (Test-Path $jsonBak) { Copy-Item $jsonBak "$target\theTerrain.terrain.json" -Force }
  }
}

$ok = $true
$ok = (Get-GitFile "levels/california_300/info.json" "$target\info.json") -and $ok
$ok = (Get-GitFile "levels/california_300/preview.png" "$target\preview.png") -and $ok
$ok = (Get-GitFile "levels/california_300/main/items.level.json" "$target\main\items.level.json") -and $ok
$ok = (Get-GitFile "levels/california_300/minimap/terrain.png" "$target\minimap\terrain.png") -and $ok
$ok = (Get-GitFile "levels/california_300/import/ca300_gpx_scale.preset.json" "$target\import\ca300_gpx_scale.preset.json") -and $ok
$ok = (Get-GitFile "import/ca300_gpx_scale.preset.json" "$target\import\ca300_gpx_scale.preset.json") -and $ok
$ok = (Get-GitFile "DO_THIS_NOW.txt" "$target\DO_THIS_NOW.txt") -and $ok

# Heightmap is large (~11 MB)
$hm = "$target\import\heightmap_4096.png"
if (-not (Test-Path $hm) -or (Get-Item $hm).Length -lt 1MB) {
  Write-Host "Downloading heightmap_4096.png (about 11 MB)..."
  $ok = (Get-GitFile "import/heightmap_4096.png" $hm) -and $ok
} else {
  Write-Host "heightmap already present: $hm"
}

# Desert materials (dirt/rock) — empty library is normal without these
New-Item -ItemType Directory -Force -Path "$target\art\terrains" | Out-Null
$matZip = Join-Path $env:TEMP "california_300_desert_materials.zip"
Write-Host "Downloading desert materials..."
if (Get-GitFile "desert_materials.zip" $matZip) {
  try {
    Expand-Archive -Path $matZip -DestinationPath "$target\art" -Force
    Write-Host "Desert materials installed to art\terrains"
  } catch {
    Write-Host "Could not extract materials zip: $($_.Exception.Message)"
    $ok = $false
  }
} else {
  $ok = $false
}

# Patch any leftover template paths in local JSON
Get-ChildItem -Path $target -Include *.json,*.level.json -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
  $raw = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
  if ($null -eq $raw) { return }
  $new = $raw -replace '/levels/template/', '/levels/california_300/'
  $new = $new -replace '"squareSize"\s*:\s*1(\.0)?', '"squareSize": 4.0'
  $new = $new -replace '"maxHeight"\s*:\s*50(\.0)?', '"maxHeight": 900.0'
  if ($new -ne $raw) {
    Set-Content $_.FullName $new -Encoding UTF8
    Write-Host "Patched $($_.Name)"
  }
}

# Desktop shortcut
foreach ($desk in @("$env:USERPROFILE\Desktop", "$env:USERPROFILE\OneDrive\Desktop")) {
  if (Test-Path $desk) {
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut("$desk\BeamNG Levels.lnk")
    $s.TargetPath = $levels
    $s.Save()
    $s2 = $ws.CreateShortcut("$desk\California 300 - READ ME.lnk")
    $s2.TargetPath = "$target\DO_THIS_NOW.txt"
    $s2.Save()
  }
}

Write-Host ""
if ($ok) {
  Write-Host "INSTALL OK"
} else {
  Write-Host "INSTALL PARTIAL - some downloads failed (check internet)"
}
Write-Host "Map folder: $target"
Write-Host "Heightmap:  $(Test-Path $hm)"
Write-Host "Preset:     $(Test-Path "$target\import\ca300_gpx_scale.preset.json")"
Write-Host "Items:      $(Test-Path "$target\main\items.level.json")"
Write-Host "Terrain.ter:$(Test-Path "$target\theTerrain.ter")  (created after Import in BeamNG)"
Write-Host ""
Write-Host "Opening instructions..."
if (Test-Path "$target\DO_THIS_NOW.txt") { notepad "$target\DO_THIS_NOW.txt" }
explorer $target
Read-Host "Press Enter to close"
