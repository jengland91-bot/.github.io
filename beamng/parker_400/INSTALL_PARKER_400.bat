@echo off
setlocal EnableExtensions
title Parker 400 - Install into BeamNG.drive 0.39+

rem BeamNG 0.39/0.39.1: Freeroam often ignores loose levels\ copies.
rem This bat installs a proper mod zip into mods\parker_400.zip

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "MODZIP="
if exist "%SCRIPT_DIR%\mods_drop_in\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\mods_drop_in\parker_400.zip"
if not defined MODZIP if exist "%SCRIPT_DIR%\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\parker_400.zip"
if not defined MODZIP if exist "%SCRIPT_DIR%\parker_400_mod.zip" set "MODZIP=%SCRIPT_DIR%\parker_400_mod.zip"

set "SRC="
if exist "%SCRIPT_DIR%\levels\parker_400\info.json" set "SRC=%SCRIPT_DIR%\levels\parker_400"
if not defined SRC if exist "%SCRIPT_DIR%\..\levels\parker_400\info.json" set "SRC=%SCRIPT_DIR%\..\levels\parker_400"
if not defined SRC if exist "%SCRIPT_DIR%\parker_400\info.json" set "SRC=%SCRIPT_DIR%\parker_400"

if not defined MODZIP if not defined SRC (
  echo.
  echo ERROR: Could not find mod zip or levels\parker_400 next to this bat.
  echo.
  echo Extract the FULL ZIP first. You should see:
  echo   INSTALL_PARKER_400.bat
  echo   levels\parker_400\
  echo   OR mods_drop_in\parker_400.zip
  echo.
  echo Direct mod download (0.39.1 Freeroam fix):
  echo   https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip
  echo.
  pause
  exit /b 1
)

set "USER="
if defined BEAMNG_USER_FOLDER if exist "%BEAMNG_USER_FOLDER%\mods" set "USER=%BEAMNG_USER_FOLDER%"
if not defined USER if exist "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods" set "USER=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current"
if not defined USER if exist "%USERPROFILE%\Documents\BeamNG.drive\mods" set "USER=%USERPROFILE%\Documents\BeamNG.drive"

if not defined USER (
  echo.
  echo Could not auto-find BeamNG user folder.
  echo Launcher -^> Manage User Folder -^> Open, then paste that path:
  echo.
  set /p "USER=Paste path: "
)

if not exist "%USER%\mods" (
  echo.
  echo ERROR: No "mods" folder at:
  echo   %USER%
  echo.
  echo Open BeamNG launcher -^> Manage User Folder -^> Open
  echo That folder should contain mods\
  echo.
  pause
  exit /b 1
)

echo.
echo Installing Parker 400 as a MOD (required for BeamNG 0.39.1 Freeroam)...
echo User: %USER%
echo.

if exist "%USER%\levels\parker_400" (
  echo Removing old loose levels\parker_400 (ignored by 0.39 Freeroam)...
  rmdir /s /q "%USER%\levels\parker_400" 2>nul
)

set "DESTZIP=%USER%\mods\parker_400.zip"
if defined MODZIP (
  echo Copying:
  echo   %MODZIP%
  echo To:
  echo   %DESTZIP%
  copy /Y "%MODZIP%" "%DESTZIP%" >nul
) else (
  echo Building mod zip from:
  echo   %SRC%
  set "STAGING=%TEMP%\parker_400_mod_build"
  if exist "%STAGING%" rmdir /s /q "%STAGING%"
  mkdir "%STAGING%\levels\parker_400"
  xcopy "%SRC%\*" "%STAGING%\levels\parker_400\" /E /I /Y /Q >nul
  if exist "%DESTZIP%" del /f /q "%DESTZIP%"
  powershell -NoProfile -Command "Compress-Archive -Path '%STAGING%\levels' -DestinationPath '%DESTZIP%' -Force"
  rmdir /s /q "%STAGING%" 2>nul
)

if not exist "%DESTZIP%" (
  echo INSTALL FAILED — zip missing.
  pause
  exit /b 1
)

echo.
echo Installed OK:
echo   %DESTZIP%
echo.
echo NEXT:
echo   1. Fully quit BeamNG
echo   2. Start again
echo   3. Mods - enable Parker 400 if needed
echo   4. Freeroam - search "parker"
echo.
echo Read INSTALL_FOR_039.md if it still does not appear.
echo.
if exist "%SCRIPT_DIR%\INSTALL_FOR_039.md" start "" "%SCRIPT_DIR%\INSTALL_FOR_039.md"
if exist "%SCRIPT_DIR%\DO_THIS_NOW.txt" start "" "%SCRIPT_DIR%\DO_THIS_NOW.txt"
if exist "%SRC%\DO_THIS_NOW.txt" start "" "%SRC%\DO_THIS_NOW.txt"
pause
endlocal
