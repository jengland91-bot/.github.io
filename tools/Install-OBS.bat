@echo off
title Rise Above — install into OBS
cd /d "%~dp0"
echo.
echo EXTRACT the zip first if you have not. OBS Studio must already be open.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-obs.ps1"
echo.
pause
