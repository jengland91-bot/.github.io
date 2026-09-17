@echo off
cd /d "%~dp0"
echo.
echo  J ENGLAND LIVE KIT
echo  Keep this window open while you stream.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Start-Server.ps1"
pause
