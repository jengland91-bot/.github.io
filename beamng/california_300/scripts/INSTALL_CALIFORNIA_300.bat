@echo off
setlocal EnableExtensions
title Install California 300 into BeamNG
echo ========================================
echo  INSTALL California 300 into BeamNG
echo ========================================
echo.
echo This is the only map name we use now:
echo   california_300
echo.
echo (Old name "Dust Valley" is retired.)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ONE_CLICK_FIX.ps1"
if errorlevel 1 pause
