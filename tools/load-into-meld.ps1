#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# Meld has no import CLI. File -> Import Session cannot be clicked reliably
# (Qt menus are not exposed to UI Automation). This script writes session.json
# into Meld's data folder, then launches Meld with --data-path so the scenes
# are already there. Do not paste code into Meld.

Write-Host ""
Write-Host "Rise Above - installing scenes into Meld Studio..."
Write-Host "Leave this window open."
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$srcAll = Join-Path $repoRoot "LOAD-THESE-SCENES\0 ALL SCENES.json"
if (-not (Test-Path -LiteralPath $srcAll)) {
    $srcAll = Join-Path $repoRoot "meld\Rise-Above-Meld.json"
}
if (-not (Test-Path -LiteralPath $srcAll)) {
    Write-Host "WRONG FOLDER. Extract the zip first." -ForegroundColor Red
    Write-Host "Looked in: $repoRoot"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
if (-not $desktop) { $desktop = Join-Path $env:USERPROFILE "Desktop" }
$logPath = Join-Path $desktop "Rise-Above-Meld-load-log.txt"
$kitLog = Join-Path $scriptDir "last-load-log.txt"

function Write-LoadLog {
    param([string]$Message, [string]$Color = "")
    $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $Message
    if ($Color) { Write-Host $Message -ForegroundColor $Color } else { Write-Host $Message }
    try {
        Add-Content -LiteralPath $logPath -Value $line -ErrorAction SilentlyContinue
        Add-Content -LiteralPath $kitLog -Value $line -ErrorAction SilentlyContinue
    } catch {}
}

try {
    Set-Content -LiteralPath $logPath -Value ("Rise Above Meld load  " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) -ErrorAction SilentlyContinue
    Set-Content -LiteralPath $kitLog -Value ("Rise Above Meld load  " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) -ErrorAction SilentlyContinue
} catch {}

$sceneDir = Join-Path $desktop "Rise Above scenes"
$srcFolder = Join-Path $repoRoot "LOAD-THESE-SCENES"
if (Test-Path -LiteralPath $srcFolder) {
    if (-not (Test-Path -LiteralPath $sceneDir)) {
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

Write-LoadLog "Session file: $json"

$serverBat = Join-Path $scriptDir "Start-MeldLayout.bat"
if (Test-Path -LiteralPath $serverBat) {
    Write-LoadLog "Starting overlay server (keep that window open)..."
    Start-Process -FilePath $serverBat
}

function Get-MeldProcesses {
    Get-Process -ErrorAction SilentlyContinue | Where-Object {
        ($_.ProcessName -match "Meld") -and ($_.ProcessName -notmatch "powershell|pwsh|cmd")
    }
}

function Stop-MeldStudio {
    $procs = @(Get-MeldProcesses)
    if ($procs.Count -eq 0) { return }
    Write-LoadLog "Closing Meld Studio so the scenes can be written in..."
    foreach ($p in $procs) {
        try { [void]$p.CloseMainWindow() } catch {}
    }
    $deadline = (Get-Date).AddSeconds(8)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 400
        if (@(Get-MeldProcesses).Count -eq 0) { break }
    }
    foreach ($p in @(Get-MeldProcesses)) {
        try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
    Start-Sleep -Milliseconds 900
}

function Add-UniqueDir {
    param($Map, [string]$Dir)
    if ([string]::IsNullOrWhiteSpace($Dir)) { return }
    if (-not (Test-Path -LiteralPath $Dir)) { return }
    try {
        $full = [IO.Path]::GetFullPath($Dir)
    } catch { return }
    $key = $full.ToLowerInvariant()
    if (-not $Map.ContainsKey($key)) { $Map[$key] = $full }
}

function Test-LooksLikeMeldSession {
    param([string]$Path)
    try {
        $text = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
        return ($text -match '"type"\s*:\s*"scene"' -or $text -match '"type"\s*:\s*"layer"')
    } catch {
        return $false
    }
}

function Get-MeldDataDirs {
    $map = @{}
    $names = @("MeldStudio", "Meld Studio", "meldstudio", "Meld", "Meld Studios")
    $roots = @($env:APPDATA, $env:LOCALAPPDATA)
    if ($env:USERPROFILE) {
        $roots += (Join-Path $env:USERPROFILE "AppData\LocalLow")
    }
    if ($env:TEMP) { Add-UniqueDir $map (Join-Path $env:TEMP "meld-studio") }

    foreach ($root in $roots) {
        if ([string]::IsNullOrWhiteSpace($root)) { continue }
        foreach ($n in $names) {
            Add-UniqueDir $map (Join-Path $root $n)
            Add-UniqueDir $map (Join-Path $root "$n\MeldStudio")
            Add-UniqueDir $map (Join-Path $root "$n\Meld Studio")
        }
    }

    $pkgRoot = Join-Path $env:LOCALAPPDATA "Packages"
    if (Test-Path -LiteralPath $pkgRoot) {
        Get-ChildItem -LiteralPath $pkgRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $isMeld = $_.Name -match "Meld"
            $rels = @(
                "LocalState",
                "LocalCache\Roaming",
                "LocalCache\Local",
                "LocalCache\Roaming\MeldStudio",
                "LocalCache\Roaming\Meld Studio",
                "LocalCache\Local\MeldStudio",
                "LocalCache\Local\Meld Studio",
                "LocalState\MeldStudio",
                "LocalState\Meld Studio"
            )
            foreach ($rel in $rels) {
                $dir = Join-Path $_.FullName $rel
                $sess = Join-Path $dir "session.json"
                $prefs = Join-Path $dir "prefs.json"
                if ((Test-Path -LiteralPath $sess) -or (Test-Path -LiteralPath $prefs)) {
                    Add-UniqueDir $map $dir
                } elseif ($isMeld -and (Test-Path -LiteralPath $dir)) {
                    Add-UniqueDir $map $dir
                }
            }
            if ($isMeld) {
                Get-ChildItem -LiteralPath $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
                    Where-Object {
                        $_.Name -eq "session.json" -or $_.Name -eq "prefs.json" -or $_.Name -like "MeldStudio_*"
                    } |
                    ForEach-Object {
                        Add-UniqueDir $map $_.DirectoryName
                        $parent = Split-Path $_.DirectoryName -Parent
                        if ($parent) { Add-UniqueDir $map $parent }
                    }
            }
        }
    }

    if (Get-Command Get-AppxPackage -ErrorAction SilentlyContinue) {
        Get-AppxPackage -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "Meld" } | ForEach-Object {
            $pf = Join-Path $env:LOCALAPPDATA ("Packages\" + $_.PackageFamilyName)
            Add-UniqueDir $map (Join-Path $pf "LocalState")
            Add-UniqueDir $map (Join-Path $pf "LocalCache\Roaming")
            Add-UniqueDir $map (Join-Path $pf "LocalCache\Local")
            Write-LoadLog ("Found Meld package: " + $_.Name + "  " + $_.PackageFamilyName)
        }
    }

    $out = New-Object System.Collections.Generic.List[string]
    foreach ($dir in $map.Values) { $out.Add($dir) }
    return $out
}

function Get-MeldLaunch {
    $exe = $null
    $appId = $null

    $aliasNames = @("meldstudio.exe", "MeldStudio.exe", "Meld Studio.exe")
    foreach ($name in $aliasNames) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source) {
            $exe = $cmd.Source
            break
        }
        try {
            $w = & where.exe $name 2>$null | Select-Object -First 1
            if ($w -and (Test-Path -LiteralPath $w)) {
                $exe = $w
                break
            }
        } catch {}
    }

    $paths = @(
        (Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\meldstudio.exe"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\MeldStudio.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Meld Studio\Meld Studio.exe"),
        (Join-Path $env:LOCALAPPDATA "Meld Studio\Meld Studio.exe"),
        (Join-Path ${env:ProgramFiles} "Meld Studio\Meld Studio.exe")
    )
    if (${env:ProgramFiles(x86)}) {
        $paths += Join-Path ${env:ProgramFiles(x86)} "Meld Studio\Meld Studio.exe"
    }
    if (-not $exe) {
        foreach ($p in $paths) {
            if ($p -and (Test-Path -LiteralPath $p)) { $exe = $p; break }
        }
    }

    if (Get-Command Get-StartApps -ErrorAction SilentlyContinue) {
        $app = Get-StartApps -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "Meld Studio" } | Select-Object -First 1
        if ($app) { $appId = $app.AppID }
    }

    if (-not $exe) {
        $startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
        $lnk = Get-ChildItem -LiteralPath $startMenu -Filter "*Meld*.lnk" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($lnk) { $exe = $lnk.FullName }
    }

    return @{ Exe = $exe; AppId = $appId }
}

function Install-SessionFile {
    param([string]$Dir, [string]$Source)
    if (-not (Test-Path -LiteralPath $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
    }
    $dest = Join-Path $Dir "session.json"
    if (Test-Path -LiteralPath $dest) {
        $already = $false
        try {
            $old = Get-Content -LiteralPath $dest -Raw -ErrorAction Stop
            if ($old -match "STARTING SOON" -and $old -match "RACE DUAL") { $already = $true }
        } catch {}
        if (-not $already) {
            $bak = Join-Path $Dir ("session.json.bak-before-rise-above-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
            try { Copy-Item -LiteralPath $dest -Destination $bak -Force } catch {}
            Write-LoadLog "Backed up old session: $bak"
        }
    }
    $ok = $false
    for ($i = 0; $i -lt 6; $i++) {
        try {
            Copy-Item -LiteralPath $Source -Destination $dest -Force -ErrorAction Stop
            $written = Get-Content -LiteralPath $dest -Raw -ErrorAction Stop
            if ($written -match "STARTING SOON") {
                $ok = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 400
        }
    }
    if ($ok) {
        Write-LoadLog "Wrote scenes into: $dest" "Green"
        $backupDir = Join-Path $Dir "backups"
        if (Test-Path -LiteralPath $backupDir) {
            try {
                Copy-Item -LiteralPath $Source -Destination (Join-Path $backupDir "Rise-Above-Meld.json") -Force
            } catch {}
        }
    } else {
        Write-LoadLog "Could not write: $dest" "Yellow"
    }
    return $ok
}

function Copy-MeldSidecars {
    param([string]$FromDir, [string]$ToDir)
    if (-not (Test-Path -LiteralPath $FromDir)) { return }
    if ($FromDir.ToLowerInvariant() -eq $ToDir.ToLowerInvariant()) { return }
    Get-ChildItem -LiteralPath $FromDir -File -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -ne "session.json" -and $_.Extension -match "\.(json|ini|conf)$"
    } | ForEach-Object {
        try { Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $ToDir $_.Name) -Force } catch {}
    }
}

function Start-MeldStudio {
    param($Launch, [string]$DataPath)
    $arg = $null
    if ($DataPath) { $arg = "--data-path=`"$DataPath`"" }

    $exe = $Launch.Exe
    if ($exe -and ($exe -like "*.lnk") -and $DataPath) {
        $exe = $null
    }
    if ($exe) {
        Write-LoadLog ("Starting Meld: " + $exe + " " + $arg)
        try {
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = $exe
            if ($arg) { $psi.Arguments = $arg }
            $psi.UseShellExecute = $true
            [void][Diagnostics.Process]::Start($psi)
            return $true
        } catch {
            Write-LoadLog ("Start-Process failed: " + $_.Exception.Message) "Yellow"
        }
        try {
            if ($arg) { Start-Process -FilePath $exe -ArgumentList $arg } else { Start-Process -FilePath $exe }
            return $true
        } catch {}
    }

    if ($arg) {
        foreach ($name in @("meldstudio.exe", "MeldStudio.exe")) {
            try {
                Start-Process -FilePath $name -ArgumentList $arg
                Write-LoadLog "Started $name with data-path"
                return $true
            } catch {}
        }
    }

    if ($Launch.AppId -and -not $DataPath) {
        try {
            Start-Process explorer.exe -ArgumentList ("shell:AppsFolder\" + $Launch.AppId)
            Write-LoadLog ("Started Meld via Start Menu id " + $Launch.AppId)
            return $true
        } catch {}
    }
    return $false
}

function New-RiseAboveShortcut {
    param([string]$Exe, [string]$DataPath)
    if (-not $DataPath) { return }
    $target = $Exe
    if (-not $target -or ($target -like "*.lnk")) { $target = "meldstudio.exe" }
    try {
        $w = New-Object -ComObject WScript.Shell
        $lnkPath = Join-Path $desktop "Rise Above Meld.lnk"
        $sc = $w.CreateShortcut($lnkPath)
        $sc.TargetPath = $target
        $sc.Arguments = "--data-path=`"$DataPath`""
        $sc.WorkingDirectory = $repoRoot
        $sc.Description = "Open Meld Studio with Rise Above scenes"
        $sc.Save()
        Write-LoadLog "Desktop shortcut: $lnkPath"
    } catch {
        Write-LoadLog ("Could not create shortcut: " + $_.Exception.Message)
    }
}

$kitData = Join-Path $env:LOCALAPPDATA "Rise-Above-Meld\meld-data"
if (-not (Test-Path -LiteralPath $kitData)) {
    New-Item -ItemType Directory -Path $kitData -Force | Out-Null
}

$launch = Get-MeldLaunch
if (-not $launch.Exe -and -not $launch.AppId) {
    Write-LoadLog "Could not find Meld Studio. Install it from meldstudio.co then run this bat again." "Yellow"
    Write-LoadLog "The session file is ready at: $json"
    Start-Process explorer.exe -ArgumentList "/select,`"$json`""
    exit 0
}

Stop-MeldStudio

$dirs = @(Get-MeldDataDirs)
if ($dirs.Count -eq 0 -and ($launch.Exe -or $launch.AppId)) {
    Write-LoadLog "Meld data folder not found yet. Opening Meld once so it creates one..."
    [void](Start-MeldStudio -Launch $launch -DataPath $null)
    Start-Sleep -Seconds 5
    Stop-MeldStudio
    $dirs = @(Get-MeldDataDirs)
}

Write-LoadLog ("Meld data folders found: " + $dirs.Count)
foreach ($d in $dirs) { Write-LoadLog "  $d" }

$wrote = 0
$prefsSource = $null
foreach ($d in $dirs) {
    if (Test-Path -LiteralPath (Join-Path $d "prefs.json")) { $prefsSource = $d }
    if (Install-SessionFile -Dir $d -Source $srcAll) { $wrote++ }
}

if ($prefsSource) {
    Copy-MeldSidecars -FromDir $prefsSource -ToDir $kitData
    Write-LoadLog "Copied Meld settings from: $prefsSource"
}

if (Install-SessionFile -Dir $kitData -Source $srcAll) { $wrote++ }

if ($wrote -eq 0) {
    Write-LoadLog "Could not write session.json anywhere." "Red"
} else {
    Write-LoadLog ("Installed Rise Above scenes into $wrote location(s).") "Green"
}

New-RiseAboveShortcut -Exe $launch.Exe -DataPath $kitData

$started = Start-MeldStudio -Launch $launch -DataPath $kitData
if (-not $started) {
    Write-LoadLog "Retrying Meld without data-path..."
    $started = Start-MeldStudio -Launch $launch -DataPath $null
}

Start-Sleep -Seconds 3
$stillOurs = $false
$check = Join-Path $kitData "session.json"
if (Test-Path -LiteralPath $check) {
    try {
        $t = Get-Content -LiteralPath $check -Raw -ErrorAction Stop
        if ($t -match "STARTING SOON") { $stillOurs = $true }
    } catch {}
}
if (-not $stillOurs) {
    Write-LoadLog "Re-writing session.json after Meld started (it may have replaced it)..." "Yellow"
    Stop-MeldStudio
    [void](Install-SessionFile -Dir $kitData -Source $srcAll)
    foreach ($d in $dirs) { [void](Install-SessionFile -Dir $d -Source $srcAll) }
    [void](Start-MeldStudio -Launch $launch -DataPath $kitData)
}

try { Set-Clipboard -Value $json } catch {
    try {
        Add-Type -AssemblyName System.Windows.Forms | Out-Null
        [System.Windows.Forms.Clipboard]::SetText($json)
    } catch {}
}

Write-Host ""
if ($wrote -gt 0) {
    Write-Host "Scenes are in Meld now: STARTING SOON, GRID, DESK, RACE, BRB, ENDING." -ForegroundColor Green
    Write-Host "Use the Meld window that just opened (or the Desktop shortcut Rise Above Meld)."
    Write-Host "Then add Game Capture + your cameras."
} else {
    Write-Host "Could not install automatically. In Meld: File -> Import Session -> Ctrl+V -> Open" -ForegroundColor Yellow
    Write-Host "  $json"
}
Write-Host ""
Write-Host "Leave the overlay window (KEEP THIS WINDOW OPEN) running."
Write-Host "Log: $logPath"
Write-Host ""
