@echo off
setlocal EnableExtensions
title Rise Above - Open in Meld
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   RISE ABOVE  -  MELD SESSION FILE
echo ========================================
echo.
echo This copies Rise-Above.json to your Desktop
echo and opens Meld. It does NOT close Meld or
echo rewrite Meld's files (that crashed Meld).
echo.

if not exist "%~dp0meld\Rise-Above-Meld.json" goto :wrongfolder
if not exist "%~dp0LOAD-THESE-SCENES\0 ALL SCENES.json" goto :wrongfolder

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\load-into-meld.ps1"
if errorlevel 1 (
  echo PowerShell could not finish. Opening the scenes folder instead.
  start "" explorer.exe "%~dp0LOAD-THESE-SCENES"
)

echo.
echo IN MELD:  File  -  Import Session  -  Desktop\Rise-Above.json
echo (Ctrl+V pastes the path.)
echo Then you should see STARTING SOON / GRID / RACE / BRB.
echo.
echo If Meld crashed before: File - Restore from Backup, then Import Session.
echo.
pause
goto :eof

:wrongfolder
color 0C
echo.
echo ========================================
echo  WRONG FOLDER
echo ========================================
echo.
echo Extract the GitHub zip first. Look for FIND-ME.txt.
echo Or skip the zip: download only the JSON. See GET-THE-KIT.txt
echo.
echo This copy is running from:
echo   %~dp0
echo.
pause
exit /b 1
