#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$kitRoot = Split-Path -Parent $PSScriptRoot
$prefix = "http://127.0.0.1:8765/"
$nowFile = Join-Path $kitRoot "overlays\shared\now.json"

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
}

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add($prefix)
try {
  $listener.Start()
} catch {
  Write-Host "Port 8765 is already in use — opening tonight setup anyway."
  Start-Process ($prefix + "overlays/tonight.html")
  exit 0
}

Write-Host ""
Write-Host " Kit server: $prefix"
Write-Host " Tonight:    $($prefix)overlays/tonight.html"
Write-Host " Control:    $($prefix)overlays/control.html"
Write-Host " Keep this window open."
Write-Host ""
Start-Process ($prefix + "overlays/tonight.html")

while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  $req = $ctx.Request
  $res = $ctx.Response
  try {
    if ($req.HttpMethod -eq "POST" -and ($req.Url.AbsolutePath -eq "/now" -or $req.Url.AbsolutePath -eq "/overlays/shared/now.json")) {
      $reader = New-Object System.IO.StreamReader($req.InputStream, $req.ContentEncoding)
      $body = $reader.ReadToEnd()
      $reader.Close()
      [System.IO.File]::WriteAllText($nowFile, $body, [System.Text.UTF8Encoding]::new($false))
      $bytes = [Text.Encoding]::UTF8.GetBytes('{"ok":true}')
      $res.ContentType = "application/json"
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $path = [Uri]::UnescapeDataString($req.Url.AbsolutePath.TrimStart("/"))
      if ([string]::IsNullOrWhiteSpace($path)) { $path = "overlays/tonight.html" }
      $full = [IO.Path]::GetFullPath((Join-Path $kitRoot $path))
      if (-not $full.StartsWith($kitRoot, [StringComparison]::OrdinalIgnoreCase)) {
        $res.StatusCode = 403
      } elseif (-not (Test-Path $full)) {
        $res.StatusCode = 404
        $bytes = [Text.Encoding]::UTF8.GetBytes("not found")
        $res.OutputStream.Write($bytes, 0, $bytes.Length)
      } else {
        $ext = [IO.Path]::GetExtension($full).ToLowerInvariant()
        $res.ContentType = $(if ($mime.ContainsKey($ext)) { $mime[$ext] } else { "application/octet-stream" })
        $bytes = [IO.File]::ReadAllBytes($full)
        $res.OutputStream.Write($bytes, 0, $bytes.Length)
      }
    }
  } catch {
    $res.StatusCode = 500
  } finally {
    $res.Close()
  }
}
