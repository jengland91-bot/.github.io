@echo off
setlocal EnableExtensions
echo ========================================
echo  Open BeamNG levels folder
echo ========================================
echo.

set "BEAM=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current"
set "LEVELS=%BEAM%\levels"

echo Windows user: %USERNAME%
echo BeamNG folder: %BEAM%
echo Levels folder: %LEVELS%
echo.

if not exist "%BEAM%" (
  echo ERROR: BeamNG folder not found.
  echo Open BeamNG once, close it, then run this again.
  pause
  exit /b 1
)

REM levels can look "gone" if it was never created, or you browsed up/out of current
mkdir "%LEVELS%" 2>nul

echo Creating a Desktop shortcut so you can find this again...
set "SHORTCUT=%USERPROFILE%\Desktop\BeamNG Levels.lnk"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%LEVELS%'; $s.WindowStyle = 1; $s.Description = 'BeamNG.drive levels folder'; $s.Save()"

if exist "%USERPROFILE%\OneDrive\Desktop\" (
  set "SHORTCUT2=%USERPROFILE%\OneDrive\Desktop\BeamNG Levels.lnk"
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT2%'); $s.TargetPath = '%LEVELS%'; $s.WindowStyle = 1; $s.Description = 'BeamNG.drive levels folder'; $s.Save()"
)

echo.
echo Opening levels folder now...
explorer "%LEVELS%"
echo.
echo Tip: use the Desktop shortcut "BeamNG Levels" next time.
echo Your map should be here:
echo   %LEVELS%\california_300
echo.
pause
