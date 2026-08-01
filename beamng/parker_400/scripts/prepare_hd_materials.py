#!/usr/bin/env python3
"""Upscale terrain base maps to 4096 so BeamNG can pack them with HD satellite."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "levels" / "parker_400" / "art" / "terrains"
TARGET = 4096

# Source base maps (typically 512) → TARGET PNG with _4096 suffix.
# desert_base color stays as parker400_base_color.jpg (unique satellite).
UPSCALE = [
    # desert_base PBR bases (color is satellite unique map)
    "desert_base_base_nm.png",
    "desert_base_base_r.png",
    "desert_base_base_ao.png",
    "desert_base_base_h.png",
    # course_pack full base set (tiled dirt ribbon)
    "course_pack_base_b.png",
    "course_pack_base_nm.png",
    "course_pack_base_r.png",
    "course_pack_base_ao.png",
    "course_pack_base_h.png",
]


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png_rgba(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    i = 8
    width = height = bit_depth = color_type = None
    idat = bytearray()
    while i < len(data):
        length = struct.unpack(">I", data[i : i + 4])[0]
        ctype = data[i + 4 : i + 8]
        chunk = data[i + 8 : i + 8 + length]
        i += 12 + length
        if ctype == b"IHDR":
            width, height, bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", chunk)
        elif ctype == b"IDAT":
            idat.extend(chunk)
        elif ctype == b"IEND":
            break
    assert width and height and bit_depth == 8 and color_type in (0, 2, 6), path
    raw = zlib.decompress(bytes(idat))
    bpp = {0: 1, 2: 3, 6: 4}[color_type]
    stride = width * bpp
    out = bytearray(height * stride)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        f = raw[pos]
        pos += 1
        row = bytearray(raw[pos : pos + stride])
        pos += stride
        cur = bytearray(stride)
        for x in range(stride):
            left = cur[x - bpp] if x >= bpp else 0
            up = prev[x]
            ul = prev[x - bpp] if x >= bpp else 0
            v = row[x]
            if f == 0:
                cur[x] = v
            elif f == 1:
                cur[x] = (v + left) & 255
            elif f == 2:
                cur[x] = (v + up) & 255
            elif f == 3:
                cur[x] = (v + ((left + up) // 2)) & 255
            elif f == 4:
                cur[x] = (v + paeth(left, up, ul)) & 255
            else:
                raise ValueError(f"bad filter {f} in {path}")
        out[y * stride : (y + 1) * stride] = cur
        prev = cur
    rgba = bytearray(width * height * 4)
    if color_type == 0:
        for p in range(width * height):
            g = out[p]
            rgba[p * 4] = g
            rgba[p * 4 + 1] = g
            rgba[p * 4 + 2] = g
            rgba[p * 4 + 3] = 255
    elif color_type == 2:
        for p in range(width * height):
            rgba[p * 4 : p * 4 + 3] = out[p * 3 : p * 3 + 3]
            rgba[p * 4 + 3] = 255
    else:
        rgba[:] = out
    return width, height, bytes(rgba)


def nearest_upscale(w: int, h: int, rgba: bytes, tw: int, th: int) -> bytes:
    out = bytearray(tw * th * 4)
    for y in range(th):
        sy = (y * h) // th
        src_row = sy * w * 4
        dst_row = y * tw * 4
        for x in range(tw):
            sx = (x * w) // tw
            si = src_row + sx * 4
            di = dst_row + x * 4
            out[di : di + 4] = rgba[si : si + 4]
    return bytes(out)


def write_png_rgba(path: Path, w: int, h: int, rgba: bytes) -> None:
    stride = w * 4
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(rgba[y * stride : (y + 1) * stride])
    compressed = zlib.compress(bytes(raw), 6)

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def out_name(src_name: str) -> str:
    stem = Path(src_name).stem  # e.g. course_pack_base_b
    return f"{stem}_4096.png"


def main() -> None:
    sat = ART / "parker400_base_color.jpg"
    if not sat.exists():
        sat = ART / "parker400_base_color.png"
    if not sat.exists():
        raise SystemExit("missing satellite: parker400_base_color.jpg/.png")
    print(f"satellite present: {sat.name} ({sat.stat().st_size / 1e6:.1f} MB)")

    for name in UPSCALE:
        src = ART / name
        if not src.exists():
            raise SystemExit(f"missing {src}")
        w, h, rgba = decode_png_rgba(src)
        up = nearest_upscale(w, h, rgba, TARGET, TARGET)
        out = ART / out_name(name)
        write_png_rgba(out, TARGET, TARGET, up)
        print(f"wrote {out.name} ({TARGET}x{TARGET} from {w}x{h})")
    print("OK: HD base maps ready for texture-set packing")


if __name__ == "__main__":
    main()
