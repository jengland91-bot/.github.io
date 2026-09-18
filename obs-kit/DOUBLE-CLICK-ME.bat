@echo off
cd /d "%~dp0"
echo.
echo  J ENGLAND LIVE KIT
echo  Opening OBS, then loading scenes.
echo  Keep this window open.
echo.

tasklist /FI "IMAGENAME eq obs64.exe" | find /I "obs64.exe" >nul
if errorlevel 1 (
  if exist "%ProgramFiles%\obs-studio\bin\64bit\obs64.exe" (
    echo  Starting OBS...
    start "" /D "%ProgramFiles%\obs-studio\bin\64bit" obs64.exe
  ) else if exist "%ProgramFiles(x86)%\obs-studio\bin\64bit\obs64.exe" (
    echo  Starting OBS...
    start "" /D "%ProgramFiles(x86)%\obs-studio\bin\64bit" obs64.exe
  ) else (
    echo  OBS not found in Program Files — open OBS yourself, then come back to the browser.
  )
) else (
  echo  OBS is already running.
)

echo  Starting kit server...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\Start-Server.ps1"
pause
