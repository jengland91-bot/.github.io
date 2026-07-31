@echo off
setlocal EnableExtensions
title Parker 400 - Install into BeamNG.drive

rem Try common layouts:
rem  1) ZIP root:  INSTALL_PARKER_400.bat + levels\parker_400\
rem  2) Repo:      scripts\INSTALL_PARKER_400.bat + ..\levels\parker_400\
rem  3) Nested:    Parker_400_Install\levels\parker_400\

set "SRC="
if exist "%~dp0levels\parker_400\info.json" set "SRC=%~dp0levels\parker_400"
if not defined SRC if exist "%~dp0..\levels\parker_400\info.json" set "SRC=%~dp0..\levels\parker_400"
if not defined SRC if exist "%~dp0parker_400\info.json" set "SRC=%~dp0parker_400"

if not defined SRC (
  echo.
  echo ERROR: Could not find the Parker 400 level folder.
  echo.
  echo Make sure you extracted the FULL ZIP first.
  echo You should see BOTH of these next to each other:
  echo   INSTALL_PARKER_400.bat
  echo   levels\parker_400\
  echo.
  echo Do NOT run only the .bat by itself.
  echo.
  echo This bat is at:
  echo   %~dp0
  echo.
  pause
  exit /b 1
)

set "DEST=%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400"
echo.
echo Source: %SRC%
echo Dest:   %DEST%
echo.

if not exist "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels" (
  mkdir "%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels" 2>nul
)

if exist "%DEST%" (
  echo Removing previous Parker 400 install...
  rmdir /s /q "%DEST%"
)

echo Copying Parker 400 level...
xcopy "%SRC%" "%DEST%\" /E /I /Y >nul
if errorlevel 1 (
  echo COPY FAILED.
  pause
  exit /b 1
)

echo.
echo Installed OK.
echo Next: BeamNG - Freeroam - Parker 400 - then follow DO_THIS_NOW.txt
echo.
if exist "%~dp0DO_THIS_NOW.txt" start "" "%~dp0DO_THIS_NOW.txt"
if exist "%SRC%\DO_THIS_NOW.txt" start "" "%SRC%\DO_THIS_NOW.txt"
pause
endlocal
