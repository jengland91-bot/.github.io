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
echo It writes the 8 scenes into Meld, starts overlays,
echo and opens Meld with STARTING SOON already loaded.
echo.

if not exist "%~dp0meld\Rise-Above-Meld.json" goto :wrongfolder
if not exist "%~dp0LOAD-THESE-SCENES\0 ALL SCENES.json" goto :wrongfolder

echo Closing Meld if it is open, then installing scenes...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\load-into-meld.ps1"
if errorlevel 1 (
  echo PowerShell could not finish. Opening the scenes folder instead.
  start "" explorer.exe "%~dp0LOAD-THESE-SCENES"
  start "Rise Above overlays - KEEP OPEN" cmd /k "%~dp0tools\Start-MeldLayout.bat"
)

echo.
echo You should see STARTING SOON / GRID / RACE / BRB in Meld.
echo Leave the overlay window open. Then add Game Capture + cameras.
echo.
echo If Meld is still empty, use the Desktop shortcut
echo   Rise Above Meld
echo or File - Import Session - Ctrl+V - Open.
echo A log is on your Desktop: Rise-Above-Meld-load-log.txt
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
