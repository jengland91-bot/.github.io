@echo off
setlocal EnableExtensions
title Parker 400 — Install into BeamNG.drive

set "SRC=%~dp0..\levels\parker_400"
if not exist "%SRC%\info.json" (
  echo ERROR: Could not find levels\parker_400 next to scripts.
  echo Expected: %SRC%
  pause
  exit /b 1
)

set "DEST=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400"
echo.
echo Source: %SRC%
echo Dest:   %DEST%
echo.

if not exist "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels" (
  mkdir "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels" 2>nul
)

if exist "%DEST%" (
  echo Removing previous Parker 400 install...
  rmdir /s /q "%DEST%"
)

echo Copying Parker 400 level...
xcopy "%SRC%" "%DEST%\" /E /I /Y >nul
if errorlevel 1 (
  echo COPY FAILED.
  pause
  exit /b 1
)

echo.
echo Installed.
echo Next: open BeamNG → Freeroam → Parker 400 → follow DO_THIS_NOW.txt
echo.
start "" "%~dp0..\DO_THIS_NOW.txt"
pause
endlocal
