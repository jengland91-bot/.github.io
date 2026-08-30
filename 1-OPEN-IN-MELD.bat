@echo off
setlocal EnableExtensions
title Rise Above - Open in Meld
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   RISE ABOVE  -  LOAD INTO MELD
echo ========================================
echo.
echo This window MUST stay open.
echo It copies the scenes, starts overlays, opens Meld,
echo and tries to Import Session for you.
echo.

if not exist "%~dp0meld\Rise-Above-Meld.json" goto :wrongfolder
if not exist "%~dp0LOAD-THESE-SCENES\0 ALL SCENES.json" goto :wrongfolder

echo Loading into Meld Studio...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\load-into-meld.ps1"
if errorlevel 1 (
  echo PowerShell could not finish. Opening the scenes folder instead.
  start "" explorer.exe "%~dp0LOAD-THESE-SCENES"
  start "Rise Above overlays - KEEP OPEN" cmd /k "%~dp0tools\Start-MeldLayout.bat"
)

echo.
echo If Meld shows STARTING SOON / GRID / RACE / BRB, it worked.
echo Leave the overlay window open. Then add Game Capture + cameras.
echo.
echo If Meld is empty: File - Import Session - Ctrl+V - Open.
echo The path is on your clipboard, and also:
echo   Desktop\Rise Above scenes\0 ALL SCENES.json
echo.
pause
goto :eof

:wrongfolder
color 0C
echo.
echo ========================================
echo  WRONG FOLDER - NOTHING TO IMPORT
echo ========================================
echo.
echo You double-clicked the bat from INSIDE the zip,
echo or from a temp folder. That never works.
echo.
echo Close this. In Downloads:
echo   right-click Rise-Above-Meld.zip
echo   Extract All
echo Then open the FOLDER named Rise-Above-Meld
echo and double-click 1-OPEN-IN-MELD.bat
echo.
echo This copy is running from:
echo   %~dp0
echo.
pause
exit /b 1
