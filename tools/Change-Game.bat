@echo off
title Change the game on Starting Soon
cd /d "%~dp0"
echo.
echo This updates STARTING SOON. You do not re-run Install-OBS.bat.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0change-game.ps1" %*
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0change-game.ps1" %*
)
echo.
pause
