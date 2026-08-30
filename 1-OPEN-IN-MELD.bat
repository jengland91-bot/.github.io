@echo off
setlocal EnableExtensions
title Rise Above - Open in Meld
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   RISE ABOVE  -  OPEN IN MELD
echo ========================================
echo.
echo This window MUST stay open. If it closes by itself,
echo Windows blocked the file. Use 00-DOUBLE-CLICK-ME.html
echo instead, then File - Import Session in Meld.
echo.

if not exist "%~dp0meld\Rise-Above-Meld.json" goto :wrongfolder
if not exist "%~dp0IMPORT-THIS-IN-MELD.json" copy /Y "%~dp0meld\Rise-Above-Meld.json" "%~dp0IMPORT-THIS-IN-MELD.json" >nul

echo Copying the Meld file and scene folder to your Desktop...
copy /Y "%~dp0meld\Rise-Above-Meld.json" "%USERPROFILE%\Desktop\Rise-Above-Meld.json" >nul 2>&1
copy /Y "%~dp0meld\Rise-Above-Meld.json" "%USERPROFILE%\OneDrive\Desktop\Rise-Above-Meld.json" >nul 2>&1
if exist "%~dp0LOAD-THESE-SCENES\0 ALL SCENES.json" (
  xcopy /E /I /Y "%~dp0LOAD-THESE-SCENES" "%USERPROFILE%\Desktop\Rise Above scenes\" >nul
  xcopy /E /I /Y "%~dp0LOAD-THESE-SCENES" "%USERPROFILE%\OneDrive\Desktop\Rise Above scenes\" >nul
)

set "NOTE=%USERPROFILE%\Desktop\READ-THIS-THEN-OPEN-MELD.txt"
if not exist "%USERPROFILE%\Desktop\." set "NOTE=%~dp0READ-THIS-THEN-OPEN-MELD.txt"

(
echo RISE ABOVE - next 3 clicks in Meld Studio
echo ========================================
echo.
echo 1. Open Meld Studio  ^(not OBS^)
echo 2. File - Import Session
echo 3. Open the Desktop folder  Rise Above scenes
echo 4. Pick  0 ALL SCENES.json  for every scene
echo    or  4 RACE.json  to try just the race look
echo.
echo    Those files are also in:
echo    %~dp0LOAD-THESE-SCENES
echo.
echo Leave the black KEEP THIS WINDOW OPEN overlay window running.
echo Then in Meld add Game Capture + your cameras.
echo.
echo You do not paste any code into Meld.
) > "%NOTE%"

echo Opening Notepad with the next clicks...
start "" notepad.exe "%NOTE%"

echo Opening the scenes folder...
if exist "%USERPROFILE%\Desktop\Rise Above scenes\0 ALL SCENES.json" (
  start "" explorer.exe "%USERPROFILE%\Desktop\Rise Above scenes"
) else (
  start "" explorer.exe "%~dp0LOAD-THESE-SCENES"
)

echo Starting overlay server - leave that window open...
start "Rise Above overlays - KEEP OPEN" cmd /k "%~dp0tools\Start-MeldLayout.bat"

echo Trying to open Meld Studio...
if exist "%LOCALAPPDATA%\Programs\Meld Studio\Meld Studio.exe" (
  start "" "%LOCALAPPDATA%\Programs\Meld Studio\Meld Studio.exe"
  goto :done
)
if exist "%LOCALAPPDATA%\Meld Studio\Meld Studio.exe" (
  start "" "%LOCALAPPDATA%\Meld Studio\Meld Studio.exe"
  goto :done
)
if exist "%ProgramFiles%\Meld Studio\Meld Studio.exe" (
  start "" "%ProgramFiles%\Meld Studio\Meld Studio.exe"
  goto :done
)
if exist "%ProgramFiles(x86)%\Meld Studio\Meld Studio.exe" (
  start "" "%ProgramFiles(x86)%\Meld Studio\Meld Studio.exe"
  goto :done
)
echo   Could not find Meld Studio.exe - open Meld yourself.

:done
echo.
echo ========================================
echo  DONE. Look for:
echo    - this window
echo    - Notepad
echo    - File Explorer
echo    - a second black window titled KEEP OPEN
echo    - Meld Studio
echo ========================================
echo.
echo In Meld: File - Import Session - Rise Above scenes\0 ALL SCENES.json
echo.
pause
goto :eof

:wrongfolder
color 0C
echo.
echo ========================================
echo  WRONG FOLDER - NOTHING TO IMPORT
echo ========================================
echo.
echo You double-clicked the bat from INSIDE the zip,
echo or from a temp folder. That never works.
echo.
echo Close this. In Downloads:
echo   right-click Rise-Above-Meld.zip
echo   Extract All
echo Then open the FOLDER named Rise-Above-Meld
echo and double-click 00-DOUBLE-CLICK-ME.html
echo.
echo This copy is running from:
echo   %~dp0
echo.
pause
exit /b 1
