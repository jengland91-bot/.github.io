@echo off
setlocal EnableExtensions
title Parker 400 - BeamNG 0.39 install
color 0A
echo.
echo ============================================================
echo   PARKER 400 - INSTALL FOR BEAMNG 0.39 / 0.39.1
echo ============================================================
echo.
echo After 0.39, Freeroam often IGNORES loose levels\ folders.
echo This installer puts a MOD ZIP into your mods\ folder instead.
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Prefer ready-made mod zip beside this bat
set "MODZIP="
if exist "%SCRIPT_DIR%\mods_drop_in\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\mods_drop_in\parker_400.zip"
if not defined MODZIP if exist "%SCRIPT_DIR%\parker_400.zip" set "MODZIP=%SCRIPT_DIR%\parker_400.zip"
if not defined MODZIP if exist "%SCRIPT_DIR%\parker_400_mod.zip" set "MODZIP=%SCRIPT_DIR%\parker_400_mod.zip"

REM Or build from extracted levels\parker_400 next to bat
set "SRC="
if exist "%SCRIPT_DIR%\levels\parker_400\info.json" set "SRC=%SCRIPT_DIR%\levels\parker_400"
if not defined SRC if exist "%SCRIPT_DIR%\parker_400\info.json" set "SRC=%SCRIPT_DIR%\parker_400"

if not defined MODZIP if not defined SRC (
  echo ERROR: Cannot find mod zip or level folder next to this bat.
  echo.
  echo Put this bat next to either:
  echo   mods_drop_in\parker_400.zip
  echo   OR levels\parker_400\info.json
  echo.
  echo Download:
  echo   https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip
  echo.
  pause
  exit /b 1
)

echo Looking for BeamNG user folder...
set "USER="

if defined BEAMNG_USER_FOLDER if exist "%BEAMNG_USER_FOLDER%\mods" set "USER=%BEAMNG_USER_FOLDER%"

if not defined USER if exist "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods" (
  set "USER=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current"
)

if not defined USER if exist "%USERPROFILE%\AppData\Local\BeamNG\BeamNG.drive\current\mods" (
  set "USER=%USERPROFILE%\AppData\Local\BeamNG\BeamNG.drive\current"
)

if not defined USER if exist "%USERPROFILE%\Documents\BeamNG.drive\mods" (
  set "USER=%USERPROFILE%\Documents\BeamNG.drive"
)

if not defined USER (
  echo.
  echo Could not auto-find BeamNG.
  echo.
  echo 1^) Open BeamNG launcher
  echo 2^) Manage User Folder -^> Open
  echo 3^) Copy the full path from the address bar here
  echo.
  set /p "USER=Paste path: "
)

if not exist "%USER%\mods" (
  echo.
  echo ERROR: That folder has no "mods" subfolder.
  echo You need the folder that CONTAINS mods, for example:
  echo   C:\Users\YOU\AppData\Local\BeamNG\BeamNG.drive\current
  echo.
  pause
  exit /b 1
)

echo.
echo User folder: %USER%
echo.

REM Remove old broken loose install that 0.39 may ignore
if exist "%USER%\levels\parker_400" (
  echo Removing old loose levels\parker_400 so Freeroam uses the mod instead...
  rmdir /s /q "%USER%\levels\parker_400" 2>nul
)

set "DESTZIP=%USER%\mods\parker_400.zip"
echo Installing mod zip to:
echo   %DESTZIP%
echo.

if defined MODZIP (
  copy /Y "%MODZIP%" "%DESTZIP%" >nul
) else (
  echo Building zip from %SRC% ...
  where powershell >nul 2>&1
  if errorlevel 1 (
    echo ERROR: Need PowerShell to build zip, or download parker_400.zip first.
    pause
    exit /b 1
  )
  set "STAGING=%TEMP%\parker_400_mod_build"
  if exist "%STAGING%" rmdir /s /q "%STAGING%"
  mkdir "%STAGING%\levels\parker_400"
  xcopy "%SRC%\*" "%STAGING%\levels\parker_400\" /E /I /Y /Q >nul
  if exist "%DESTZIP%" del /f /q "%DESTZIP%"
  powershell -NoProfile -Command "Compress-Archive -Path '%STAGING%\levels' -DestinationPath '%DESTZIP%' -Force"
  rmdir /s /q "%STAGING%" 2>nul
)

if not exist "%DESTZIP%" (
  echo ERROR: Install failed — zip not created.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo   SUCCESS
echo ============================================================
echo.
echo Mod installed:
echo   %DESTZIP%
echo.
echo NEXT:
echo   1. Fully QUIT BeamNG
echo   2. Start BeamNG again
echo   3. Mods - make sure Parker 400 is ENABLED
echo   4. Play -^> Freeroam -^> search "parker"
echo.
echo If it still does not show, read INSTALL_FOR_039.md
echo.
pause
endlocal
