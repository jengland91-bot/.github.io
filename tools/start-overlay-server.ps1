#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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
Write-Host "Rise Above - TikTok LIVE Studio layout" -ForegroundColor White
Write-Host "Serving: $repoRoot"
Write-Host "Keep this window open while you are live on TikTok."
Write-Host "TikTok is LIVE Studio only. Do not open OBS for TikTok."
Write-Host ""
Write-Host "Turn Dual layout ON. Add sources on the PHONE canvas first."
Write-Host "Then switch to landscape and resize the SAME sources. One overlay URL per scene."
Write-Host ""
Write-Host "Layout board: ${prefix}tiktok-studio/"
Write-Host ""
Write-Host "PHONE overlay Links (1080 x 1920), then stretch that same Link to 1920 x 1080 on landscape:"
Write-Host "  STARTING SOON  ${prefix}overlays/vertical/starting-soon.html?m=5"
Write-Host "  GRID           ${prefix}overlays/vertical/chatting.html"
Write-Host "  DESK           ${prefix}overlays/vertical/desk.html"
Write-Host "  RACE           ${prefix}overlays/vertical/live.html"
Write-Host "  RACE DUAL      ${prefix}overlays/vertical/race-dual.html"
Write-Host "  REPLAY         ${prefix}overlays/vertical/replay.html"
Write-Host "  BRB            ${prefix}overlays/vertical/brb.html"
Write-Host "  ENDING         ${prefix}overlays/vertical/ending.html"
Write-Host ""
Write-Host "Setup boxes:  ${prefix}overlays/vertical/live.html?setup=1"
Write-Host "Guide:        ${prefix}docs/tiktok.html"
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
try { Start-Process "${prefix}tiktok-studio/" } catch {}

while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response
    try {
        $rel = [Uri]::UnescapeDataString($req.Url.AbsolutePath.TrimStart("/"))
        if ([string]::IsNullOrWhiteSpace($rel)) { $rel = "tiktok-studio/index.html" }
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
