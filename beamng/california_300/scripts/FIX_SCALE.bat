@echo off
setlocal EnableExtensions
echo Running California 300 scale fixer...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0FIX_SCALE.ps1"
if errorlevel 1 pause
