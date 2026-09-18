#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$kitRoot = Split-Path -Parent $PSScriptRoot
$listFile = Join-Path $kitRoot "tools\downloads.json"
$dest = Join-Path $kitRoot "installers"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$items = Get-Content $listFile -Raw | ConvertFrom-Json
Write-Host ""
Write-Host "Downloading Windows installers into:"
Write-Host "  $dest"
Write-Host ""

foreach ($item in $items) {
  if (-not $item.url) { continue }
  $out = Join-Path $dest $item.file
  Write-Host ("- {0}" -f $item.name)
  try {
    Invoke-WebRequest -Uri $item.url -OutFile $out -UseBasicParsing
    Write-Host ("    saved {0}" -f $item.file) -ForegroundColor Green
  } catch {
    Write-Host ("    FAILED: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
    if ($item.page) {
      Write-Host ("    open: {0}" -f $item.page)
      Start-Process $item.page
    }
  }
}

Write-Host ""
Write-Host "Close OBS, then run the .exe files in the installers folder."
Write-Host "Aitum Stream Suite covers Multistream + Vertical. Do not also install Restream."
Write-Host "Lumia is a separate app - install it from the page that opened if the file is missing."
Write-Host ""
Start-Process $dest
