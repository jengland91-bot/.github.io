@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Parker 400 - UNPACKED install
color 0B

rem Keep a log even if the window closes
set "LOG=%~dp0INSTALL_LOG.txt"
echo Parker 400 install started %DATE% %TIME% > "%LOG%"
echo Script folder: %CD% >> "%LOG%"

echo.
echo ============================================================
echo   PARKER 400 - UNPACKED INSTALL (BeamNG 0.39.1)
echo ============================================================
echo.
echo If this window closes by itself, open INSTALL_LOG.txt
echo in this same folder to see what happened.
echo.

set "SCRIPT_DIR=%CD%"

set "MODZIP="
if exist "%SCRIPT_DIR%\mods_drop_in\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\mods_drop_in\parker_400.zip"
if not defined MODZIP if exist "%SCRIPT_DIR%\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\parker_400.zip"

set "SRC="
if exist "%SCRIPT_DIR%\levels\parker_400\theTerrain.ter" set "SRC=%SCRIPT_DIR%\levels\parker_400"
if not defined SRC if exist "%SCRIPT_DIR%\parker_400\theTerrain.ter" set "SRC=%SCRIPT_DIR%\parker_400"

echo Looking for files in: %SCRIPT_DIR%
dir /b "%SCRIPT_DIR%"
echo.

if not defined MODZIP if not defined SRC (
  echo ERROR: Cannot find parker_400.zip next to this bat.
  echo.
  echo You must EXTRACT Parker400_Download_Both.zip first.
  echo Then you should see BOTH in the same folder:
  echo   INSTALL_UNPACKED.bat
  echo   parker_400.zip
  echo.
  echo Do NOT run the bat from inside the zip window.
  echo.
  echo MANUAL INSTALL: see MANUAL_INSTALL.txt
  echo ERROR: missing parker_400.zip >> "%LOG%"
  goto :END
)

echo Found:
if defined MODZIP echo   MODZIP=%MODZIP%
if defined SRC echo   SRC=%SRC%
echo. >> "%LOG%"
echo MODZIP=%MODZIP% >> "%LOG%"
echo SRC=%SRC% >> "%LOG%"

set "USER="
if exist "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods" set "USER=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current"

if not defined USER (
  echo Could not auto-find BeamNG user folder.
  echo.
  echo 1. Open BeamNG launcher
  echo 2. Manage User Folder -^> Open
  echo 3. Copy the path from the address bar and paste here
  echo.
  set /p "USER=Paste path: "
)

if not exist "%USER%\mods" (
  echo ERROR: that folder has no mods\ subfolder:
  echo   %USER%
  echo.
  echo MANUAL INSTALL: see MANUAL_INSTALL.txt
  echo ERROR: bad user folder %USER% >> "%LOG%"
  goto :END
)

echo User folder: %USER%
echo User=%USER% >> "%LOG%"
echo.

echo Cleaning old Parker 400 installs...
if exist "%USER%\mods\parker_400.zip" del /f /q "%USER%\mods\parker_400.zip"
if exist "%USER%\levels\parker_400" rmdir /s /q "%USER%\levels\parker_400"
if exist "%USER%\mods\unpacked\parker_400" rmdir /s /q "%USER%\mods\unpacked\parker_400"

set "DEST=%USER%\mods\unpacked\parker_400"
mkdir "%USER%\mods\unpacked" 2>nul
mkdir "%DEST%" 2>nul

if defined MODZIP (
  echo Extracting mod zip... this can take 1-2 minutes. Wait.
  echo   From: %MODZIP%
  echo   To:   %DEST%
  echo.
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Expand-Archive -LiteralPath '%MODZIP%' -DestinationPath '%DEST%' -Force; Write-Output 'EXTRACT_OK' } catch { Write-Output $_.Exception.Message; exit 1 }"
  if errorlevel 1 (
    echo PowerShell extract failed. Trying tar...
    tar -xf "%MODZIP%" -C "%DEST%"
  )
) else (
  echo Copying level folder...
  mkdir "%DEST%\levels\parker_400" 2>nul
  xcopy "%SRC%\*" "%DEST%\levels\parker_400\" /E /I /Y
)

if not exist "%DEST%\levels\parker_400\theTerrain.ter" (
  echo.
  echo ERROR: theTerrain.ter missing after install.
  echo Download may be incomplete, or extract failed.
  echo MANUAL INSTALL: see MANUAL_INSTALL.txt
  echo ERROR: missing theTerrain.ter >> "%LOG%"
  goto :END
)

if exist "%USER%\temp\art\terrainMaterialCache" (
  echo Clearing terrain material cache...
  rmdir /s /q "%USER%\temp\art\terrainMaterialCache" 2>nul
)

echo.
echo ============================================================
echo   SUCCESS
echo ============================================================
echo.
echo Installed to:
echo   %DEST%\levels\parker_400\
for %%A in ("%DEST%\levels\parker_400\theTerrain.ter") do echo Terrain bytes: %%~zA  ^(want ~50331692^)
echo.
echo NEXT:
echo   1. Fully quit BeamNG
echo   2. Start BeamNG
echo   3. Mods - enable Parker 400
echo   4. Freeroam - search parker
echo.
echo SUCCESS >> "%LOG%"
echo DEST=%DEST% >> "%LOG%"

:END
echo.
echo Log saved: %LOG%
echo.
echo Press any key to close...
pause >nul
endlocal
