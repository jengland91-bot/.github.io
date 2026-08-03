@echo off
setlocal
title Parker 400 — open MapNG drop folders

set "LEVEL=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400"
if not exist "%LEVEL%\info.json" (
  echo Parker 400 is not installed yet.
  echo Run INSTALL_PARKER_400.bat first.
  pause
  exit /b 1
)

if not exist "%LEVEL%\import" mkdir "%LEVEL%\import"
if not exist "%LEVEL%\art\terrains" mkdir "%LEVEL%\art\terrains"

echo.
echo Put MapNG files here:
echo   HEIGHTMAP  -^>  %LEVEL%\import\mapng_heightmap.png
echo   SATELLITE  -^>  %LEVEL%\art\terrains\parker400_base_color.png
echo.
echo Opening both folders...
explorer "%LEVEL%\import"
explorer "%LEVEL%\art\terrains"
echo.
echo Done. After copying, tell Cursor you dropped the MapNG files.
pause
endlocal
