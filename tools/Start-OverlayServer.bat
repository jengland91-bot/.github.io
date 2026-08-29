@echo off
title Rise Above overlay server (TikTok LIVE Studio)
cd /d "%~dp0"
echo.
echo Keep this window open while TikTok LIVE Studio is using the overlays.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1"
)
echo.
pause
