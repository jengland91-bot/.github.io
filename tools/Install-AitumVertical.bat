@echo off
title Rise Above - fill Aitum Vertical Scenes
cd /d "%~dp0"
echo.
echo OBS must be open. Collection Rise Above BeamNG. Aitum Vertical plugin installed.
echo This fills the Vertical Scenes dock (phone 1080x1920). It does not replace the wide scenes.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-obs.ps1" -AitumOnly
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-obs.ps1" -AitumOnly
)
echo.
pause
