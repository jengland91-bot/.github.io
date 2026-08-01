#!/usr/bin/env python3
"""
Convert an RGB terrain feature mask into a grayscale heightmap.

Typical World-Machine / GIS preview style:
  R = ridges / peaks (high)
  G = slopes / mid
  B = valleys / basins (low)

Usage:
  python3 rgb_to_heightmap.py [input.png]
  python3 rgb_to_heightmap.py   # uses source/rgb_terrain_mask.png

Outputs (terrain/export/):
  heightmap_8bit.png   — Blender displace / preview
  heightmap_16bit.png  — higher precision (16-bit gray via PNG)
  heightmap_preview.png — false-color check (optional)
"""

from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))
from pngutil import load_rgba, save_rgba, solid  # noqa: E402

SRC_DEFAULT = ROOT / "source" / "rgb_terrain_mask.png"
OUT = ROOT / "export"


def save_gray16(path: Path, w: int, h: int, values_01: list[float]) -> None:
    """16-bit grayscale PNG (ctype=0, bit depth 16)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter None
        row = y * w
        for x in range(w):
            v = int(max(0.0, min(1.0, values_01[row + x])) * 65535.0 + 0.5)
            raw.append((v >> 8) & 255)
            raw.append(v & 255)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    # IHDR: 16-bit, grayscale, non-interlaced
    ihdr = struct.pack(">IIBBBBB", w, h, 16, 0, 0, 0, 0)
    path.write_bytes(
        b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                chunk(b"IHDR", ihdr),
                chunk(b"IDAT", zlib.compress(bytes(raw), 6)),
                chunk(b"IEND", b""),
            ]
        )
    )


def box_blur(w: int, h: int, data: list[float], radius: int) -> list[float]:
    if radius <= 0:
        return data
    out = data[:]
    # Separable approximate blur (horizontal then vertical)
    tmp = [0.0] * (w * h)
    for y in range(h):
        for x in range(w):
            s = c = 0.0
            for dx in range(-radius, radius + 1):
                xx = min(w - 1, max(0, x + dx))
                s += data[y * w + xx]
                c += 1
            tmp[y * w + x] = s / c
    for y in range(h):
        for x in range(w):
            s = c = 0.0
            for dy in range(-radius, radius + 1):
                yy = min(h - 1, max(0, y + dy))
                s += tmp[yy * w + x]
                c += 1
            out[y * w + x] = s / c
    return out


def rgb_to_height(w: int, h: int, pixels) -> list[float]:
    """
    Decode R/G/B feature weights into height in [0,1].

    Uses channel dominance (softmax-ish) so pure blue → low, pure red → high,
    green → mid, mixed colors interpolate smoothly.
    """
    heights = []
    for r, g, b, _a in pixels:
        rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
        # Softmax weights so channels compete
        k = 6.0
        er, eg, eb = math.exp(k * rf), math.exp(k * gf), math.exp(k * bf)
        s = er + eg + eb
        wr, wg, wb = er / s, eg / s, eb / s
        # Target elevations for each class
        hgt = wr * 1.0 + wg * 0.45 + wb * 0.08
        # Tiny luminance detail so it isn't perfectly flat in large regions
        lum = 0.299 * rf + 0.587 * gf + 0.114 * bf
        hgt = hgt * 0.92 + lum * 0.08
        heights.append(hgt)
    return heights


def normalize(data: list[float]) -> list[float]:
    lo, hi = min(data), max(data)
    span = hi - lo if hi > lo else 1.0
    return [(v - lo) / span for v in data]


def make_synthetic_rgb(path: Path, size: int = 1024) -> None:
    """
    Generate a demo RGB ridge/valley mask similar to World Machine style
    (red ridges, green slopes, blue basins) when no source image is present.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    px = []
    for y in range(size):
        for x in range(size):
            nx = x / size
            ny = y / size
            # Multi-scale warped ridges
            v = (
                math.sin((nx * 7.3 + math.sin(ny * 4.1) * 0.4) * math.pi)
                * math.cos((ny * 5.7 + math.cos(nx * 3.3) * 0.35) * math.pi)
                + 0.35 * math.sin((nx + ny) * 18.0)
                + 0.2 * math.sin(nx * 31.0 - ny * 27.0)
            )
            # Ridge strength
            ridge = abs(v)
            # Valley = inverted smoothed field
            valley = max(0.0, 0.55 - ridge)
            slope = max(0.0, 1.0 - ridge * 1.4 - valley * 1.1)
            # Noise stipple
            n = ((x * 13) ^ (y * 7)) % 17 / 17.0
            r = int(min(255, ridge * 255 * 1.3 + n * 8))
            g = int(min(255, slope * 220 + n * 10))
            b = int(min(255, valley * 255 * 1.4 + n * 6))
            # Boost contrast per channel
            if ridge > 0.45:
                r = min(255, r + 40)
                g = int(g * 0.5)
                b = int(b * 0.3)
            if valley > 0.35:
                b = min(255, b + 50)
                r = int(r * 0.35)
            px.append((r, g, b, 255))
    save_rgba(path, size, size, px)
    print(f"wrote synthetic source {path}")


def convert(src: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    w, h, pixels = load_rgba(src)
    print(f"loaded {src} {w}x{h}")

    heights = rgb_to_height(w, h, pixels)
    heights = normalize(heights)
    # Light blur — removes channel-edge stair steps, keeps ridge structure
    heights = box_blur(w, h, heights, radius=max(1, w // 256))
    heights = normalize(heights)

    # 8-bit grayscale (RGB triplet)
    gray8 = []
    for v in heights:
        g = int(v * 255 + 0.5)
        gray8.append((g, g, g, 255))
    save_rgba(OUT / "heightmap_8bit.png", w, h, gray8)
    save_gray16(OUT / "heightmap_16bit.png", w, h, heights)

    # Preview: height as luminosity with slight cyan/amber tint
    preview = []
    for v in heights:
        preview.append((int(v * 255), int(v * 220), int(v * 180), 255))
    save_rgba(OUT / "heightmap_preview.png", w, h, preview)

    print(f"wrote {OUT / 'heightmap_8bit.png'}")
    print(f"wrote {OUT / 'heightmap_16bit.png'}")
    print(f"wrote {OUT / 'heightmap_preview.png'}")


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    if not src.exists():
        print(f"No source at {src} — generating synthetic RGB mask for demo")
        make_synthetic_rgb(src)
    convert(src)
    print("DONE heightmap")


if __name__ == "__main__":
    main()
