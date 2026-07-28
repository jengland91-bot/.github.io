# Fix BeamNG levels folder for California 300
# Run this in PowerShell on your PC.

$levels = Join-Path $env:LOCALAPPDATA "BeamNG\BeamNG.drive\current\levels"
$target = Join-Path $levels "california_300"

Write-Host "Levels folder: $levels"

if (-not (Test-Path $levels)) {
  Write-Host "ERROR: levels folder not found."
  exit 1
}

New-Item -ItemType Directory -Force -Path $target | Out-Null

# Move loose level files that were dumped into /levels into california_300
$names = @(
  "art",
  "import",
  "main",
  "info.json",
  "map.json",
  "theTerrain.ter",
  "theTerrain.terrain.json",
  "main.decals.json",
  "main.forestbrushes.json",
  ".forest.json",
  ".ter.depth.png",
  "_preview.png",
  "preview.png"
)

foreach ($name in $names) {
  $src = Join-Path $levels $name
  $dst = Join-Path $target $name
  if (Test-Path $src) {
    if (Test-Path $dst) {
      Write-Host "Skip (already exists): $name"
    } else {
      Move-Item -Path $src -Destination $dst
      Write-Host "Moved: $name"
    }
  }
}

Write-Host ""
Write-Host "Done. Your level should now be at:"
Write-Host $target
Write-Host ""
Write-Host "Next in BeamNG:"
Write-Host "1) F11"
Write-Host "2) File -> Open Level -> california_300"
Write-Host "3) Terrain -> Heightmap Import"
Write-Host "4) Import heightmap_4096.png"
Write-Host "5) squareSize=4 , maxHeight=900"
Write-Host "6) Save"
