@echo off
cd /d "%~dp0"
echo.
echo  J ENGLAND LIVE - load horizontal + vertical scenes into OBS
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
  timeout /t 6 /nobreak >nul
)

echo  Tip: OBS - Docks - turn on Vertical before or during the load.
echo  Opening installer...
if exist "%~dp0overlays\load-now.html" (
  start "" "%~dp0overlays\load-now.html"
) else (
  start "" "%~dp0overlays\install.html"
)
echo.
echo  IN THE BROWSER PAGE:
echo  1) Paste WebSocket password  (OBS - Tools - WebSocket Server Settings)
echo  2) Click Connect OBS if it did not auto-connect
echo  3) Click "Load horizontal + vertical into OBS" if it did not auto-start
echo  4) Wait until the log says Done
echo.
echo  If you see a red auth error: wrong password - copy it again from OBS.
echo  If Vertical canvas not found: Docks - Vertical, then click Load again.
echo.
pause
