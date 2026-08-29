@echo off
title Rise Above TikTok LIVE Studio layout
cd /d "%~dp0"
echo.
echo TikTok LIVE Studio layout server. Keep this window open while you are live.
echo Do not open OBS for TikTok.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1"
)
echo.
pause
