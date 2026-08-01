@echo off
setlocal EnableExtensions
title Parker 400 - UNPACKED install (fixes black void)
color 0B
echo.
echo ============================================================
echo   PARKER 400 - UNPACKED INSTALL (BeamNG 0.39.1)
echo ============================================================
echo.
echo This extracts the map into mods\unpacked\ so BeamNG cannot
echo miss theTerrain.ter inside a zip. Use this if Freeroam is
echo a black void after installing the zip.
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "MODZIP="
if exist "%SCRIPT_DIR%\mods_drop_in\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\mods_drop_in\parker_400.zip"
if not defined MODZIP if exist "%SCRIPT_DIR%\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\parker_400.zip"

set "SRC="
if exist "%SCRIPT_DIR%\levels\parker_400\theTerrain.ter" set "SRC=%SCRIPT_DIR%\levels\parker_400"
if not defined SRC if exist "%SCRIPT_DIR%\parker_400\theTerrain.ter" set "SRC=%SCRIPT_DIR%\parker_400"

if not defined MODZIP if not defined SRC (
  echo ERROR: Need mods_drop_in\parker_400.zip OR levels\parker_400\theTerrain.ter
  echo next to this bat.
  pause
  exit /b 1
)

set "USER="
if exist "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods" set "USER=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current"
if not defined USER (
  echo Open launcher -^> Manage User Folder -^> Open, paste path:
  set /p "USER=Path: "
)
if not exist "%USER%\mods" (
  echo ERROR: no mods folder at %USER%
  pause
  exit /b 1
)

echo User: %USER%
echo.

echo Cleaning old Parker 400 installs...
if exist "%USER%\mods\parker_400.zip" del /f /q "%USER%\mods\parker_400.zip"
if exist "%USER%\levels\parker_400" rmdir /s /q "%USER%\levels\parker_400"
if exist "%USER%\mods\unpacked\parker_400" rmdir /s /q "%USER%\mods\unpacked\parker_400"

set "DEST=%USER%\mods\unpacked\parker_400"
mkdir "%DEST%" 2>nul

if defined MODZIP (
  echo Extracting:
  echo   %MODZIP%
  echo To:
  echo   %DEST%
  echo.
  powershell -NoProfile -Command "Expand-Archive -LiteralPath '%MODZIP%' -DestinationPath '%DEST%' -Force"
) else (
  echo Copying level folder...
  mkdir "%DEST%\levels\parker_400" 2>nul
  xcopy "%SRC%\*" "%DEST%\levels\parker_400\" /E /I /Y /Q >nul
)

if not exist "%DEST%\levels\parker_400\theTerrain.ter" (
  echo.
  echo ERROR: theTerrain.ter missing after install.
  echo Your download is incomplete or too old.
  echo Re-download parker_400.zip from the PR branch.
  pause
  exit /b 1
)

if not exist "%DEST%\levels\parker_400\info.json" (
  echo ERROR: info.json missing — bad package layout.
  pause
  exit /b 1
)

echo Clearing BeamNG temp terrain cache if present...
if exist "%USER%\temp\art\terrainMaterialCache" rmdir /s /q "%USER%\temp\art\terrainMaterialCache" 2>nul

echo.
echo ============================================================
echo   SUCCESS — unpacked mod installed
echo ============================================================
echo.
echo Path:
echo   %DEST%\levels\parker_400\theTerrain.ter
echo.
for %%A in ("%DEST%\levels\parker_400\theTerrain.ter") do echo Terrain size: %%~zA bytes  (should be about 50331692)
echo.
echo NEXT:
echo   1. Fully QUIT BeamNG (check tray)
echo   2. Start BeamNG
echo   3. Mods - enable Parker 400 / parker_400
echo   4. Freeroam - search parker
echo   5. You should see desert ground, not black
echo.
echo If STILL black: press ~ (console) and look for
echo   theTerrain / parker_400 / material errors
echo Then read BLACK_VOID_FIX.md
echo.
pause
endlocal
