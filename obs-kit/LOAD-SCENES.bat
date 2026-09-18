@echo off
cd /d "%~dp0"
echo.
echo  J ENGLAND LIVE — load horizontal + vertical scenes into OBS
echo.

tasklist /FI "IMAGENAME eq obs64.exe" | find /I "obs64.exe" >nul
if errorlevel 1 (
  if exist "%ProgramFiles%\obs-studio\bin\64bit\obs64.exe" (
    start "" /D "%ProgramFiles%\obs-studio\bin\64bit" obs64.exe
  ) else if exist "%ProgramFiles(x86)%\obs-studio\bin\64bit\obs64.exe" (
    start "" /D "%ProgramFiles(x86)%\obs-studio\bin\64bit" obs64.exe
  ) else (
    echo  Open OBS yourself first.
    pause
    exit /b 1
  )
  echo  Waiting for OBS to start...
  timeout /t 5 /nobreak >nul
)

echo  Tip: turn on Docks - Vertical before or during the load.
echo  Opening installer (auto-load)...
start "" "%~dp0overlays\install.html?load=1"
echo.
echo  1) Paste WebSocket password if asked
echo  2) Wait until the log says Done
echo  3) Optional: Tools - Scripts - add tools\je-link-vertical.lua
echo  4) After that use OPEN-OBS.bat only
echo.
pause
