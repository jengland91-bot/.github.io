#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
Write-Host ""
Write-Host "Rise Above - loading scenes into Meld Studio..."
Write-Host "Leave this window open."
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$srcAll = Join-Path $repoRoot "LOAD-THESE-SCENES\0 ALL SCENES.json"
if (-not (Test-Path $srcAll)) {
    $srcAll = Join-Path $repoRoot "meld\Rise-Above-Meld.json"
}
if (-not (Test-Path $srcAll)) {
    Write-Host "WRONG FOLDER. Extract the zip first." -ForegroundColor Red
    Write-Host "Looked in: $repoRoot"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
if (-not $desktop) { $desktop = Join-Path $env:USERPROFILE "Desktop" }
$sceneDir = Join-Path $desktop "Rise Above scenes"
$srcFolder = Join-Path $repoRoot "LOAD-THESE-SCENES"
if (Test-Path $srcFolder) {
    if (-not (Test-Path $sceneDir)) {
        New-Item -ItemType Directory -Path $sceneDir -Force | Out-Null
    }
    Copy-Item -Path (Join-Path $srcFolder "*") -Destination $sceneDir -Force
} else {
    New-Item -ItemType Directory -Path $sceneDir -Force | Out-Null
}
$json = Join-Path $sceneDir "0 ALL SCENES.json"
Copy-Item -LiteralPath $srcAll -Destination $json -Force
Copy-Item -LiteralPath $srcAll -Destination (Join-Path $repoRoot "IMPORT-THIS-IN-MELD.json") -Force
Copy-Item -LiteralPath $srcAll -Destination (Join-Path $desktop "Rise-Above-Meld.json") -Force

Write-Host "Session file:"
Write-Host "  $json"
Write-Host ""

$serverBat = Join-Path $scriptDir "Start-MeldLayout.bat"
if (Test-Path $serverBat) {
    Write-Host "Starting overlay server (keep that window open)..."
    Start-Process -FilePath $serverBat
}

function Get-MeldExe {
    $paths = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Meld Studio\Meld Studio.exe"),
        (Join-Path $env:LOCALAPPDATA "Meld Studio\Meld Studio.exe"),
        (Join-Path ${env:ProgramFiles} "Meld Studio\Meld Studio.exe")
    )
    if (${env:ProgramFiles(x86)}) {
        $paths += Join-Path ${env:ProgramFiles(x86)} "Meld Studio\Meld Studio.exe"
    }
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    $startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
    $lnk = Get-ChildItem -LiteralPath $startMenu -Filter "*Meld*.lnk" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($lnk) { return $lnk.FullName }
    return $null
}

function Get-MeldProcess {
    Get-Process -ErrorAction SilentlyContinue | Where-Object {
        ($_.ProcessName -match "Meld") -and ($_.MainWindowHandle -ne [IntPtr]::Zero)
    } | Select-Object -First 1
}

$meld = Get-MeldExe
if (-not $meld) {
    Write-Host "Could not find Meld Studio. Open it yourself, then File -> Import Session ->" -ForegroundColor Yellow
    Write-Host "  $json"
    Start-Process explorer.exe -ArgumentList "/select,`"$json`""
    exit 0
}

Write-Host "Opening Meld Studio with the session file..."
try {
    Start-Process -FilePath $meld -ArgumentList @($json)
} catch {
    Start-Process -FilePath $meld
}

$proc = $null
for ($i = 0; $i -lt 50; $i++) {
    Start-Sleep -Milliseconds 400
    $proc = Get-MeldProcess
    if ($proc) { break }
}
if (-not $proc) {
    Write-Host "Meld did not show a window yet. Starting it again..."
    Start-Process -FilePath $meld
    Start-Sleep -Seconds 4
    $proc = Get-MeldProcess
}

Add-Type -AssemblyName System.Windows.Forms | Out-Null
try { Add-Type -AssemblyName UIAutomationClient } catch {}
try { Add-Type -AssemblyName UIAutomationTypes } catch {}

$wshell = New-Object -ComObject WScript.Shell
try { Set-Clipboard -Value $json } catch {
    try { [System.Windows.Forms.Clipboard]::SetText($json) } catch {}
}

function Invoke-NamedButton([string]$name) {
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $cond = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty, $name)
        $el = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
        if (-not $el) { return $false }
        $pat = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $pat.Invoke()
        return $true
    } catch {
        return $false
    }
}

function Send-ImportKeys {
    $ok = $false
    if ($proc) { $ok = [bool]$wshell.AppActivate($proc.Id) }
    if (-not $ok) { $ok = [bool]$wshell.AppActivate("Meld Studio") }
    if (-not $ok) {
        Write-Host "Click the Meld Studio window if you see it..."
        Start-Sleep -Seconds 3
        $ok = [bool]$wshell.AppActivate("Meld Studio")
    }
    if (-not $ok) {
        Write-Host "Could not focus Meld. The file path is copied."
        Write-Host "In Meld: File -> Import Session -> Ctrl+V -> Open."
        return
    }
    Start-Sleep -Milliseconds 700
    $wshell.SendKeys("%f")
    Start-Sleep -Milliseconds 600
    $clicked = $false
    foreach ($label in @("Import Session", "Import Session...")) {
        if (Invoke-NamedButton $label) { $clicked = $true; break }
    }
    if (-not $clicked) {
        Write-Host "Could not click Import Session automatically. The file path is copied."
        Write-Host "In Meld: File -> Import Session -> Ctrl+V -> Open."
        return
    }
    Start-Sleep -Milliseconds 900
    $wshell.SendKeys("^v")
    Start-Sleep -Milliseconds 250
    $wshell.SendKeys("{ENTER}")
}

Write-Host "Asking Meld to Import Session..."
Start-Sleep -Seconds 2
Send-ImportKeys

Write-Host ""
Write-Host "If RACE / STARTING SOON / BRB appeared in Meld, you are done." -ForegroundColor Green
Write-Host "Then add Game Capture + your cameras."
Write-Host ""
Write-Host "If Meld is still empty:"
Write-Host "  File -> Import Session"
Write-Host "  paste (Ctrl+V) or pick:"
Write-Host "  $json"
Write-Host ""
Write-Host "Leave the overlay window (KEEP THIS WINDOW OPEN) running."
Write-Host ""
