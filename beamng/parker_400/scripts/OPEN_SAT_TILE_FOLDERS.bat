@echo off
set LEVEL=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\mods\unpacked\parker_400\levels\parker_400
set DROP=%LEVEL%\import\sat_tiles
if not exist "%DROP%" mkdir "%DROP%"
explorer "%DROP%"
echo.
echo Drop Google Earth / MapNG JPGs + tiles.json here.
echo See docs\CLOSEUP_MULTI_TILE.md
pause
