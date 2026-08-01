#!/usr/bin/env bash
# Rebuild Parker 400 map data + HD heightmap + shipped 4096.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/convert_p400_to_map.py
python3 scripts/bake_srtm_heightmap.py
python3 - <<'PY'
import struct, zlib, numpy as np
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from pngio import write_png16_gray

def load_png16(path):
    data = Path(path).read_bytes()
    pos = 8
    w = h = None
    raw = b""
    while pos < len(data):
        ln = int.from_bytes(data[pos:pos+4], "big")
        tag = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+ln]
        pos += 12 + ln
        if tag == b"IHDR":
            w, h = struct.unpack(">II", chunk[:8])
        elif tag == b"IDAT":
            raw += chunk
        elif tag == b"IEND":
            break
    dec = zlib.decompress(raw)
    arr = np.empty((h, w), dtype=np.uint16)
    stride = 1 + w * 2
    for y in range(h):
        arr[y] = np.frombuffer(dec[y*stride+1:(y+1)*stride], dtype=">u2")
    return arr

src = load_png16(Path("import/heightmap_8192.png"))
h, w = src.shape
ds = src.reshape(h//2, 2, w//2, 2).mean(axis=(1, 3)).astype(np.uint16)
write_png16_gray(Path("import/heightmap_4096.png"), ds)
write_png16_gray(Path("levels/parker_400/import/heightmap_4096.png"), ds)
print("wrote heightmap_4096.png")
PY
python3 scripts/prepare_hd_materials.py
python3 scripts/bake_level.py
python3 scripts/bake_ter.py
echo "Rebuild complete."
