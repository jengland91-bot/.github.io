#Requires -Version 5.1
param(
    [string]$Game
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$configPath = Join-Path $repoRoot "overlays\shared\config.js"

if (-not (Test-Path $configPath)) {
    Write-Host "Cannot find overlays\shared\config.js" -ForegroundColor Red
    Write-Host "EXTRACT the zip, then run Change-Game.bat from the tools folder inside that folder."
    Write-Host "Looked in: $configPath"
    exit 1
}

$raw = [System.IO.File]::ReadAllText($configPath)
$current = "BeamNG"
$m = [regex]::Match($raw, '(?m)^(\s*game:\s*")([^"]*)(")')
if ($m.Success) { $current = $m.Groups[2].Value }

$presets = @(
    "BeamNG"
    "SnowRunner"
    "Forza Horizon"
    "GTA V"
    "Euro Truck Simulator 2"
)

function Get-GameName {
    param([string]$Asked, [string]$CurrentName, [string[]]$List)
    if ($Asked) { return $Asked.Trim() }

    Write-Host ""
    Write-Host "STARTING SOON game title" -ForegroundColor White
    Write-Host ("Current: " + $CurrentName)
    Write-Host ""
    for ($i = 0; $i -lt $List.Count; $i++) {
        Write-Host ("  " + ($i + 1) + ") " + $List[$i])
    }
    Write-Host "  6) Type a different name"
    Write-Host ""
    $pick = Read-Host "Pick 1-6, or type the game (Enter keeps it)"
    if (-not $pick) { return $CurrentName }
    if ($pick -eq "6") {
        $typed = Read-Host "Game name"
        return $typed.Trim()
    }
    $idx = 0
    $isNum = [int]::TryParse($pick, [ref]$idx)
    if ($isNum -and $idx -ge 1 -and $idx -le $List.Count) {
        return $List[$idx - 1]
    }
    return $pick.Trim()
}

$game = Get-GameName -Asked $Game -CurrentName $current -List $presets
if (-not $game) { $game = $current }
if ($game.IndexOfAny([char[]]@("`r", "`n")) -ge 0) {
    Write-Host "Game name cannot have a line break." -ForegroundColor Red
    exit 1
}

$escaped = $game.Replace("\", "\\").Replace('"', '\"')
$forReplace = $escaped.Replace('$', '$$')
$updated = [regex]::Replace($raw, '(?m)^(\s*game:\s*")([^"]*)(")', ('${1}' + $forReplace + '${3}'), 1)

if ($updated -eq $raw -and $game -eq $current) {
    Write-Host ("Already set to " + $game)
}
elseif ($updated -eq $raw) {
    Write-Host "Could not find the game: line in config.js" -ForegroundColor Red
    Write-Host "Open overlays\shared\config.js and change game: `"...`" yourself."
    exit 1
}
else {
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($configPath, $updated, $utf8)
}

Write-Host ""
Write-Host ("Starting Soon will say: " + $game) -ForegroundColor Green
Write-Host ""
Write-Host "In OBS: click STARTING SOON, right-click Overlay / Starting Soon -> Refresh."
Write-Host "Or click GRID, then STARTING SOON again (that overlay reloads itself)."
Write-Host "You do not run Install-OBS.bat for this."
Write-Host ""
Write-Host "Optional: in OBS you can also add ?game=SnowRunner to the overlay URL."
