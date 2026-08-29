@echo off
title Rise Above OBS installer
cd /d "%~dp0"
echo.
echo EXTRACT the zip first if you have not. OBS Studio must already be open.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-obs.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-obs.ps1"
)
echo.
pause
