#!/usr/bin/env bash
# Zip contents for BeamNG mods folder (zip root = scripts/ lua/ ui/)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$ROOT/../courseBuilderHud.zip}"
cd "$ROOT"
zip -r "$OUT" scripts lua ui README.md -x "*.DS_Store" -x "pack-mod.sh"
echo "Wrote $OUT"
