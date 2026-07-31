@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Parker 400 - FIND AND FIX INSTALL

echo.
echo ============================================
echo  Parker 400 - Find BeamNG folder + install
echo ============================================
echo.

rem --- Find source level (where you extracted the ZIP) ---
set "SRC="
if exist "%~dp0levels\parker_400\info.json" set "SRC=%~dp0levels\parker_400"
if not defined SRC if exist "%~dp0parker_400\info.json" set "SRC=%~dp0parker_400"
if not defined SRC if exist "D:\Parker_400_Install\levels\parker_400\info.json" set "SRC=D:\Parker_400_Install\levels\parker_400"
if not defined SRC if exist "%USERPROFILE%\Downloads\Parker_400_Install\levels\parker_400\info.json" set "SRC=%USERPROFILE%\Downloads\Parker_400_Install\levels\parker_400"
if not defined SRC if exist "%USERPROFILE%\Downloads\levels\parker_400\info.json" set "SRC=%USERPROFILE%\Downloads\levels\parker_400"

if not defined SRC (
  echo Could not find the extracted map files.
  echo.
  echo Put this FIX bat INSIDE your extracted Parker_400_Install folder
  echo ^(same place as the levels folder^), then run it again.
  echo.
  echo This bat is currently at:
  echo   %~f0
  echo.
  pause
  exit /b 1
)

echo Found map source:
echo   %SRC%
echo.

rem --- Candidate BeamNG levels folders ---
set "D1=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels"
set "D2=%USERPROFILE%\Documents\BeamNG.drive\levels"
set "D3=%USERPROFILE%\Documents\BeamNG.Drive\levels"
set "D4=%LOCALAPPDATA%\BeamNG.drive\levels"

echo Checking BeamNG levels folders...
echo.

set "DEST="
if exist "%D1%" (
  echo [OK] Found: %D1%
  set "DEST=%D1%\parker_400"
) else (
  echo [ ] Missing: %D1%
)
if exist "%D2%" (
  echo [OK] Found: %D2%
  if not defined DEST set "DEST=%D2%\parker_400"
) else (
  echo [ ] Missing: %D2%
)
if exist "%D3%" (
  echo [OK] Found: %D3%
  if not defined DEST set "DEST=%D3%\parker_400"
) else (
  echo [ ] Missing: %D3%
)
if exist "%D4%" (
  echo [OK] Found: %D4%
  if not defined DEST set "DEST=%D4%\parker_400"
) else (
  echo [ ] Missing: %D4%
)

echo.

if not defined DEST (
  echo No BeamNG levels folder found yet.
  echo Creating the modern one:
  echo   %D1%
  mkdir "%D1%" 2>nul
  set "DEST=%D1%\parker_400"
)

echo Will install to:
echo   %DEST%
echo.
echo Close BeamNG if it is open.
pause

if exist "%DEST%" (
  echo Removing old Parker 400 copy...
  rmdir /s /q "%DEST%"
)

echo Copying files...
mkdir "%DEST%" 2>nul
xcopy "%SRC%" "%DEST%\" /E /I /Y
if errorlevel 1 (
  echo.
  echo COPY FAILED. Try running this bat as Administrator.
  pause
  exit /b 1
)

echo.
echo ============================================
echo  SUCCESS
echo ============================================
echo Parker 400 is installed at:
echo   %DEST%
echo.
echo Next:
echo  1. Open BeamNG.drive
echo  2. Freeroam -^> Parker 400
echo  3. Press F11 -^> Import terrain preset
echo     import\p400_gpx_scale.preset.json
echo     Meters per Pixel = 16
echo     Max Height = 1500
echo  4. Ctrl+S, paint desert_base, drive
echo.
echo Opening the install folder now...
explorer "%DEST%\.."
echo.
pause
endlocal
