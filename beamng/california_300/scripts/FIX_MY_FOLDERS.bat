@echo off
setlocal EnableExtensions
echo ========================================
echo  California 300 BeamNG folder fixer
echo ========================================
echo.

set "BEAM=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current"
set "LEVELS=%BEAM%\levels"
set "TARGET=%LEVELS%\california_300"

echo Windows user: %USERNAME%
echo BeamNG folder: %BEAM%
echo.

if not exist "%BEAM%" (
  echo ERROR: BeamNG folder not found:
  echo   %BEAM%
  echo.
  echo Open BeamNG once, close it, then run this again.
  pause
  exit /b 1
)

mkdir "%LEVELS%" 2>nul
echo OK: levels folder ready:
echo   %LEVELS%
echo.

set "SOURCE="
if exist "%USERPROFILE%\Desktop\california_300\info.json" set "SOURCE=%USERPROFILE%\Desktop\california_300"
if exist "%USERPROFILE%\OneDrive\Desktop\california_300\info.json" set "SOURCE=%USERPROFILE%\OneDrive\Desktop\california_300"
if exist "%USERPROFILE%\Downloads\california_300\info.json" set "SOURCE=%USERPROFILE%\Downloads\california_300"
if exist "%USERPROFILE%\Desktop\california_300\california_300\info.json" set "SOURCE=%USERPROFILE%\Desktop\california_300\california_300"
if exist "%USERPROFILE%\OneDrive\Desktop\california_300\california_300\info.json" set "SOURCE=%USERPROFILE%\OneDrive\Desktop\california_300\california_300"

REM Also support running the bat FROM inside the california_300 folder
if exist "%~dp0info.json" set "SOURCE=%~dp0"

if "%SOURCE%"=="" (
  echo Could not find california_300 with info.json automatically.
  echo I still created the levels folder.
  echo.
  echo Copy your california_300 folder into:
  echo   %LEVELS%
  explorer "%LEVELS%"
  pause
  exit /b 0
)

echo Found map source:
echo   %SOURCE%
echo.

mkdir "%TARGET%" 2>nul
echo Copying files into BeamNG levels...
xcopy "%SOURCE%*" "%TARGET%\" /E /I /Y /Q >nul

echo.
echo DONE.
echo Final map path:
echo   %TARGET%
if exist "%TARGET%\info.json" (
  echo info.json: FOUND
) else (
  echo info.json: MISSING
)

echo.
echo Next in BeamNG:
echo 1^) Press F11
echo 2^) File -^> Open Level -^> california_300
echo 3^) Import heightmap_4096.png
echo    squareSize = 4
echo    maxHeight = 900
echo.

explorer "%LEVELS%"
pause
