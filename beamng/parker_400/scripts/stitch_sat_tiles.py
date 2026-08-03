#!/usr/bin/env python3
"""Burn georeferenced Google Earth / MapNG tiles into the Parker unique sat.

Drop tiles + tiles.json in import/sat_tiles/ (see docs/CLOSEUP_MULTI_TILE.md),
then run this script and pack_mod_zip.py.

Each tile needs center lat/lon and ground size in meters (north-up image).
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from pngio import write_png8  # noqa: E402

P400 = ROOT / "source" / "reference" / "p400"
TILES_DIR = ROOT / "import" / "sat_tiles"
SAT_JPG = ROOT / "levels" / "parker_400" / "art" / "terrains" / "parker400_base_color.jpg"
IMPORT = ROOT / "import"
WORLD_M = 65536.0


def load_rgb(path: Path) -> np.ndarray:
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    )
    arr = np.frombuffer(raw, dtype=np.uint8)
    # probe size via ffprobe
    probe = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    w, h = [int(x) for x in probe.split(",")]
    return arr.reshape(h, w, 3)


def write_jpg(path: Path, rgb: np.ndarray, quality: int = 92) -> None:
    h, w, _ = rgb.shape
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{w}x{h}",
            "-i",
            "-",
            "-q:v",
            str(max(1, min(31, int(round((100 - quality) / 3))))),
            str(path),
        ],
        input=np.ascontiguousarray(rgb).tobytes(),
        check=True,
    )


def latlon_to_uv(lat: float, lon: float, t: dict) -> tuple[float, float]:
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat))
    xm = (lon - t["minLon"]) * m_per_deg_lon
    ym = (lat - t["minLat"]) * m_per_deg_lat
    X = (xm - t["cx"]) * t["scale"] + WORLD_M / 2.0
    Y = (ym - t["cy"]) * t["scale"] + WORLD_M / 2.0
    return X / WORLD_M, Y / WORLD_M


def resize_rgb(rgb: np.ndarray, tw: int, th: int) -> np.ndarray:
    h, w, _ = rgb.shape
    if w == tw and h == th:
        return rgb
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{w}x{h}",
            "-i",
            "-",
            "-vf",
            f"scale={tw}:{th}:flags=lanczos",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        input=np.ascontiguousarray(rgb).tobytes(),
    )
    return np.frombuffer(raw, dtype=np.uint8).reshape(th, tw, 3)


def feather_mask(h: int, w: int, feather: float = 0.12) -> np.ndarray:
    """Soft edge mask 0..1 so tiles blend into the base sat."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = min(h, w) * feather
    d = np.minimum.reduce([xx, yy, (w - 1 - xx), (h - 1 - yy)])
    return np.clip(d / max(edge, 1.0), 0.0, 1.0).astype(np.float32)


def main() -> None:
    cfg_path = TILES_DIR / "tiles.json"
    if not cfg_path.exists():
        raise SystemExit(
            f"Missing {cfg_path}\n"
            "Add Google Earth / MapNG tiles + tiles.json — see docs/CLOSEUP_MULTI_TILE.md"
        )
    if not SAT_JPG.exists():
        raise SystemExit(f"Missing base sat {SAT_JPG} — run bake_esri_satellite.py first")

    course = json.loads((P400 / "p400_map_course.json").read_text(encoding="utf-8"))
    t = course["transform"]
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    tiles = cfg.get("tiles") or []
    if not tiles:
        raise SystemExit("tiles.json has no tiles[] entries")

    print(f"Loading base sat {SAT_JPG.name}…")
    base = load_rgb(SAT_JPG).astype(np.float32)
    # BeamNG unique sat: row0 = south (same as bake_esri)
    H, W, _ = base.shape
    placed = 0

    for entry in tiles:
        path = TILES_DIR / entry["file"]
        if not path.exists():
            print(f"  skip missing {path.name}")
            continue
        lat = float(entry["lat"])
        lon = float(entry["lon"])
        width_m = float(entry.get("widthMeters") or entry.get("sizeMeters") or 4000)
        height_m = float(entry.get("heightMeters") or width_m)
        u, v = latlon_to_uv(lat, lon, t)
        # pixel center; v=0 south at row0
        cx = u * (W - 1)
        cy = v * (H - 1)
        tw = max(2, int(round(width_m / WORLD_M * W)))
        th = max(2, int(round(height_m / WORLD_M * H)))
        print(f"  {path.name}: center uv=({u:.4f},{v:.4f}) → {tw}x{th}px")

        patch = resize_rgb(load_rgb(path), tw, th).astype(np.float32)
        # GE is usually north-up; our sat row0=south → flip patch vertically
        if entry.get("northUp", True):
            patch = np.flipud(patch)

        x0 = int(round(cx - tw / 2))
        y0 = int(round(cy - th / 2))
        x1, y1 = x0 + tw, y0 + th
        # clip to canvas
        sx0, sy0 = max(0, x0), max(0, y0)
        sx1, sy1 = min(W, x1), min(H, y1)
        if sx0 >= sx1 or sy0 >= sy1:
            print("    outside map — skipped")
            continue
        px0, py0 = sx0 - x0, sy0 - y0
        px1, py1 = px0 + (sx1 - sx0), py0 + (sy1 - sy0)
        region = patch[py0:py1, px0:px1]
        mask = feather_mask(th, tw)[py0:py1, px0:px1][..., None]
        strength = float(entry.get("strength", 1.0))
        m = mask * strength
        dst = base[sy0:sy1, sx0:sx1]
        base[sy0:sy1, sx0:sx1] = dst * (1 - m) + region * m
        placed += 1

    if placed == 0:
        raise SystemExit("No tiles placed — check files / lat-lon / sizes")

    out = np.clip(base, 0, 255).astype(np.uint8)
    SAT_JPG.parent.mkdir(parents=True, exist_ok=True)
    write_jpg(SAT_JPG, out, quality=92)
    IMPORT.mkdir(parents=True, exist_ok=True)
    write_jpg(IMPORT / "parker400_base_color.jpg", out, quality=92)
    # small preview
    prev = resize_rgb(out, 1024, 1024)
    write_png8(IMPORT / "parker400_base_color_preview.png", prev)
    art = Path("/opt/cursor/artifacts")
    art.mkdir(parents=True, exist_ok=True)
    write_png8(art / "parker400_sat_stitched_preview.png", prev)
    print(f"Stitched {placed} tile(s) into {SAT_JPG}")
    print("Next: python3 scripts/pack_mod_zip.py")


if __name__ == "__main__":
    main()
