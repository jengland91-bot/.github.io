@echo off
setlocal EnableExtensions
title Install California 300 into BeamNG
echo ========================================
echo  INSTALL California 300 into BeamNG
echo ========================================
echo.
echo Map name: california_300
echo.

cd /d "%~dp0"

set "PS1=%~dp0ONE_CLICK_FIX.ps1"
set "PS1_URL=https://raw.githubusercontent.com/jengland91-bot/.github.io/cursor/dust-valley-ultra-map-65dc/beamng/california_300/scripts/ONE_CLICK_FIX.ps1"

if not exist "%PS1%" (
  echo ONE_CLICK_FIX.ps1 not found next to this .bat
  echo Downloading it now...
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { Invoke-WebRequest -Uri '%PS1_URL%' -OutFile '%PS1%' -UseBasicParsing; Write-Host 'Download OK' } catch { Write-Host $_.Exception.Message; exit 1 }"
  if errorlevel 1 (
    echo.
    echo Download failed. Do this instead:
    echo 1^) Download the ZIP:
    echo https://github.com/jengland91-bot/.github.io/raw/cursor/dust-valley-ultra-map-65dc/beamng/california_300/California_300_Install.zip
    echo 2^) Extract All
    echo 3^) Run INSTALL_CALIFORNIA_300.bat from inside that folder
    pause
    exit /b 1
  )
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
if errorlevel 1 pause
