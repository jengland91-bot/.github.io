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

  $oldZip = Join-Path $user "mods\parker_400.zip"
  $oldLevel = Join-Path $user "levels\parker_400"
  $dest = Join-Path $user "mods\unpacked\parker_400"
  if (Test-Path $oldZip) { Remove-Item $oldZip -Force }
  if (Test-Path $oldLevel) { Remove-Item $oldLevel -Recurse -Force }
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  New-Item -ItemType Directory -Path $dest -Force | Out-Null

  Write-Host "Extracting (1-2 minutes)... wait"
  Expand-Archive -LiteralPath $modZip -DestinationPath $dest -Force

  $ter = Join-Path $dest "levels\parker_400\theTerrain.ter"
  if (-not (Test-Path $ter)) {
    Write-Host "ERROR: theTerrain.ter missing after extract"
    Write-Log "ERROR missing ter"
    Read-Host "Press Enter to close"
    exit 1
  }
  $len = (Get-Item $ter).Length
  Write-Log "Terrain bytes: $len"

  $cache = Join-Path $user "temp\art\terrainMaterialCache"
  if (Test-Path $cache) { Remove-Item $cache -Recurse -Force -ErrorAction SilentlyContinue }

  Write-Host ""
  Write-Host "SUCCESS"
  Write-Host "Installed: $ter"
  Write-Host "Terrain bytes: $len  (want ~50331692)"
  Write-Host ""
  Write-Host "NEXT: quit BeamNG fully -> start -> Mods enable -> Freeroam -> parker"
  Write-Log "SUCCESS"
} catch {
  Write-Host "ERROR: $($_.Exception.Message)"
  Write-Log "EXCEPTION $($_.Exception.Message)"
}

Write-Host ""
Read-Host "Press Enter to close"
