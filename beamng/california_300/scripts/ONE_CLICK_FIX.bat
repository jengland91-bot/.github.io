@echo off
setlocal EnableExtensions
echo ========================================
echo  California 300 - ONE CLICK GPX SCALE FIX
echo ========================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ONE_CLICK_FIX.ps1"
if errorlevel 1 pause
