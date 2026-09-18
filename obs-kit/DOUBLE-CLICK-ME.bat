@echo off
cd /d "%~dp0"
echo.
echo  J ENGLAND LIVE
echo  Opening OBS only. No kit server.
echo.

tasklist /FI "IMAGENAME eq obs64.exe" | find /I "obs64.exe" >nul
if errorlevel 1 (
  if exist "%ProgramFiles%\obs-studio\bin\64bit\obs64.exe" (
    start "" /D "%ProgramFiles%\obs-studio\bin\64bit" obs64.exe
  ) else if exist "%ProgramFiles(x86)%\obs-studio\bin\64bit\obs64.exe" (
    start "" /D "%ProgramFiles(x86)%\obs-studio\bin\64bit" obs64.exe
  ) else (
    echo  Open OBS yourself - it was not found in Program Files.
    pause
    exit /b 1
  )
) else (
  echo  OBS is already running.
)

echo  Opening the one-time online-overlay fix page...
start "" "%~dp0overlays\go-online.html"
echo.
echo  1) Paste WebSocket password
echo  2) Connect OBS
echo  3) Click "Switch overlays to online"
echo  4) Close that page - you will not need it every stream
echo.
pause
