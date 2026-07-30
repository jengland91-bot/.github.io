@echo off
set "LEVELS=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels"
if not exist "%LEVELS%" mkdir "%LEVELS%" 2>nul
explorer "%LEVELS%"
