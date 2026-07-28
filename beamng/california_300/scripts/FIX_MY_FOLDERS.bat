@echo off
echo Running California 300 folder fixer...
powershell -ExecutionPolicy Bypass -File "%~dp0fix_all_beamng_folders.ps1"
pause
