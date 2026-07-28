# California 300 - fix BeamNG folders (run in PowerShell)
# This creates missing folders and copies california_300 from Desktop if found.

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " California 300 BeamNG folder fixer"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$beamRoot = Join-Path $env:LOCALAPPDATA "BeamNG\BeamNG.drive\current"
$levels   = Join-Path $beamRoot "levels"
$mods     = Join-Path $beamRoot "mods"
$target   = Join-Path $levels "california_300"

Write-Host "Logged in Windows user: $env:USERNAME"
Write-Host "BeamNG current folder:  $beamRoot"
Write-Host ""

if (-not (Test-Path $beamRoot)) {
  Write-Host "ERROR: BeamNG current folder not found at:" -ForegroundColor Red
  Write-Host "  $beamRoot"
  Write-Host ""
  Write-Host "Open BeamNG once, then run this script again."
  Read-Host "Press Enter to close"
  exit 1
}

# Create required folders
New-Item -ItemType Directory -Force -Path $levels | Out-Null
New-Item -ItemType Directory -Force -Path $mods | Out-Null
Write-Host "OK: levels folder exists at:" -ForegroundColor Green
Write-Host "  $levels"

# Possible places the downloaded map might already be
$candidates = @(
  (Join-Path $env:USERPROFILE "Desktop\california_300"),
  (Join-Path $env:USERPROFILE "OneDrive\Desktop\california_300"),
  (Join-Path $env:USERPROFILE "Downloads\california_300"),
  (Join-Path $env:USERPROFILE "Desktop\california_300\california_300"),
  (Join-Path $env:USERPROFILE "OneDrive\Desktop\california_300\california_300")
)

$source = $null
foreach ($c in $candidates) {
  if (Test-Path (Join-Path $c "info.json")) {
    $source = $c
    break
  }
}

if (-not $source) {
  Write-Host ""
  Write-Host "Could not find california_300 with info.json on Desktop/Downloads." -ForegroundColor Yellow
  Write-Host "I still created the levels folder for you."
  Write-Host ""
  Write-Host "Next:"
  Write-Host "1) Copy your california_300 folder into:"
  Write-Host "   $levels"
  Write-Host "2) Make sure this file exists:"
  Write-Host "   $levels\california_300\info.json"
  Write-Host ""
  explorer.exe $levels
  Read-Host "Press Enter to close"
  exit 0
}

Write-Host ""
Write-Host "Found map source:" -ForegroundColor Green
Write-Host "  $source"

# Copy / refresh into BeamNG levels
if (Test-Path $target) {
  Write-Host "Target already exists, updating files..."
} else {
  New-Item -ItemType Directory -Force -Path $target | Out-Null
}

Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force
Write-Host "OK: copied into:" -ForegroundColor Green
Write-Host "  $target"

# If loose level files are sitting directly in /levels, move them into california_300
$loose = @(
  "art","import","main","info.json","map.json",
  "theTerrain.ter","theTerrain.terrain.json",
  "main.decals.json","main.forestbrushes.json",
  ".forest.json",".ter.depth.png","_preview.png","preview.png"
)
foreach ($name in $loose) {
  $src = Join-Path $levels $name
  $dst = Join-Path $target $name
  if ((Test-Path $src) -and ($src -ne $dst)) {
    if (-not (Test-Path $dst)) {
      Move-Item -Path $src -Destination $dst -Force
      Write-Host "Moved loose file/folder into map: $name"
    }
  }
}

Write-Host ""
Write-Host "DONE." -ForegroundColor Green
Write-Host "Final map path:"
Write-Host "  $target"
if (Test-Path (Join-Path $target "info.json")) {
  Write-Host "info.json: FOUND" -ForegroundColor Green
} else {
  Write-Host "info.json: MISSING" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next in BeamNG:"
Write-Host "1) Press F11"
Write-Host "2) File -> Open Level -> california_300"
Write-Host "3) Import heightmap_4096.png"
Write-Host "   squareSize = 4"
Write-Host "   maxHeight = 900"
Write-Host ""

explorer.exe $levels
Read-Host "Press Enter to close"
