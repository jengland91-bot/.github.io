@echo off
setlocal EnableExtensions
title Rise Above overlays - KEEP THIS WINDOW OPEN
color 0A
cd /d "%~dp0.."

echo.
echo ========================================
echo   KEEP THIS WINDOW OPEN
echo   Overlays:  http://127.0.0.1:5500/
echo ========================================
echo.
echo If this window closes, Browser layers in Meld go black.
echo.

echo Starting PowerShell overlay server...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1" -Mode meld
if errorlevel 1 (
  echo.
  echo PowerShell server failed. Trying Python...
  where py >nul 2>&1
  if not errorlevel 1 py -3 -m http.server 5500 --bind 127.0.0.1
  if errorlevel 1 (
    where python >nul 2>&1
    if not errorlevel 1 python -m http.server 5500 --bind 127.0.0.1
  )
)

echo.
echo Overlay server stopped. Overlays in Meld will go black until you run this again.
pause
