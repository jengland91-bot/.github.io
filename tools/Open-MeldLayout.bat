@echo off
title Rise Above Meld Studio layout
cd /d "%~dp0"
echo.
echo Meld only. Do not open OBS.
echo Keep this window open so overlay URLs keep working in Meld.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1" -Mode meld
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1" -Mode meld
)
echo.
pause
