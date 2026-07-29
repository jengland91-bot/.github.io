@echo off
setlocal EnableExtensions
title Install California 300 into BeamNG
echo ========================================
echo  INSTALL California 300 into BeamNG
echo ========================================
echo.
echo Map name: california_300
echo Old name Dust Valley is retired.
echo.
cd /d "%~dp0"
if not exist "%~dp0ONE_CLICK_FIX.ps1" (
  echo ERROR: ONE_CLICK_FIX.ps1 must be in the same folder as this .bat
  echo Extract the whole ZIP first, then run this file.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ONE_CLICK_FIX.ps1"
if errorlevel 1 pause
