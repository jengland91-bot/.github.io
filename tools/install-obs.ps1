#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Net.WebSockets.Client

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$overlayDir = Join-Path $repoRoot "overlays"

Write-Host ""
Write-Host "Rise Above — push scenes into OBS" -ForegroundColor White
Write-Host ""

if (-not (Test-Path (Join-Path $overlayDir "live.html"))) {
    Write-Host "Cannot find overlays\live.html" -ForegroundColor Red
    Write-Host "You must EXTRACT the zip, then run Install-OBS.bat from the tools folder inside that extracted folder."
    Write-Host "Looked in: $overlayDir"
    exit 1
}

Write-Host "Overlay folder: $overlayDir"
Write-Host ""
Write-Host "OBS must be open. Top menu: Tools -> WebSocket Server Settings -> Enable."
Write-Host "Copy the password from Show Connect Info."
Write-Host ""
$password = Read-Host "Paste OBS WebSocket password"

$css = "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }"
$collectionName = "Rise Above BeamNG"
$overlaySlash = ($overlayDir -replace "\\", "/")

$scenes = @(
    "STARTING SOON", "GRID", "RACE", "RACE DUAL", "REPLAY", "BRB", "ENDING"
)

$overlayFiles = @{
    "Overlay / Starting Soon" = @{ File = "starting-soon.html"; Shutdown = $true; Restart = $true }
    "Overlay / Grid HUD"      = @{ File = "chatting.html"; Shutdown = $false; Restart = $false }
    "Overlay / Race HUD"      = @{ File = "live.html"; Shutdown = $false; Restart = $false }
    "Overlay / Dual HUD"      = @{ File = "race-dual.html"; Shutdown = $false; Restart = $false }
    "Overlay / Replay HUD"    = @{ File = "replay.html"; Shutdown = $false; Restart = $false }
    "Overlay / BRB"           = @{ File = "brb.html"; Shutdown = $true; Restart = $true }
    "Overlay / Ending"        = @{ File = "ending.html"; Shutdown = $true; Restart = $true }
}

$items = @{
    "STARTING SOON" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Overlay / Starting Soon"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
    )
    "GRID" = @(
        @{ name = "Color / Backdrop"; kind = "color" }
        @{ name = "Cam / Face"; kind = "camera"; x = 48; y = 168; w = 960; h = 540 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 1032; y = 168; w = 840; h = 473 }
        @{ name = "Overlay / Grid HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
    )
    "RACE" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Cam / Face"; kind = "camera"; x = 48; y = 816; w = 400; h = 225 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 464; y = 816; w = 400; h = 225 }
        @{ name = "Overlay / Race HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Media / Hype Clip"; kind = "media"; x = 0; y = 0; w = 1920; h = 1080; enabled = $false }
    )
    "RACE DUAL" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Game / Angle 2"; kind = "game"; x = 1248; y = 48; w = 640; h = 360 }
        @{ name = "Cam / Face"; kind = "camera"; x = 48; y = 860; w = 320; h = 180 }
        @{ name = "Cam / Wheel"; kind = "camera"; x = 384; y = 860; w = 320; h = 180 }
        @{ name = "Overlay / Dual HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
    )
    "REPLAY" = @(
        @{ name = "Game / Main"; kind = "game"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Overlay / Replay HUD"; kind = "browser"; x = 0; y = 0; w = 1920; h = 1080 }
        @{ name = "Lumia / Overlay"; kind = "lumia"; x = 0; y = 0; w = 1920; h = 1080 }
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
        if ([string]$msg.d.requestId -ne $id) { continue }
        if (-not $msg.d.requestStatus.result) {
            $comment = $msg.d.requestStatus.comment
            throw "$type failed: $comment"
        }
        return $msg.d.responseData
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
    if ($name -eq "Lumia / Overlay") {
        return @{
            is_local_file        = $false
            url                  = "about:blank"
            width                = 1920
            height               = 1080
            fps                  = 30
            fps_custom           = $true
            css                  = $css
            shutdown             = $false
            restart_when_active  = $false
        }
    }
    $meta = $overlayFiles[$name]
    $path = "$overlaySlash/$($meta.File)"
    return @{
        is_local_file        = $true
        local_file           = $path
        width                = 1920
        height               = 1080
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
                settings  = @{ color = 4278978567; width = 1920; height = 1080 }
            }
        }
        "game" {
            if ($item.name -eq "Game / Angle 2") {
                return @{
                    inputKind = (Get-Kind $kinds @("window_capture", "game_capture"))
                    settings  = @{ cursor = $false; capture_cursor = $false }
                }
            }
            return @{
                inputKind = (Get-Kind $kinds @("game_capture", "window_capture"))
                settings  = @{ capture_mode = "any"; capture_cursor = $false }
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
$ws = [System.Net.WebSockets.ClientWebSocket]::new()
$ws.Options.KeepAliveInterval = [TimeSpan]::FromSeconds(20)

Write-Host "Connecting to OBS on this PC..."
try {
    $connect = $ws.ConnectAsync([Uri]"ws://127.0.0.1:4455/", [System.Threading.CancellationToken]::None)
    if (-not $connect.Wait(5000)) { throw "timed out" }
    if ($connect.IsFaulted) { throw $connect.Exception.InnerException }
}
catch {
    Write-Host ""
    Write-Host "Could not reach OBS." -ForegroundColor Red
    Write-Host "1. Open OBS Studio"
    Write-Host "2. Top bar: Tools  (File, Edit, Tools, Help)"
    Write-Host "3. WebSocket Server Settings -> Enable WebSocket server"
    Write-Host "4. Run this bat again"
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

$identified = Receive-Obs $ws
if ($identified.op -ne 2) {
    Write-Host "OBS rejected the password. Copy it from Tools -> WebSocket Server Settings -> Show Connect Info." -ForegroundColor Red
    exit 1
}

Write-Host "Connected." -ForegroundColor Green

$ver = Invoke-Obs $ws "GetVersion" @{}
Write-Host ("OBS " + $ver.obsVersion)

$kindList = Invoke-Obs $ws "GetInputKindList" @{ unversioned = $false }
$kinds = @($kindList.inputKinds)

$cols = Invoke-Obs $ws "GetSceneCollectionList" @{}
$colNames = @($cols.sceneCollections)
if ($colNames -contains $collectionName) {
    Invoke-Obs $ws "SetCurrentSceneCollection" @{ sceneCollectionName = $collectionName } | Out-Null
    Write-Host "Using existing collection $collectionName"
}
else {
    Invoke-Obs $ws "CreateSceneCollection" @{ sceneCollectionName = $collectionName } | Out-Null
    Write-Host "Created collection $collectionName"
}

Invoke-Obs $ws "SetVideoSettings" @{
    baseWidth      = 1920
    baseHeight     = 1080
    outputWidth    = 1920
    outputHeight   = 1080
    fpsNumerator   = 60
    fpsDenominator = 1
} | Out-Null

$sceneList = Invoke-Obs $ws "GetSceneList" @{}
$sceneNames = @($sceneList.scenes | ForEach-Object { $_.sceneName })
if (($sceneNames -contains "Scene") -and -not ($sceneNames -contains "STARTING SOON")) {
    Invoke-Obs $ws "SetSceneName" @{ sceneName = "Scene"; newSceneName = "STARTING SOON" } | Out-Null
}

function Test-Scene($ws, $name) {
    $list = Invoke-Obs $ws "GetSceneList" @{}
    return (@($list.scenes | ForEach-Object { $_.sceneName }) -contains $name)
}

function Test-Input($ws, $name) {
    $list = Invoke-Obs $ws "GetInputList" @{}
    return (@($list.inputs | ForEach-Object { $_.inputName }) -contains $name)
}

function Get-ItemId($ws, $scene, $source) {
    $list = Invoke-Obs $ws "GetSceneItemList" @{ sceneName = $scene }
    $hit = @($list.sceneItems | Where-Object { $_.sourceName -eq $source } | Select-Object -First 1)
    if ($hit) { return [int]$hit.sceneItemId }
    return $null
}

foreach ($scene in $scenes) {
    if (-not (Test-Scene $ws $scene)) {
        Invoke-Obs $ws "CreateScene" @{ sceneName = $scene } | Out-Null
        Write-Host "  scene $scene"
    }
}

foreach ($scene in $scenes) {
    Write-Host $scene
    foreach ($item in $items[$scene]) {
        $spec = Get-InputSpec $kinds $item
        if (-not $spec.inputKind) { throw "OBS missing source type for $($item.name)" }
        $enabled = $true
        if ($item.ContainsKey("enabled")) { $enabled = [bool]$item.enabled }
        if (-not (Test-Input $ws $item.name)) {
            Invoke-Obs $ws "CreateInput" @{
                sceneName         = $scene
                inputName         = $item.name
                inputKind         = $spec.inputKind
                inputSettings     = $spec.settings
                sceneItemEnabled  = $enabled
            } | Out-Null
            Write-Host "  created $($item.name)"
        }
        else {
            $id = Get-ItemId $ws $scene $item.name
            if ($null -eq $id) {
                Invoke-Obs $ws "CreateSceneItem" @{
                    sceneName         = $scene
                    sourceName        = $item.name
                    sceneItemEnabled  = $enabled
                } | Out-Null
                Write-Host "  linked $($item.name)"
            }
            if ($item.kind -eq "browser" -or $item.kind -eq "lumia") {
                Invoke-Obs $ws "SetInputSettings" @{
                    inputName     = $item.name
                    inputSettings = $spec.settings
                    overlay       = $true
                } | Out-Null
            }
        }
        $id = Get-ItemId $ws $scene $item.name
        $tf = Get-Transform $item
        if ($null -ne $id -and $null -ne $tf) {
            Invoke-Obs $ws "SetSceneItemTransform" @{
                sceneName           = $scene
                sceneItemId         = $id
                sceneItemTransform  = $tf
            } | Out-Null
        }
        if ($null -ne $id -and -not $enabled) {
            Invoke-Obs $ws "SetSceneItemEnabled" @{
                sceneName        = $scene
                sceneItemId      = $id
                sceneItemEnabled = $false
            } | Out-Null
        }
    }
    $order = @($items[$scene] | ForEach-Object { $_.name })
    for ($i = 0; $i -lt $order.Count; $i++) {
        $id = Get-ItemId $ws $scene $order[$i]
        if ($null -ne $id) {
            Invoke-Obs $ws "SetSceneItemIndex" @{
                sceneName      = $scene
                sceneItemId    = $id
                sceneItemIndex = $i
            } | Out-Null
        }
    }
}

try { Invoke-Obs $ws "SetCurrentSceneTransition" @{ transitionName = "Fade" } | Out-Null } catch {}
try { Invoke-Obs $ws "SetCurrentSceneTransitionDuration" @{ transitionDuration = 300 } | Out-Null } catch {}
Invoke-Obs $ws "SetCurrentProgramScene" @{ sceneName = "STARTING SOON" } | Out-Null

$ws.Dispose()

Write-Host ""
Write-Host "Done. Look at OBS." -ForegroundColor Green
Write-Host "Top of the OBS window: scene collection should say  Rise Above BeamNG"
Write-Host "Scenes on the left: STARTING SOON, GRID, RACE, ..."
Write-Host ""
Write-Host "Next: click RACE, double-click Game / Main, pick BeamNG."
Write-Host "Cameras can wait."
