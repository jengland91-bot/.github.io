#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$kitRoot = Split-Path -Parent $PSScriptRoot
$nowFile = Join-Path $kitRoot "overlays\shared\now.json"
$port = 8765
$prefix = "http://127.0.0.1:$port/"
$loadUrl = $prefix + "overlays/install.html?load=1"

$mime = @{
  ".html" = "text/html; charset=utf-8"
  ".js"   = "application/javascript; charset=utf-8"
  ".css"  = "text/css; charset=utf-8"
  ".json" = "application/json; charset=utf-8"
  ".png"  = "image/png"
  ".svg"  = "image/svg+xml"
  ".txt"  = "text/plain; charset=utf-8"
  ".bat"  = "text/plain; charset=utf-8"
  ".md"   = "text/plain; charset=utf-8"
  ".ico"  = "image/x-icon"
}

function Get-ContentType([string]$path) {
  $ext = [IO.Path]::GetExtension($path).ToLowerInvariant()
  if ($mime.ContainsKey($ext)) { return $mime[$ext] }
  return "application/octet-stream"
}

function Read-Request([System.Net.Sockets.NetworkStream]$stream) {
  $ms = New-Object System.IO.MemoryStream
  $buf = New-Object byte[] 4096
  while ($true) {
    if (-not $stream.DataAvailable -and $ms.Length -gt 0) { break }
    $read = $stream.Read($buf, 0, $buf.Length)
    if ($read -le 0) { break }
    $ms.Write($buf, 0, $read)
    $text = [Text.Encoding]::ASCII.GetString($ms.ToArray())
    if ($text.Contains("`r`n`r`n")) { break }
    if ($ms.Length -gt 1024 * 1024) { break }
  }
  return $ms.ToArray()
}

function Send-Response([System.Net.Sockets.NetworkStream]$stream, [int]$status, [string]$contentType, [byte[]]$body) {
  if ($null -eq $body) { $body = New-Object byte[] 0 }
  $reason = switch ($status) {
    200 { "OK" }
    403 { "Forbidden" }
    404 { "Not Found" }
    default { "Error" }
  }
  $header = "HTTP/1.1 $status $reason`r`nContent-Type: $contentType`r`nContent-Length: $($body.Length)`r`nConnection: close`r`n`r`n"
  $headerBytes = [Text.Encoding]::ASCII.GetBytes($header)
  $stream.Write($headerBytes, 0, $headerBytes.Length)
  if ($body.Length -gt 0) { $stream.Write($body, 0, $body.Length) }
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
try {
  $listener.Start()
} catch {
  Write-Host "Could not bind port $port : $($_.Exception.Message)"
  Write-Host "Trying to open the loader anyway..."
  Start-Process $loadUrl
  exit 1
}

Write-Host ""
Write-Host " Kit server: $prefix"
Write-Host " Load scenes: $loadUrl"
Write-Host " Keep this window open."
Write-Host ""
Start-Process $loadUrl

while ($true) {
  $client = $listener.AcceptTcpClient()
  try {
    $stream = $client.GetStream()
    $stream.ReadTimeout = 5000
    $raw = Read-Request $stream
    if ($null -eq $raw -or $raw.Length -eq 0) { continue }
    $reqText = [Text.Encoding]::ASCII.GetString($raw)
    $lines = $reqText -split "`r`n"
    $requestLine = $lines[0]
    $parts = $requestLine -split " "
    if ($parts.Length -lt 2) {
      Send-Response $stream 400 "text/plain; charset=utf-8" ([Text.Encoding]::UTF8.GetBytes("bad request"))
      continue
    }
    $method = $parts[0]
    $urlPath = $parts[1]
    if ($urlPath.StartsWith("http")) {
      try { $urlPath = [Uri]$urlPath | ForEach-Object { $_.AbsolutePath + $_.Query } } catch { $urlPath = "/" }
    }
    $pathOnly = $urlPath.Split("?")[0]
    if ([string]::IsNullOrWhiteSpace($pathOnly) -or $pathOnly -eq "/") {
      $pathOnly = "/overlays/install.html"
    }

    if ($method -eq "POST" -and ($pathOnly -eq "/now" -or $pathOnly -eq "/overlays/shared/now.json")) {
      $headerEnd = $reqText.IndexOf("`r`n`r`n")
      $bodyBytes = New-Object byte[] 0
      if ($headerEnd -ge 0) {
        $start = $headerEnd + 4
        if ($start -lt $raw.Length) {
          $len = $raw.Length - $start
          $bodyBytes = New-Object byte[] $len
          [Array]::Copy($raw, $start, $bodyBytes, 0, $len)
        }
      }
      [IO.File]::WriteAllBytes($nowFile, $bodyBytes)
      Send-Response $stream 200 "application/json" ([Text.Encoding]::UTF8.GetBytes('{"ok":true}'))
      continue
    }

    $rel = [Uri]::UnescapeDataString($pathOnly.TrimStart("/"))
    $full = [IO.Path]::GetFullPath((Join-Path $kitRoot $rel))
    if (-not $full.StartsWith($kitRoot, [StringComparison]::OrdinalIgnoreCase)) {
      Send-Response $stream 403 "text/plain; charset=utf-8" ([Text.Encoding]::UTF8.GetBytes("forbidden"))
    } elseif (-not (Test-Path -LiteralPath $full)) {
      Send-Response $stream 404 "text/plain; charset=utf-8" ([Text.Encoding]::UTF8.GetBytes("not found"))
    } else {
      $bytes = [IO.File]::ReadAllBytes($full)
      Send-Response $stream 200 (Get-ContentType $full) $bytes
    }
  } catch {
    Write-Host ("request error: {0}" -f $_.Exception.Message)
  } finally {
    try { $client.Close() } catch {}
  }
}
