@echo off
title Open Rise Above in Meld Studio
cd /d "%~dp0"
echo.
echo This puts the Meld file on your DESKTOP and opens Meld.
echo You do not hunt in a meld folder.
echo.
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\open-in-meld.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\open-in-meld.ps1"
)
echo.
pause
