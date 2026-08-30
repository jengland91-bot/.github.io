#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
Write-Host ""
Write-Host "Rise Above - copying the Meld file to your Desktop..."

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$src = Join-Path $repoRoot "meld\Rise-Above-Meld.json"
if (-not (Test-Path $src)) {
    Write-Host "Cannot find meld\Rise-Above-Meld.json" -ForegroundColor Red
    Write-Host "Extract the zip first. Looked in: $repoRoot"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$deskFile = Join-Path $desktop "Rise-Above-Meld.json"
$rootFile = Join-Path $repoRoot "IMPORT-THIS-IN-MELD.json"
Copy-Item -LiteralPath $src -Destination $deskFile -Force
Copy-Item -LiteralPath $src -Destination $rootFile -Force

Write-Host ""
Write-Host "The Meld import file is on your DESKTOP:" -ForegroundColor Green
Write-Host "  $deskFile"
Write-Host ""
Write-Host "It is also in this folder as IMPORT-THIS-IN-MELD.json"
Write-Host ""

$serverBat = Join-Path $scriptDir "Start-MeldLayout.bat"
Start-Process -FilePath $serverBat

$meld = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Meld Studio\Meld Studio.exe"),
    (Join-Path $env:LOCALAPPDATA "Meld Studio\Meld Studio.exe"),
    (Join-Path ${env:ProgramFiles} "Meld Studio\Meld Studio.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Meld Studio\Meld Studio.exe")
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $meld) {
    $lnk = Get-ChildItem -LiteralPath (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs") -Filter "*Meld*.lnk" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($lnk) {
        Start-Process -FilePath $lnk.FullName
        Write-Host "Opened Meld from the Start Menu."
    } else {
        Write-Host "Open Meld Studio yourself (could not find Meld Studio.exe)." -ForegroundColor Yellow
    }
} else {
    Start-Process -FilePath $meld
    Write-Host "Opened Meld Studio."
}

Start-Sleep -Seconds 2
Start-Process explorer.exe -ArgumentList "/select,`"$deskFile`""

Write-Host ""
Write-Host "IN MELD (3 clicks):" -ForegroundColor White
Write-Host "  1. File"
Write-Host "  2. Import Session"
Write-Host "  3. Pick Rise-Above-Meld.json on your DESKTOP"
Write-Host ""
Write-Host "Leave the black overlay-server window open."
Write-Host "Then in Meld add Game Capture + your cameras."
Write-Host ""
Read-Host "Press Enter to close this window"
