#!/usr/bin/env python3
"""Bake Esri World Imagery satellite base for the exact Parker 400 map frame.

Pushes the highest practical resolution that still ships under GitHub's 100 MiB
limit: 8192² (~8 m/px) from zoom-14 tiles, written as high-quality JPEG for the
level plus a smaller PNG preview.

Outputs:
  - import/parker400_base_color.jpg / .png (full 8192)
  - levels/parker_400/art/terrains/parker400_base_color.jpg  (shipped)
  - import/parker400_base_color_preview.png
  - /opt/cursor/artifacts/parker400_satellite.png
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
IMPORT = ROOT / "import"
LEVEL_ART = ROOT / "levels" / "parker_400" / "art" / "terrains"

WORLD_M = 65536.0
OUT = 16000  # bake mosaic at ~4.1 m/px (ffmpeg cannot encode full 16384² MJPEG)
SHIP = 12288  # shipped unique sat (~5.3 m/px) — sharp enough, packs under GitHub 100 MiB
ZOOM = 15  # source ~4 m/px
JPEG_Q = 92
WORKERS = 28
# Light burn only — DecalRoad carries the race line; keep sat readable on/near course
COURSE_BURN_HALF_WIDTH_M = 18.0
COURSE_BURN_STRENGTH = 0.12
USER_AGENT = "Parker400BeamNGBaker/1.0 (personal mod; Esri World Imagery tiles)"


def latlon_to_tile_xy(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2.0**z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y


def uv_to_latlon(u: np.ndarray, v: np.ndarray, t: dict) -> tuple[np.ndarray, np.ndarray]:
    X = u * WORLD_M
    Y = v * WORLD_M
    xm = (X - WORLD_M / 2.0) / t["scale"] + t["cx"]
    ym = (Y - WORLD_M / 2.0) / t["scale"] + t["cy"]
    lat = t["minLat"] + ym / 111320.0
    lon = t["minLon"] + xm / (111320.0 * np.cos(np.radians(lat)))
    return lat, lon


def download_tile(z: int, x: int, y: int, cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / f"{z}_{x}_{y}.jpg"
    if out.exists() and out.stat().st_size > 1000:
        return out
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if len(data) < 500:
                raise RuntimeError(f"tiny tile {z}/{x}/{y}")
            out.write_bytes(data)
            return out
        except Exception:
            if attempt == 3:
                raise
    return out


def jpg_to_rgb(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
    )
    arr = np.frombuffer(raw, dtype=np.uint8)
    n = arr.size // 3
    side = int(math.sqrt(n))
    return arr.reshape(side, side, 3)


def main() -> None:
    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    t = {
        "scale": course["transform"]["scale"],
        "cx": course["transform"]["cx"],
        "cy": course["transform"]["cy"],
        "minLat": course["transform"]["minLat"],
        "minLon": course["transform"]["minLon"],
    }

    corners = [(0, 0), (1, 0), (0, 1), (1, 1)]
    xs, ys = [], []
    for u, v in corners:
        lat, lon = uv_to_latlon(np.array([u]), np.array([v]), t)
        tx, ty = latlon_to_tile_xy(float(lat[0]), float(lon[0]), ZOOM)
        xs.append(tx)
        ys.append(ty)
    x0, x1 = int(math.floor(min(xs))), int(math.floor(max(xs)))
    y0, y1 = int(math.floor(min(ys))), int(math.floor(max(ys)))
    coords = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    print(f"Zoom {ZOOM} tiles x={x0}..{x1} y={y0}..{y1} ({len(coords)} tiles) → {OUT}²")

    cache = ROOT / "source" / "reference" / "satellite_cache"
    paths: dict[tuple[int, int], Path] = {}
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(download_tile, ZOOM, x, y, cache): (x, y) for x, y in coords}
        for fut in as_completed(futs):
            x, y = futs[fut]
            paths[(x, y)] = fut.result()
            done += 1
            if done % 50 == 0 or done == len(coords):
                print(f"  downloaded {done}/{len(coords)}")

    print("Decoding tiles...")
    sample = jpg_to_rgb(paths[(x0, y0)])
    tw, th = sample.shape[1], sample.shape[0]
    mosaic = np.zeros(((y1 - y0 + 1) * th, (x1 - x0 + 1) * tw, 3), dtype=np.uint8)
    for (x, y), path in paths.items():
        img = jpg_to_rgb(path) if (x, y) != (x0, y0) else sample
        px = (x - x0) * tw
        py = (y - y0) * th
        mosaic[py : py + th, px : px + tw] = img

    print(f"Resampling to {OUT}x{OUT} ...")
    out = np.zeros((OUT, OUT, 3), dtype=np.uint8)
    block = 256
    for y0b in range(0, OUT, block):
        y1b = min(OUT, y0b + block)
        vv = np.linspace(y0b / (OUT - 1), (y1b - 1) / (OUT - 1), y1b - y0b)[:, None]
        uu = np.linspace(0, 1, OUT)[None, :]
        uu = np.broadcast_to(uu, (y1b - y0b, OUT))
        vv = np.broadcast_to(vv, (y1b - y0b, OUT))
        lat, lon = uv_to_latlon(uu, vv, t)
        n = 2.0**ZOOM
        fx = (lon + 180.0) / 360.0 * n
        lat_r = np.radians(lat)
        fy = (1.0 - np.log(np.tan(lat_r) + 1.0 / np.cos(lat_r)) / math.pi) / 2.0 * n
        px = (fx - x0) * tw
        py = (fy - y0) * th
        px = np.clip(px, 0, mosaic.shape[1] - 1.001)
        py = np.clip(py, 0, mosaic.shape[0] - 1.001)
        # bilinear sample for cleaner 8 m/px
        x0i = np.floor(px).astype(np.int32)
        y0i = np.floor(py).astype(np.int32)
        x1i = np.clip(x0i + 1, 0, mosaic.shape[1] - 1)
        y1i = np.clip(y0i + 1, 0, mosaic.shape[0] - 1)
        wx = (px - x0i)[..., None]
        wy = (py - y0i)[..., None]
        c00 = mosaic[y0i, x0i].astype(np.float32)
        c10 = mosaic[y0i, x1i].astype(np.float32)
        c01 = mosaic[y1i, x0i].astype(np.float32)
        c11 = mosaic[y1i, x1i].astype(np.float32)
        sample_f = (c00 * (1 - wx) + c10 * wx) * (1 - wy) + (c01 * (1 - wx) + c11 * wx) * wy
        out[y0b:y1b] = np.clip(sample_f, 0, 255).astype(np.uint8)
        if y0b % 1024 == 0:
            print(f"  rows {y0b}..{y1b}")

    # Burn race corridor into sat (packed-dirt tint) — visible even if DecalRoad fails
    uvs = course.get("longCourseUv") or []
    if uvs:
        radius_px = max(1, int(round(COURSE_BURN_HALF_WIDTH_M / (WORLD_M / OUT))))
        print(f"Burning course corridor (r={radius_px}px, strength={COURSE_BURN_STRENGTH})...")
        mask = np.zeros((OUT, OUT), dtype=np.uint8)
        pts = np.array(uvs, dtype=np.float64)
        xs = np.clip(np.round(pts[:, 0] * (OUT - 1)).astype(np.int32), 0, OUT - 1)
        ys = np.clip(np.round(pts[:, 1] * (OUT - 1)).astype(np.int32), 0, OUT - 1)
        yy, xx = np.ogrid[-radius_px : radius_px + 1, -radius_px : radius_px + 1]
        disk = xx * xx + yy * yy <= radius_px * radius_px
        for x, y in zip(xs, ys):
            y0c, y1c = y - radius_px, y + radius_px + 1
            x0c, x1c = x - radius_px, x + radius_px + 1
            gy0, gy1 = max(0, y0c), min(OUT, y1c)
            gx0, gx1 = max(0, x0c), min(OUT, x1c)
            dy0, dx0 = gy0 - y0c, gx0 - x0c
            patch = disk[dy0 : dy0 + (gy1 - gy0), dx0 : dx0 + (gx1 - gx0)]
            mask[gy0:gy1, gx0:gx1][patch] = 1
        # Pale wash silt tint (matches course_pack shoulder)
        silt = np.array([208, 196, 172], dtype=np.float32)
        m = mask.astype(np.float32)[..., None] * COURSE_BURN_STRENGTH
        out_f = out.astype(np.float32)
        out = np.clip(out_f * (1.0 - m) + silt * m, 0, 255).astype(np.uint8)
        print(f"  course burn pixels: {int(mask.sum())}")

    IMPORT.mkdir(parents=True, exist_ok=True)
    LEVEL_ART.mkdir(parents=True, exist_ok=True)

    # Preview before freeing the big array
    step = max(1, OUT // 1024)
    north_up = np.flipud(out[::step, ::step].copy())
    ph, pw = north_up.shape[:2]
    for u, v in course["longCourseUv"][::2]:
        x = int(round(u * (pw - 1)))
        y = int(round((1.0 - v) * (ph - 1)))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                yy, xx = y + dy, x + dx
                if 0 <= yy < ph and 0 <= xx < pw:
                    north_up[yy, xx] = (242, 199, 71)
    write_png8(IMPORT / "parker400_base_color_preview.png", north_up)
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_satellite.png", north_up)

    # Encode: write full mosaic PPM, then Lanczos-scale to SHIP JPEG (encoder-safe size).
    jpg_level = LEVEL_ART / "parker400_base_color.jpg"
    jpg_import = IMPORT / "parker400_base_color.jpg"
    qv = 2 if JPEG_Q >= 95 else max(2, min(8, int(round((100 - JPEG_Q) * 0.2 + 2))))
    ppm = IMPORT / f"_sat_{OUT}.ppm"
    print(f"Writing temp PPM ({OUT}x{OUT})...")
    with ppm.open("wb") as f:
        f.write(f"P6\n{OUT} {OUT}\n255\n".encode("ascii"))
        flat = out.reshape(-1)
        del out
        chunk = OUT * 3 * 64
        for i in range(0, flat.size, chunk):
            f.write(flat[i : i + chunk].tobytes())
        del flat
    for dest in (jpg_level, jpg_import):
        print(f"Encoding {dest.name} at {SHIP}² (q={qv})...")
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-threads",
                "1",
                "-max_pixels",
                "400000000",
                "-i",
                str(ppm),
                "-vf",
                f"scale={SHIP}:{SHIP}:flags=lanczos",
                "-frames:v",
                "1",
                "-update",
                "1",
                "-q:v",
                str(qv),
                str(dest),
            ],
            check=True,
        )
        print(f"wrote {dest} ({dest.stat().st_size / 1e6:.1f} MB)")
    ppm.unlink(missing_ok=True)

    old_png = LEVEL_ART / "parker400_base_color.png"
    if old_png.exists():
        old_png.unlink()

    meta = {
        "source": "Esri World Imagery tiles (same family MapNG uses for satellite)",
        "zoom": ZOOM,
        "bakeResolution": OUT,
        "resolution": SHIP,
        "metersPerPixelApprox": round(WORLD_M / SHIP, 3),
        "format": "jpeg",
        "jpegQualityHint": JPEG_Q,
        "worldSizeMeters": WORLD_M,
        "geographicScale": course["geographicScale"],
        "tileRange": {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "count": len(coords)},
        "center": {"lat": 34.086139, "lon": -113.897239},
        "courseBurnHalfWidthMeters": COURSE_BURN_HALF_WIDTH_M,
        "courseBurnStrength": COURSE_BURN_STRENGTH,
        "note": "12288 unique sat (~5.3 m/px) from z15/16000 bake. Color detail/macro off so sat shows.",
    }
    (IMPORT / "parker400_base_color_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    print("OK: HD Parker satellite baked")


if __name__ == "__main__":
    main()
