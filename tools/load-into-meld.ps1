#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# Do not close Meld. Do not overwrite session.json. Do not use --data-path.
# Those crashed Meld. This only copies the import file and opens Meld.

Write-Host ""
Write-Host "Rise Above - putting the session file on your Desktop..."
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$srcAll = Join-Path $repoRoot "LOAD-THESE-SCENES\0 ALL SCENES.json"
if (-not (Test-Path -LiteralPath $srcAll)) {
    $srcAll = Join-Path $repoRoot "meld\Rise-Above-Meld.json"
}
if (-not (Test-Path -LiteralPath $srcAll)) {
    $srcAll = Join-Path $repoRoot "IMPORT-THIS-IN-MELD.json"
}
if (-not (Test-Path -LiteralPath $srcAll)) {
    Write-Host "WRONG FOLDER. Extract the GitHub zip first." -ForegroundColor Red
    Write-Host "Looked in: $repoRoot"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
if (-not $desktop) { $desktop = Join-Path $env:USERPROFILE "Desktop" }
$deskFile = Join-Path $desktop "Rise-Above.json"
Copy-Item -LiteralPath $srcAll -Destination $deskFile -Force
Copy-Item -LiteralPath $srcAll -Destination (Join-Path $repoRoot "IMPORT-THIS-IN-MELD.json") -Force

$sceneDir = Join-Path $desktop "Rise Above scenes"
$srcFolder = Join-Path $repoRoot "LOAD-THESE-SCENES"
if (Test-Path -LiteralPath $srcFolder) {
    if (-not (Test-Path -LiteralPath $sceneDir)) {
        New-Item -ItemType Directory -Path $sceneDir -Force | Out-Null
    }
    Copy-Item -Path (Join-Path $srcFolder "*") -Destination $sceneDir -Force
}

try { Set-Clipboard -Value $deskFile } catch {
    try {
        Add-Type -AssemblyName System.Windows.Forms | Out-Null
        [System.Windows.Forms.Clipboard]::SetText($deskFile)
    } catch {}
}

Write-Host "Session file is on your DESKTOP:" -ForegroundColor Green
Write-Host "  $deskFile"
Write-Host ""

function Get-MeldLaunch {
    foreach ($name in @("meldstudio.exe", "MeldStudio.exe")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source) { return $cmd.Source }
        try {
            $w = & where.exe $name 2>$null | Select-Object -First 1
            if ($w) { return $w }
        } catch {}
    }
    $paths = @(
        (Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\meldstudio.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Meld Studio\Meld Studio.exe"),
        (Join-Path ${env:ProgramFiles} "Meld Studio\Meld Studio.exe")
    )
    foreach ($p in $paths) {
        if ($p -and (Test-Path -LiteralPath $p)) { return $p }
    }
    if (Get-Command Get-StartApps -ErrorAction SilentlyContinue) {
        $app = Get-StartApps -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "Meld Studio" } | Select-Object -First 1
        if ($app) { return ("shell:" + $app.AppID) }
    }
    return $null
}

$meld = Get-MeldLaunch
$running = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match "Meld" })
if ($running.Count -eq 0 -and $meld) {
    Write-Host "Opening Meld Studio (normal window, no extra flags)..."
    try {
        if ($meld.StartsWith("shell:")) {
            Start-Process explorer.exe -ArgumentList ("shell:AppsFolder\" + $meld.Substring(6))
        } else {
            Start-Process -FilePath $meld
        }
    } catch {
        Write-Host "Open Meld Studio yourself." -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 3
}

Start-Process explorer.exe -ArgumentList "/select,`"$deskFile`""

Write-Host ""
Write-Host "IN MELD (this will not crash it):" -ForegroundColor White
Write-Host "  1. File"
Write-Host "  2. Import Session   (not Import OBS Session)"
Write-Host "  3. Pick  Rise-Above.json  on your DESKTOP"
Write-Host "     or paste (Ctrl+V) and Open"
Write-Host ""
Write-Host "Overlays load from the internet. No black server window needed."
Write-Host "Then add Game Capture + cameras."
Write-Host ""
Write-Host "If Meld crashed earlier: File -> Restore from Backup"
Write-Host ""
