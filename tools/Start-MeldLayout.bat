@echo off
title Rise Above Meld Studio layout
cd /d "%~dp0"
echo.
echo Meld Studio layout server. Keep this window open if Browser layers use http://127.0.0.1:5500
echo Fastest path is still File - Import OBS Session. This server is optional.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1" -Mode meld
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-overlay-server.ps1" -Mode meld
)
echo.
pause
