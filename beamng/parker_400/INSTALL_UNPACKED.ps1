# Parker 400 installer for BeamNG 0.39.1
# Right-click → Run with PowerShell   OR   run from RUN_INSTALL.cmd
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
$Log = Join-Path $ScriptDir "INSTALL_LOG.txt"

function Write-Log($msg) {
  $line = "$(Get-Date -Format o)  $msg"
  Add-Content -Path $Log -Value $line
  Write-Host $msg
}

try {
  "Parker 400 install started" | Set-Content $Log
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "  PARKER 400 - UNPACKED INSTALL (BeamNG 0.39.1)"
  Write-Host "============================================================"
  Write-Host ""
  Write-Log "Folder: $ScriptDir"

  $modZip = $null
  foreach ($c in @(
    (Join-Path $ScriptDir "parker_400.zip"),
    (Join-Path $ScriptDir "mods_drop_in\parker_400.zip")
  )) {
    if (Test-Path $c) { $modZip = $c; break }
  }

  if (-not $modZip) {
    Write-Host "ERROR: parker_400.zip not found next to this script."
    Write-Host "Extract Parker400_Download_Both.zip first."
    Write-Host "See MANUAL_INSTALL.txt"
    Write-Log "ERROR missing zip"
    Read-Host "Press Enter to close"
    exit 1
  }
  Write-Log "Using zip: $modZip"

  $user = Join-Path $env:LOCALAPPDATA "BeamNG\BeamNG.drive\current"
  if (-not (Test-Path (Join-Path $user "mods"))) {
    Write-Host "Could not auto-find BeamNG folder."
    Write-Host "Launcher -> Manage User Folder -> Open, then paste path:"
    $user = Read-Host "Path"
  }
  if (-not (Test-Path (Join-Path $user "mods"))) {
    Write-Host "ERROR: no mods folder at $user"
    Write-Log "ERROR bad user $user"
    Read-Host "Press Enter to close"
    exit 1
  }
  Write-Log "User: $user"

  # Clean old installs (zip mod, unpacked mod, AND loose levels copy)
  $oldZip = Join-Path $user "mods\parker_400.zip"
  $oldLevel = Join-Path $user "levels\parker_400"
  $dest = Join-Path $user "mods\unpacked\parker_400"
  if (Test-Path $oldZip) { Remove-Item $oldZip -Force; Write-Log "Removed old mods\parker_400.zip" }
  if (Test-Path $oldLevel) { Remove-Item $oldLevel -Recurse -Force; Write-Log "Removed old levels\parker_400" }
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force; Write-Log "Removed old unpacked mod" }
  New-Item -ItemType Directory -Path $dest -Force | Out-Null

  Write-Host "Extracting to mods\unpacked\parker_400 ... wait"
  Expand-Archive -LiteralPath $modZip -DestinationPath $dest -Force

  $levelRoot = Join-Path $dest "levels\parker_400"
  $ter = Join-Path $levelRoot "theTerrain.ter"
  $info = Join-Path $levelRoot "info.json"
  $preview = Join-Path $levelRoot "preview.jpg"

  if (-not (Test-Path $ter)) {
    Write-Host "ERROR: theTerrain.ter missing after extract"
    Write-Log "ERROR missing ter"
    Read-Host "Press Enter to close"
    exit 1
  }
  if (-not (Test-Path $info)) {
    Write-Host "ERROR: info.json missing — Freeroam will not list Parker 400"
    Write-Log "ERROR missing info.json"
    Read-Host "Press Enter to close"
    exit 1
  }
  if (-not (Test-Path $preview)) {
    Write-Host "ERROR: preview.jpg missing — Freeroam thumbnail will be blank"
    Write-Log "ERROR missing preview.jpg"
    Read-Host "Press Enter to close"
    exit 1
  }

  # Also install into user levels\ so Freeroam always discovers the map
  # (some 0.39 installs miss unpacked mods in the level selector)
  $levelsParent = Join-Path $user "levels"
  New-Item -ItemType Directory -Path $levelsParent -Force | Out-Null
  Write-Host "Copying level into levels\parker_400 for Freeroam..."
  Copy-Item -LiteralPath $levelRoot -Destination $oldLevel -Recurse -Force
  Write-Log "Copied level to $oldLevel"

  $len = (Get-Item $ter).Length
  Write-Log "Terrain bytes: $len"

  $cache = Join-Path $user "temp\art\terrainMaterialCache"
  if (Test-Path $cache) { Remove-Item $cache -Recurse -Force -ErrorAction SilentlyContinue }

  # Clear level list / mod DB caches that can hide maps
  foreach ($extra in @(
    (Join-Path $user "temp\cache"),
    (Join-Path $user "temp\shaders")
  )) {
    if (Test-Path $extra) {
      Write-Log "Note: left $extra (optional clear via launcher Clear cache)"
    }
  }

  Write-Host ""
  Write-Host "SUCCESS"
  Write-Host "Mod path:   $levelRoot"
  Write-Host "Level path: $oldLevel"
  Write-Host "Terrain bytes: $len  (want ~50331681)"
  Write-Host "preview.jpg: OK"
  Write-Host "info.json:   OK"
  Write-Host ""
  Write-Host "NEXT:"
  Write-Host "  1) Fully quit BeamNG (and launcher)"
  Write-Host "  2) Start BeamNG"
  Write-Host "  3) Repository / Mods -> make sure nothing blocks local mods"
  Write-Host "  4) Freeroam -> search PARKER -> select Parker 400"
  Write-Host "     (desert thumbnail, NOT West Coast / Belasco City)"
  Write-Log "SUCCESS"
} catch {
  Write-Host "ERROR: $($_.Exception.Message)"
  Write-Log "EXCEPTION $($_.Exception.Message)"
}

Write-Host ""
Read-Host "Press Enter to close"
