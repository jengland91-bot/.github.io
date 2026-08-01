#!/usr/bin/env bash
# Rebuild Parker 400 map data + HD heightmap + shipped 4096.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/convert_p400_to_map.py
# USGS 3DEP = MapNG's US elevation source (real hills / washes for full loop)
python3 scripts/bake_usgs_heightmap.py
python3 scripts/prepare_hd_materials.py
python3 scripts/bake_silt_shoulder.py
python3 scripts/bake_dirt_road.py
python3 scripts/bake_esri_satellite.py
python3 scripts/bake_level.py
python3 scripts/bake_ter.py
python3 scripts/bake_minimap.py
python3 scripts/pack_mod_zip.py
echo "Rebuild complete."
