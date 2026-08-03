@echo off
cd /d "%~dp0"
title Parker 400 installer - window stays open
echo.
echo ============================================================
echo   PARKER 400 INSTALLER
echo ============================================================
echo.
echo This window STAYS OPEN so you can read any errors.
echo.
echo Prefer PowerShell installer if the .bat closes by itself...
echo.

if exist "%~dp0INSTALL_UNPACKED.ps1" (
  echo Running INSTALL_UNPACKED.ps1 ...
  echo.
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_UNPACKED.ps1"
) else (
  echo Running INSTALL_UNPACKED.bat ...
  echo.
  call "%~dp0INSTALL_UNPACKED.bat"
)

echo.
echo ----- finished -----
echo If it failed, open MANUAL_INSTALL.txt in this folder.
echo Also check INSTALL_LOG.txt
echo.
pause
