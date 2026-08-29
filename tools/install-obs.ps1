#Requires -Version 5.1
param(
    [switch]$AitumOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$overlayDir = Join-Path $repoRoot "overlays"

Write-Host ""
Write-Host 'Rise Above - push scenes into OBS' -ForegroundColor White
Write-Host ""

if (-not (Test-Path (Join-Path $overlayDir "live.html"))) {
    Write-Host 'Cannot find overlays\live.html' -ForegroundColor Red
    Write-Host 'You must EXTRACT the zip, then run Install-OBS.bat from the tools folder inside that extracted folder.'
    Write-Host "Looked in: $overlayDir"
    exit 1
}
if (-not (Test-Path (Join-Path $overlayDir "desk.html"))) {
    Write-Host 'Cannot find overlays\desk.html' -ForegroundColor Red
    Write-Host 'You have an old zip. Download a fresh one so DESK is in it.'
    Write-Host "Looked in: $overlayDir"
    exit 1
}
if (-not (Test-Path (Join-Path $overlayDir "vertical\live.html"))) {
    Write-Host 'Cannot find overlays\vertical\live.html' -ForegroundColor Red
    Write-Host 'You need the zip that includes the vertical overlays folder.'
    exit 1
}
if (-not (Test-Path (Join-Path $overlayDir "vertical\desk.html"))) {
    Write-Host 'Cannot find overlays\vertical\desk.html' -ForegroundColor Red
    Write-Host 'You have an old zip. Download a fresh one so DESK is in it.'
    exit 1
}

function Open-HtmlInstaller {
    $html = Join-Path $scriptDir "install.html"
    Write-Host ""
    Write-Host 'Open this page in Chrome or Edge on this PC instead:' -ForegroundColor Yellow
    Write-Host $html
    if (Test-Path $html) { Start-Process $html }
}

if (-not ("System.Net.WebSockets.ClientWebSocket" -as [type])) {
    try { Add-Type -AssemblyName System } catch {}
}
if (-not ("System.Net.WebSockets.ClientWebSocket" -as [type])) {
    Write-Host 'Windows PowerShell on this PC cannot open WebSockets.' -ForegroundColor Red
    Open-HtmlInstaller
    exit 1
}

Write-Host "Overlay folder: $overlayDir"
Write-Host ""
Write-Host 'OBS must be open. Top menu: Tools -> WebSocket Server Settings -> Enable.'
Write-Host 'Copy the password from Show Connect Info.'
Write-Host ""
$password = Read-Host 'Paste OBS WebSocket password'

$css = "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }"
$collectionName = "Rise Above BeamNG"
$verticalCollectionName = "Rise Above BeamNG Vertical"
$overlaySlash = ($overlayDir -replace "\\", "/")
$script:canvasW = 1920
$script:canvasH = 1080

$scenes = @(
    "STARTING SOON", "GRID", "DESK", "RACE", "RACE DUAL", "REPLAY", "BRB", "ENDING"
)

$overlayFiles = @{
    "Overlay / Starting Soon" = @{ File = "starting-soon.html"; Shutdown = $true; Restart = $true }
    "Overlay / Grid HUD"      = @{ File = "chatting.html"; Shutdown = $false; Restart = $false }
    "Overlay / Desk HUD"      = @{ File = "desk.html"; Shutdown = $false; Restart = $false }
    "Overlay / Race HUD"      = @{ File = "live.html"; Shutdown = $false; Restart = $false }
    "Overlay / Dual HUD"      = @{ File = "race-dual.html"; Shutdown = $false; Restart = $false }
    "Overlay / Replay HUD"    = @{ File = "replay.html"; Shutdown = $false; Restart = $false }
    "Overlay / BRB"           = @{ File = "brb.html"; Shutdown = $true; Restart = $true }
    "Overlay / Ending"        = @{ File = "ending.html"; Shutdown = $true; Restart = $true }
}
$script:overlayFiles = $overlayFiles

$items = @{
    "STARTING SOON" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / Starting Soon"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
    )
    "GRID" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Cam / Face"; kind = "camera"; x = 48; y = 168; w = 960; h = 540 }
        @{ name = "Cam / Room"; kind = "camera"; x = 1032; y = 168; w = 840; h = 360 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 1032; y = 544; w = 408; h = 200 }
        @{ name = "Cam / Pedals"; kind = "camera"; x = 1464; y = 544; w = 408; h = 200 }
        @{ name = "Overlay / Grid HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
    )
    "DESK" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Cam / Face"; kind = "camera"; x = 1256; y = 696; w = 640; h = 360 }
        @{ name = "Cam / Room"; kind = "camera"; x = 760; y = 786; w = 480; h = 270 }
        @{ name = "Overlay / Desk HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "RACE" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Cam / Face"; kind = "camera"; x = 48; y = 876; w = 320; h = 180 }
        @{ name = "Cam / Room"; kind = "camera"; x = 384; y = 876; w = 320; h = 180 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 720; y = 876; w = 320; h = 180 }
        @{ name = "Cam / Pedals"; kind = "camera"; x = 1056; y = 876; w = 320; h = 180 }
        @{ name = "Overlay / Race HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Media / Hype Clip"; kind = "media"; x = 0; y = 0; w = 1920; h = 1080; enabled = $false }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "RACE DUAL" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Game / Angle 2"; kind = "game"; x = 1248; y = 48; w = 640; h = 360 }
        @{ name = "Cam / Face"; kind = "camera"; x = 48; y = 900; w = 240; h = 135 }
        @{ name = "Cam / Room"; kind = "camera"; x = 304; y = 900; w = 240; h = 135 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 560; y = 900; w = 240; h = 135 }
        @{ name = "Cam / Pedals"; kind = "camera"; x = 816; y = 900; w = 240; h = 135 }
        @{ name = "Overlay / Dual HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "REPLAY" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Overlay / Replay HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "BRB" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / BRB"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
    )
    "ENDING" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / Ending"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
    )
}

$verticalOverlayFiles = @{
    "Overlay / Starting Soon" = @{ File = "vertical/starting-soon.html"; Shutdown = $true; Restart = $true }
    "Overlay / Grid HUD"      = @{ File = "vertical/chatting.html"; Shutdown = $false; Restart = $false }
    "Overlay / Desk HUD"      = @{ File = "vertical/desk.html"; Shutdown = $false; Restart = $false }
    "Overlay / Race HUD"      = @{ File = "vertical/live.html"; Shutdown = $false; Restart = $false }
    "Overlay / Dual HUD"      = @{ File = "vertical/race-dual.html"; Shutdown = $false; Restart = $false }
    "Overlay / Replay HUD"    = @{ File = "vertical/replay.html"; Shutdown = $false; Restart = $false }
    "Overlay / BRB"           = @{ File = "vertical/brb.html"; Shutdown = $true; Restart = $true }
    "Overlay / Ending"        = @{ File = "vertical/ending.html"; Shutdown = $true; Restart = $true }
}

$verticalItems = @{
    "STARTING SOON" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / Starting Soon"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
    )
    "GRID" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Cam / Face"; kind = "camera"; x = 16; y = 88; w = 1048; h = 420 }
        @{ name = "Cam / Room"; kind = "camera"; x = 16; y = 524; w = 1048; h = 280 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 16; y = 820; w = 516; h = 200 }
        @{ name = "Cam / Pedals"; kind = "camera"; x = 548; y = 820; w = 516; h = 200 }
        @{ name = "Overlay / Grid HUD"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1080; h = 1920 }
    )
    "DESK" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1080; h = 608 }
        @{ name = "Cam / Face"; kind = "camera"; x = 16; y = 624; w = 520; h = 300 }
        @{ name = "Cam / Room"; kind = "camera"; x = 544; y = 624; w = 520; h = 300 }
        @{ name = "Overlay / Desk HUD"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "RACE" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1080; h = 608 }
        @{ name = "Cam / Face"; kind = "camera"; x = 16; y = 624; w = 520; h = 220 }
        @{ name = "Cam / Room"; kind = "camera"; x = 544; y = 624; w = 520; h = 220 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 16; y = 860; w = 520; h = 220 }
        @{ name = "Cam / Pedals"; kind = "camera"; x = 544; y = 860; w = 520; h = 220 }
        @{ name = "Overlay / Race HUD"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Media / Hype Clip"; kind = "media"; x = 0; y = 0; w = 1080; h = 1920; enabled = $false }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "RACE DUAL" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1080; h = 608 }
        @{ name = "Game / Angle 2"; kind = "game"; x = 16; y = 624; w = 1048; h = 200 }
        @{ name = "Cam / Face"; kind = "camera"; x = 16; y = 840; w = 520; h = 180 }
        @{ name = "Cam / Room"; kind = "camera"; x = 544; y = 840; w = 520; h = 180 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 16; y = 1036; w = 520; h = 180 }
        @{ name = "Cam / Pedals"; kind = "camera"; x = 544; y = 1036; w = 520; h = 180 }
        @{ name = "Overlay / Dual HUD"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "REPLAY" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 360; w = 1080; h = 608 }
        @{ name = "Overlay / Replay HUD"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1080; h = 1920 }
        @{ name = "Audio / Game"; kind = "gameaudio" }
    )
    "BRB" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / BRB"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
    )
    "ENDING" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / Ending"; kind = "browser"; x = 0; y = 0; w = 1080; h = 1920 }
    )
}

function Get-Sha256B64([string]$text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
        return [Convert]::ToBase64String($sha.ComputeHash($bytes))
    }
    finally { $sha.Dispose() }
}

function Send-ObsJson($ws, $obj) {
    $json = $obj | ConvertTo-Json -Compress -Depth 30
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $seg = [System.ArraySegment[byte]]::new($bytes)
    $ok = $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [System.Threading.CancellationToken]::None).Wait(10000)
    if (-not $ok) { throw "Send to OBS timed out" }
}

function Receive-Obs($ws) {
    $buffer = New-Object byte[] 262144
    $sb = New-Object System.Text.StringBuilder
    do {
        $seg = [System.ArraySegment[byte]]::new($buffer)
        $task = $ws.ReceiveAsync($seg, [System.Threading.CancellationToken]::None)
        if (-not $task.Wait(20000)) { throw "OBS stopped answering. Is it still open?" }
        $result = $task.Result
        [void]$sb.Append([System.Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count))
        $end = $result.EndOfMessage
    } while (-not $end)
    return $sb.ToString() | ConvertFrom-Json
}

function Get-ObsProp($obj, [string]$name) {
    if ($null -eq $obj) { return $null }
    $prop = $obj.PSObject.Properties[$name]
    if ($null -eq $prop) { return $null }
    return $prop.Value
}

function Invoke-Obs($ws, [string]$type, $data) {
    if ($null -eq $data) { $data = @{} }
    $script:reqId++
    $id = [string]$script:reqId
    Send-ObsJson $ws @{
        op = 6
        d  = @{
            requestType = $type
            requestId   = $id
            requestData = $data
        }
    }
    while ($true) {
        $msg = Receive-Obs $ws
        if ($msg.op -ne 7) { continue }
        $d = Get-ObsProp $msg "d"
        if ([string](Get-ObsProp $d "requestId") -ne $id) { continue }
        $status = Get-ObsProp $d "requestStatus"
        if (-not (Get-ObsProp $status "result")) {
            $comment = Get-ObsProp $status "comment"
            throw "$type failed: $comment"
        }
        $out = Get-ObsProp $d "responseData"
        if ($null -eq $out) { return @{} }
        return $out
    }
}

function Try-Obs($ws, [string]$type, $data) {
    try {
        return Invoke-Obs $ws $type $data
    }
    catch {
        return $null
    }
}

function Get-VendorAitumSceneNames($ws) {
    $vr = Try-Obs $ws "CallVendorRequest" @{
        vendorName  = "aitum-vertical-canvas"
        requestType = "get_scenes"
        requestData = @{ width = 1080; height = 1920 }
    }
    if ($null -eq $vr) { return @() }
    $inner = Get-ObsProp $vr "responseData"
    if ($null -eq $inner) { $inner = $vr }
    $arr = @(Get-ObsProp $inner "scenes")
    $out = @()
    foreach ($s in $arr) {
        if ($null -eq $s) { continue }
        if ($s -is [string]) { $out += [string]$s; continue }
        $n = Get-ObsProp $s "name"
        if (-not $n) { $n = Get-ObsProp $s "sceneName" }
        if ($n) { $out += [string]$n }
    }
    return $out
}

function Ensure-AitumScene($ws, $uuid, [string]$desired) {
    $vendor = @(Get-VendorAitumSceneNames $ws)
    foreach ($tryName in @($desired, "$desired V")) {
        if ($vendor -contains $tryName) {
            Write-Host "  have $tryName"
            return $tryName
        }
        try {
            Invoke-Obs $ws "CreateScene" @{ sceneName = $tryName; canvasUuid = $uuid } | Out-Null
            Write-Host "  scene $tryName"
            return $tryName
        }
        catch {
            Write-Host ("  skip $tryName (" + $_.Exception.Message + ")")
        }
    }
    return $null
}

function Ping-SceneCollection($ws) {
    $cols = Try-Obs $ws "GetSceneCollectionList" @{}
    if ($null -eq $cols) { return }
    $current = [string](Get-ObsProp $cols "currentSceneCollectionName")
    $names = @(Get-ObsProp $cols "sceneCollections")
    $other = $null
    foreach ($n in $names) {
        if ($n -and ([string]$n -ne $current)) { $other = [string]$n; break }
    }
    if (-not $other) { return }
    Write-Host "Refreshing Aitum dock (switch collection and back)..."
    try {
        Invoke-Obs $ws "SetCurrentSceneCollection" @{ sceneCollectionName = $other } | Out-Null
        Start-Sleep -Seconds 2
        Invoke-Obs $ws "SetCurrentSceneCollection" @{ sceneCollectionName = $current } | Out-Null
        Start-Sleep -Seconds 1
    }
    catch {
        Write-Host ("  refresh skipped: " + $_.Exception.Message)
    }
}

function Get-Kind($kinds, [string[]]$names) {
    foreach ($n in $names) {
        if ($kinds -contains $n) { return $n }
        $hit = $kinds | Where-Object { $_ -eq $n -or $_.StartsWith("$n`_v") } | Select-Object -First 1
        if ($hit) { return $hit }
    }
    return $null
}

function Get-BrowserSettings($name) {
    if ($name -eq "Lumia / Overlay" -or $name -eq "Lumia / Overlay V") {
        return @{
            is_local_file        = $false
            url                  = "about:blank"
            width                = $script:canvasW
            height               = $script:canvasH
            fps                  = 30
            fps_custom           = $true
            css                  = $css
            shutdown             = $false
            restart_when_active  = $false
        }
    }
    $meta = $script:overlayFiles[$name]
    $path = "$overlaySlash/$($meta.File)"
    return @{
        is_local_file        = $true
        local_file           = $path
        width                = $script:canvasW
        height               = $script:canvasH
        fps                  = 30
        fps_custom           = $true
        css                  = $css
        shutdown             = [bool]$meta.Shutdown
        restart_when_active  = [bool]$meta.Restart
    }
}

function Get-InputSpec($kinds, $item) {
    switch ($item.kind) {
        "browser" { return @{ inputKind = (Get-Kind $kinds @("browser_source")); settings = (Get-BrowserSettings $item.name) } }
        "lumia" { return @{ inputKind = (Get-Kind $kinds @("browser_source")); settings = (Get-BrowserSettings $item.name) } }
        "color" {
            return @{
                inputKind = (Get-Kind $kinds @("color_source_v3", "color_source"))
                settings  = @{ color = 4278978567; width = $script:canvasW; height = $script:canvasH }
            }
        }
        "game" {
            if ($item.name -eq "Game / Angle 2") {
                return @{
                    inputKind = (Get-Kind $kinds @("window_capture", "game_capture"))
                    settings  = @{ cursor = $false; capture_cursor = $false; capture_audio = $false }
                }
            }
            return @{
                inputKind = (Get-Kind $kinds @("game_capture", "window_capture"))
                settings  = @{ capture_mode = "any"; capture_cursor = $false; capture_audio = $false }
            }
        }
        "camera" {
            return @{
                inputKind = (Get-Kind $kinds @("dshow_input", "av_capture_input", "v4l2_input"))
                settings  = @{}
            }
        }
        "media" {
            return @{
                inputKind = (Get-Kind $kinds @("ffmpeg_source"))
                settings  = @{ looping = $false; restart_on_activate = $true; close_when_inactive = $true }
            }
        }
        "gameaudio" {
            return @{
                inputKind = (Get-Kind $kinds @("wasapi_process_output_capture"))
                settings  = @{}
            }
        }
        "mic" {
            return @{
                inputKind = (Get-Kind $kinds @("wasapi_input_capture", "coreaudio_input_capture"))
                settings  = @{}
            }
        }
        default { throw "Unknown kind $($item.kind)" }
    }
}

function Get-Transform($item) {
    if (-not $item.ContainsKey("w")) { return $null }
    return @{
        positionX       = [double]$item.x
        positionY       = [double]$item.y
        rotation        = 0.0
        scaleX          = 1.0
        scaleY          = 1.0
        alignment       = 5
        boundsType      = "OBS_BOUNDS_SCALE_INNER"
        boundsAlignment = 0
        boundsWidth     = [double][Math]::Max(1, $item.w)
        boundsHeight    = [double][Math]::Max(1, $item.h)
        cropLeft        = 0
        cropRight       = 0
        cropTop         = 0
        cropBottom      = 0
    }
}

$script:reqId = 0
$ws = New-Object System.Net.WebSockets.ClientWebSocket
try { $ws.Options.KeepAliveInterval = [TimeSpan]::FromSeconds(20) } catch {}

Write-Host 'Connecting to OBS on this PC...'
try {
    $connect = $ws.ConnectAsync([Uri]"ws://127.0.0.1:4455/", [System.Threading.CancellationToken]::None)
    if (-not $connect.Wait(5000)) { throw "timed out" }
    if ($connect.IsFaulted) { throw $connect.Exception.InnerException }
}
catch {
    Write-Host ""
    Write-Host 'Could not reach OBS.' -ForegroundColor Red
    Write-Host '1. Open OBS Studio'
    Write-Host '2. Top menu: File, Edit, Tools, Help'
    Write-Host '3. Tools -> WebSocket Server Settings -> Enable WebSocket server'
    Write-Host '4. Run this bat again'
    exit 1
}

$hello = Receive-Obs $ws
if ($hello.op -ne 0) { throw "Unexpected hello from OBS" }

$identify = @{ op = 1; d = @{ rpcVersion = 1 } }
if ($hello.d.PSObject.Properties.Name -contains "authentication") {
    $salt = [string]$hello.d.authentication.salt
    $challenge = [string]$hello.d.authentication.challenge
    $secret = Get-Sha256B64 ($password + $salt)
    $auth = Get-Sha256B64 ($secret + $challenge)
    $identify.d.authentication = $auth
}
Send-ObsJson $ws $identify

$identified = $null
for ($n = 0; $n -lt 10; $n++) {
    $msg = Receive-Obs $ws
    if ($msg.op -eq 2) { $identified = $msg; break }
}
if ($null -eq $identified) {
    Write-Host 'OBS rejected the password. Copy it from Tools -> WebSocket Server Settings -> Show Connect Info.' -ForegroundColor Red
    exit 1
}

Write-Host 'Connected.' -ForegroundColor Green

$ver = Invoke-Obs $ws "GetVersion" @{}
Write-Host ("OBS " + (Get-ObsProp $ver "obsVersion"))

$kindList = Invoke-Obs $ws "GetInputKindList" @{ unversioned = $false }
$kinds = @(Get-ObsProp $kindList "inputKinds")

function Use-RiseCollection($ws, [string]$name) {
    $cols = Invoke-Obs $ws "GetSceneCollectionList" @{}
    $colNames = @(Get-ObsProp $cols "sceneCollections")
    if ($colNames -contains $name) {
        Invoke-Obs $ws "SetCurrentSceneCollection" @{ sceneCollectionName = $name } | Out-Null
        Write-Host "Using collection $name"
    }
    else {
        Invoke-Obs $ws "CreateSceneCollection" @{ sceneCollectionName = $name } | Out-Null
        Write-Host "Created collection $name"
    }
    Start-Sleep -Seconds 1
}

function Set-RiseCanvas($ws, [int]$width, [int]$height) {
    $script:canvasW = $width
    $script:canvasH = $height
    Invoke-Obs $ws "SetVideoSettings" @{
        baseWidth      = $width
        baseHeight     = $height
        outputWidth    = $width
        outputHeight   = $height
        fpsNumerator   = 60
        fpsDenominator = 1
    } | Out-Null
}

function Test-Scene($ws, $name, $canvasUuid) {
    $data = @{}
    if ($canvasUuid) { $data["canvasUuid"] = $canvasUuid }
    $list = Invoke-Obs $ws "GetSceneList" $data
    $names = @(Get-ObsProp $list "scenes") | ForEach-Object { Get-ObsProp $_ "sceneName" }
    return ($names -contains $name)
}

function Test-Input($ws, $name) {
    $list = Invoke-Obs $ws "GetInputList" @{}
    $names = @(Get-ObsProp $list "inputs") | ForEach-Object { Get-ObsProp $_ "inputName" }
    return ($names -contains $name)
}

function Get-ItemId($ws, $scene, $source, $canvasUuid) {
    $data = @{ sceneName = $scene }
    if ($canvasUuid) { $data["canvasUuid"] = $canvasUuid }
    $list = Invoke-Obs $ws "GetSceneItemList" $data
    $hit = @(Get-ObsProp $list "sceneItems") | Where-Object { (Get-ObsProp $_ "sourceName") -eq $source } | Select-Object -First 1
    if ($hit) { return [int](Get-ObsProp $hit "sceneItemId") }
    return $null
}

function Get-SourceName($item, $sourceNameMap) {
    if ($sourceNameMap -and $sourceNameMap.ContainsKey($item.name)) {
        return [string]$sourceNameMap[$item.name]
    }
    return [string]$item.name
}

function Install-RiseScenes($ws, $kinds, $sceneNames, $sceneItems, $canvasUuid, $sourceNameMap) {
    $kitToObs = @{}
    if ($canvasUuid) {
        $vendor = @(Get-VendorAitumSceneNames $ws)
        foreach ($defaultName in @("Vertical Scene", "Scene")) {
            if ($vendor -contains $defaultName) {
                foreach ($newName in @("STARTING SOON", "STARTING SOON V")) {
                    try {
                        Invoke-Obs $ws "SetSceneName" @{
                            sceneName    = $defaultName
                            newSceneName = $newName
                            canvasUuid   = $canvasUuid
                        } | Out-Null
                        Write-Host "  renamed $defaultName -> $newName"
                        break
                    }
                    catch {
                        Write-Host ("  rename $defaultName -> $newName failed")
                    }
                }
            }
        }
        foreach ($scene in $sceneNames) {
            $actual = Ensure-AitumScene $ws $canvasUuid $scene
            if ($actual) { $kitToObs[$scene] = $actual }
            else { Write-Host "  could not add $scene to Vertical Scenes" }
        }
    }
    else {
        $sceneList = Invoke-Obs $ws "GetSceneList" @{}
        $existing = @(Get-ObsProp $sceneList "scenes") | ForEach-Object { Get-ObsProp $_ "sceneName" }
        if (($existing -contains "Scene") -and -not ($existing -contains "STARTING SOON")) {
            Invoke-Obs $ws "SetSceneName" @{ sceneName = "Scene"; newSceneName = "STARTING SOON" } | Out-Null
        }
        foreach ($scene in $sceneNames) {
            $kitToObs[$scene] = $scene
            if (-not (Test-Scene $ws $scene $null)) {
                Invoke-Obs $ws "CreateScene" @{ sceneName = $scene } | Out-Null
                Write-Host "  scene $scene"
            }
        }
    }

    foreach ($scene in $sceneNames) {
        if (-not $kitToObs.ContainsKey($scene)) { continue }
        $obsScene = [string]$kitToObs[$scene]
        Write-Host $obsScene
        foreach ($item in $sceneItems[$scene]) {
            try {
                $spec = Get-InputSpec $kinds $item
                $sourceName = Get-SourceName $item $sourceNameMap
                if (-not $spec.inputKind) {
                    if ($item.kind -eq "gameaudio") {
                        Write-Host "  skip Audio / Game (this OBS has no Application Audio Capture)"
                        continue
                    }
                    throw "OBS missing source type for $sourceName"
                }
                $enabled = $true
                if ($item.ContainsKey("enabled")) { $enabled = [bool]$item.enabled }
                if (-not (Test-Input $ws $sourceName)) {
                    $createIn = @{
                        sceneName        = $obsScene
                        inputName        = $sourceName
                        inputKind        = $spec.inputKind
                        inputSettings    = $spec.settings
                        sceneItemEnabled = $enabled
                    }
                    if ($canvasUuid) { $createIn["canvasUuid"] = $canvasUuid }
                    Invoke-Obs $ws "CreateInput" $createIn | Out-Null
                    Write-Host "  created $sourceName"
                }
                else {
                    $id = Get-ItemId $ws $obsScene $sourceName $canvasUuid
                    if ($null -eq $id) {
                        $link = @{
                            sceneName        = $obsScene
                            sourceName       = $sourceName
                            sceneItemEnabled = $enabled
                        }
                        if ($canvasUuid) { $link["canvasUuid"] = $canvasUuid }
                        Invoke-Obs $ws "CreateSceneItem" $link | Out-Null
                        Write-Host "  linked $sourceName"
                    }
                    $updateSettings = $false
                    if ($canvasUuid) {
                        if ($item.kind -eq "browser" -or $item.kind -eq "lumia") {
                            if ($sourceNameMap -and $sourceNameMap.ContainsKey($item.name)) {
                                $updateSettings = $true
                            }
                        }
                    }
                    elseif ($item.kind -eq "browser" -or $item.kind -eq "lumia") {
                        $updateSettings = $true
                    }
                    if ($updateSettings) {
                        Invoke-Obs $ws "SetInputSettings" @{
                            inputName     = $sourceName
                            inputSettings = $spec.settings
                            overlay       = $true
                        } | Out-Null
                    }
                }
                $id = Get-ItemId $ws $obsScene $sourceName $canvasUuid
                $tf = Get-Transform $item
                if ($null -ne $id -and $null -ne $tf) {
                    $tfReq = @{
                        sceneName          = $obsScene
                        sceneItemId        = $id
                        sceneItemTransform = $tf
                    }
                    if ($canvasUuid) { $tfReq["canvasUuid"] = $canvasUuid }
                    Invoke-Obs $ws "SetSceneItemTransform" $tfReq | Out-Null
                }
                if ($null -ne $id -and -not $enabled) {
                    $enReq = @{
                        sceneName        = $obsScene
                        sceneItemId      = $id
                        sceneItemEnabled = $false
                    }
                    if ($canvasUuid) { $enReq["canvasUuid"] = $canvasUuid }
                    Invoke-Obs $ws "SetSceneItemEnabled" $enReq | Out-Null
                }
            }
            catch {
                Write-Host ("  " + $item.name + " failed: " + $_.Exception.Message)
            }
        }
        $order = @($sceneItems[$scene] | ForEach-Object { Get-SourceName $_ $sourceNameMap })
        for ($i = 0; $i -lt $order.Count; $i++) {
            $id = Get-ItemId $ws $obsScene $order[$i] $canvasUuid
            if ($null -ne $id) {
                $idxReq = @{
                    sceneName      = $obsScene
                    sceneItemId    = $id
                    sceneItemIndex = $i
                }
                if ($canvasUuid) { $idxReq["canvasUuid"] = $canvasUuid }
                try { Invoke-Obs $ws "SetSceneItemIndex" $idxReq | Out-Null } catch {}
            }
        }
    }

    if (-not $canvasUuid) {
        try { Invoke-Obs $ws "SetCurrentSceneTransition" @{ transitionName = "Fade" } | Out-Null } catch {}
        try { Invoke-Obs $ws "SetCurrentSceneTransitionDuration" @{ transitionDuration = 300 } | Out-Null } catch {}
    }
    $first = [string]$kitToObs[$sceneNames[0]]
    if ($first) {
        $prog = @{ sceneName = $first }
        if ($canvasUuid) { $prog["canvasUuid"] = $canvasUuid }
        try { Invoke-Obs $ws "SetCurrentProgramScene" $prog | Out-Null } catch {}
    }
}

$aitumSourceMap = @{
    "Overlay / Starting Soon" = "Overlay / Starting Soon V"
    "Overlay / Grid HUD"      = "Overlay / Grid HUD V"
    "Overlay / Desk HUD"      = "Overlay / Desk HUD V"
    "Overlay / Race HUD"      = "Overlay / Race HUD V"
    "Overlay / Dual HUD"      = "Overlay / Dual HUD V"
    "Overlay / Replay HUD"    = "Overlay / Replay HUD V"
    "Overlay / BRB"           = "Overlay / BRB V"
    "Overlay / Ending"        = "Overlay / Ending V"
    "Lumia / Overlay"         = "Lumia / Overlay V"
    "Color / Backdrop"        = "Color / Backdrop V"
}

function Get-AitumCanvasUuid($ws) {
    $list = Try-Obs $ws "GetCanvasList" @{}
    if ($null -eq $list) { return $null }
    $canvases = @(Get-ObsProp $list "canvases")
    $fallback = $null
    foreach ($c in $canvases) {
        $flags = Get-ObsProp $c "canvasFlags"
        $isMain = $false
        if ($null -ne $flags) {
            $isMain = [bool](Get-ObsProp $flags "main")
        }
        $name = [string](Get-ObsProp $c "canvasName")
        $uuid = [string](Get-ObsProp $c "canvasUuid")
        $vs = Get-ObsProp $c "canvasVideoSettings"
        $w = 0
        $h = 0
        if ($null -ne $vs) {
            $w = [int](Get-ObsProp $vs "baseWidth")
            $h = [int](Get-ObsProp $vs "baseHeight")
        }
        if (-not $uuid) { continue }
        if ($isMain) { continue }
        Write-Host ("  canvas " + $name + " " + $w + "x" + $h)
        if (($w -eq 1080 -and $h -eq 1920) -or ($name -match "Vertical|Aitum|vertical")) {
            return $uuid
        }
        if (-not $fallback) { $fallback = $uuid }
    }
    return $fallback
}

function Install-AitumVertical($ws, $kinds) {
    Write-Host ""
    Write-Host "Aitum Vertical Scenes (phone dock)..."
    $vendor = Try-Obs $ws "CallVendorRequest" @{
        vendorName  = "aitum-vertical-canvas"
        requestType = "version"
        requestData = @{}
    }
    $uuid = Get-AitumCanvasUuid $ws
    if (-not $uuid) {
        if ($vendor) {
            Write-Host "Aitum Vertical is installed, but this OBS cannot create scenes on that canvas from here."
            Write-Host "Update OBS Studio to 32.1 or newer, keep Aitum Vertical, then run tools\Install-AitumVertical.bat"
        }
        else {
            Write-Host "No Aitum Vertical canvas found. Install Aitum Vertical, reopen OBS,"
            Write-Host "Docks -> tick Vertical Scenes, then run tools\Install-AitumVertical.bat"
        }
        return $false
    }
    $savedW = $script:canvasW
    $savedH = $script:canvasH
    $savedOverlays = $script:overlayFiles
    $script:canvasW = 1080
    $script:canvasH = 1920
    $script:overlayFiles = $verticalOverlayFiles
    try {
        Install-RiseScenes $ws $kinds $scenes $verticalItems $uuid $aitumSourceMap
        Ping-SceneCollection $ws
        $have = @(Get-VendorAitumSceneNames $ws)
        Write-Host "Vertical Scenes dock:"
        if ($have.Count -eq 0) {
            Write-Host "  (Aitum did not report names. Switch collection away and back, or restart OBS.)"
        }
        foreach ($n in $have) { Write-Host "  - $n" }
        if ($have.Count -lt 2) {
            Write-Host "If you still only see STARTING SOON: in Vertical Scenes click + and add GRID V, DESK V, RACE V, REPLAY V, BRB V, ENDING V."
            Write-Host "OBS will not allow those names if they already exist on the left list, so name them GRID V, DESK V, RACE V, ..."
        }
    }
    finally {
        $script:canvasW = $savedW
        $script:canvasH = $savedH
        $script:overlayFiles = $savedOverlays
    }
    Write-Host "Vertical Scenes should now list STARTING SOON, GRID, DESK, RACE, RACE DUAL, REPLAY, BRB, ENDING (or ... V names)."
    Write-Host "In Vertical Scenes, right-click each name -> Linked Scenes -> tick the matching wide scene (DESK V -> DESK, RACE V -> RACE)."
    return $true
}

function Install-RiseAudio($ws) {
    Write-Host "Audio: mute Desktop so Discord is not on the stream"
    $special = Invoke-Obs $ws "GetSpecialInputs" @{}
    foreach ($key in @("desktop1", "desktop2")) {
        $name = Get-ObsProp $special $key
        if ($name) {
            try {
                Invoke-Obs $ws "SetInputMute" @{ inputName = $name; inputMuted = $true } | Out-Null
                Write-Host "  muted $name"
            }
            catch {}
        }
    }
    $mic1 = Get-ObsProp $special "mic1"
    if ($mic1 -and $mic1 -ne "Mic / Main") {
        try {
            Invoke-Obs $ws "SetInputName" @{ inputName = $mic1; newInputName = "Mic / Main" } | Out-Null
            Write-Host "  mic is Mic / Main"
        }
        catch {}
    }
    $hasGameAudio = Test-Input $ws "Audio / Game"
    foreach ($gameName in @("Game / Main", "Game / Angle 2")) {
        if (-not (Test-Input $ws $gameName)) { continue }
        try {
            Invoke-Obs $ws "SetInputSettings" @{
                inputName     = $gameName
                inputSettings = @{ capture_audio = (-not $hasGameAudio) }
                overlay       = $true
            } | Out-Null
        }
        catch {}
    }
    if ($hasGameAudio) {
        try {
            Invoke-Obs $ws "SetInputAudioMonitorType" @{ inputName = "Audio / Game"; monitorType = "OBS_MONITORING_TYPE_NONE" } | Out-Null
        }
        catch {}
        try {
            Invoke-Obs $ws "SetInputMute" @{ inputName = "Audio / Game"; inputMuted = $false } | Out-Null
        }
        catch {}
    }
    if ($mic1) {
        $micName = "Mic / Main"
        if (-not (Test-Input $ws $micName)) { $micName = $mic1 }
        try {
            Invoke-Obs $ws "SetInputMute" @{ inputName = $micName; inputMuted = $false } | Out-Null
        }
        catch {}
    }
}

if (-not $AitumOnly) {
    Write-Host 'Wide 1920x1080...'
    Use-RiseCollection $ws $collectionName
    Set-RiseCanvas $ws 1920 1080
    Install-RiseScenes $ws $kinds $scenes $items
    Install-RiseAudio $ws

    Write-Host 'Vertical 1080x1920...'
    $script:overlayFiles = $verticalOverlayFiles
    Use-RiseCollection $ws $verticalCollectionName
    Set-RiseCanvas $ws 1080 1920
    Install-RiseScenes $ws $kinds $scenes $verticalItems
    Install-RiseAudio $ws
}

Use-RiseCollection $ws $collectionName
Set-RiseCanvas $ws 1920 1080
$aitumOk = $false
try {
    $aitumOk = [bool](Install-AitumVertical $ws $kinds)
}
catch {
    Write-Host ("Aitum Vertical install skipped: " + $_.Exception.Message)
}

$ws.Dispose()

Write-Host ""
Write-Host 'Done. Look at OBS.' -ForegroundColor Green
if (-not $AitumOnly) {
    Write-Host 'Two scene collections (dropdown at the top of OBS):'
    Write-Host '  Rise Above BeamNG            = 1920x1080 Twitch / YouTube / Kick'
    Write-Host '  Rise Above BeamNG Vertical  = 1080x1920 phone-only if you are not using Aitum'
    Write-Host 'Same scene names in both: STARTING SOON, GRID, DESK, RACE, ...'
}
Write-Host ""
Write-Host 'Stay on collection Rise Above BeamNG for Aitum Multi + Vertical.'
if ($aitumOk) {
    Write-Host 'Vertical Scenes dock should now have the eight phone scenes.'
    Write-Host 'Right-click each one -> Linked Scenes -> tick the matching wide scene.'
}
else {
    Write-Host 'If Vertical Scenes is still empty: install Aitum Vertical, reopen OBS,'
    Write-Host 'then double-click tools\Install-AitumVertical.bat'
}
Write-Host ""
Write-Host 'Next: click RACE, double-click Game / Main, pick BeamNG.'
Write-Host 'Other games (no wheel cams): click DESK, then pick that game on Game / Main and Audio / Game.'
Write-Host 'Audio: Desktop Audio is muted so Discord is not on stream.'
Write-Host '  Mixer: Mic / Main = your mic. Audio / Game = double-click and pick BeamNG.drive (or the other game on DESK).'
Write-Host 'Cameras can wait.'
Write-Host 'Chat for you: tools\Open-ChatForYou.bat  (not on the stream).'
Write-Host 'See docs\aitum.html'
