#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
Write-Host ""
Write-Host "Rise Above overlay server starting..."

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$overlayDir = Join-Path $repoRoot "overlays"
$port = 5500
$prefix = "http://127.0.0.1:$port/"

if (-not (Test-Path (Join-Path $overlayDir "vertical\live.html"))) {
    Write-Host "Cannot find overlays\vertical\live.html" -ForegroundColor Red
    Write-Host "EXTRACT the zip, then run Start-OverlayServer.bat from the tools folder inside that extracted folder."
    Write-Host "Looked in: $overlayDir"
    exit 1
}
if (-not (Test-Path (Join-Path $overlayDir "live.html"))) {
    Write-Host "Cannot find overlays\live.html" -ForegroundColor Red
    Write-Host "Need overlays\live.html in this zip too."
    Write-Host "Looked in: $overlayDir"
    exit 1
}

Write-Host ""
Write-Host "Rise Above - Meld Studio" -ForegroundColor White
Write-Host "Serving: $repoRoot"
Write-Host "Keep this window open while Meld Browser layers use these URLs."
Write-Host ""
Write-Host "Layout board: ${prefix}meld/"
Write-Host "Apps list:    ${prefix}apps.html"
Write-Host "Guide:        ${prefix}docs/meld.html"
Write-Host "Scenes:       $repoRoot\LOAD-THESE-SCENES"
Write-Host "Drag folder:  $repoRoot\DROP-INTO-MELD"
Write-Host ""
Write-Host "Scenes: double-click 1-OPEN-IN-MELD.bat (it writes them into Meld)."
Write-Host "Backup: File -> Import Session -> LOAD-THESE-SCENES\0 ALL SCENES.json"
Write-Host ""
Write-Host "Main canvas overlays (1920 x 1080):"
Write-Host "  STARTING SOON  ${prefix}overlays/starting-soon.html?m=5"
Write-Host "  GRID           ${prefix}overlays/chatting.html"
Write-Host "  DESK           ${prefix}overlays/desk.html"
Write-Host "  RACE           ${prefix}overlays/live.html"
Write-Host "  RACE DUAL      ${prefix}overlays/race-dual.html"
Write-Host "  REPLAY         ${prefix}overlays/replay.html"
Write-Host "  BRB            ${prefix}overlays/brb.html"
Write-Host "  ENDING         ${prefix}overlays/ending.html"
Write-Host ""
Write-Host "Portrait canvas overlays (1080 x 1920):"
Write-Host "  STARTING SOON  ${prefix}overlays/vertical/starting-soon.html?m=5"
Write-Host "  GRID           ${prefix}overlays/vertical/chatting.html"
Write-Host "  DESK           ${prefix}overlays/vertical/desk.html"
Write-Host "  RACE           ${prefix}overlays/vertical/live.html"
Write-Host "  RACE DUAL      ${prefix}overlays/vertical/race-dual.html"
Write-Host "  REPLAY         ${prefix}overlays/vertical/replay.html"
Write-Host "  BRB            ${prefix}overlays/vertical/brb.html"
Write-Host "  ENDING         ${prefix}overlays/vertical/ending.html"
Write-Host ""
Write-Host "Setup boxes:  ${prefix}overlays/live.html?setup=1"
Write-Host ""

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
try {
    $listener.Start()
}
catch {
    Write-Host "Could not start on port $port. Is another copy already running?" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

function Get-Mime([string]$ext) {
    switch ($ext.ToLowerInvariant()) {
        ".html" { return "text/html; charset=utf-8" }
        ".htm"  { return "text/html; charset=utf-8" }
        ".js"   { return "text/javascript; charset=utf-8" }
        ".css"  { return "text/css; charset=utf-8" }
        ".json" { return "application/json; charset=utf-8" }
        ".txt"  { return "text/plain; charset=utf-8" }
        ".svg"  { return "image/svg+xml" }
        ".png"  { return "image/png" }
        ".jpg"  { return "image/jpeg" }
        ".jpeg" { return "image/jpeg" }
        ".webp" { return "image/webp" }
        ".gif"  { return "image/gif" }
        ".ico"  { return "image/x-icon" }
        ".woff" { return "font/woff" }
        ".woff2"{ return "font/woff2" }
        default { return "application/octet-stream" }
    }
}

Write-Host "Ready. Ctrl+C to stop." -ForegroundColor Green
try { Start-Process "${prefix}meld/" } catch {}
try { Start-Process (Join-Path $repoRoot "LOAD-THESE-SCENES") } catch {}
try { Start-Process "${prefix}apps.html" } catch {}

while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response
    try {
        $rel = [Uri]::UnescapeDataString($req.Url.AbsolutePath.TrimStart("/"))
        if ([string]::IsNullOrWhiteSpace($rel)) { $rel = "meld/index.html" }
        $rel = $rel -replace "/", "\"
        if ($rel.Contains("..")) {
            $res.StatusCode = 400
            $bytes = [Text.Encoding]::UTF8.GetBytes("bad path")
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        else {
            $full = Join-Path $repoRoot $rel
            if ((Test-Path $full) -and (Get-Item $full).PSIsContainer) {
                $full = Join-Path $full "index.html"
            }
            if (-not (Test-Path $full)) {
                $res.StatusCode = 404
                $msg = [Text.Encoding]::UTF8.GetBytes("not found")
                $res.OutputStream.Write($msg, 0, $msg.Length)
            }
            else {
                $bytes = [IO.File]::ReadAllBytes($full)
                $res.ContentType = Get-Mime ([IO.Path]::GetExtension($full))
                $res.ContentLength64 = $bytes.Length
                $res.Headers.Add("Cache-Control", "no-cache")
                $res.OutputStream.Write($bytes, 0, $bytes.Length)
            }
        }
    }
    catch {
        try { $res.StatusCode = 500 } catch {}
    }
    finally {
        try { $res.OutputStream.Close() } catch {}
    }
}
