"""Minimal RGBA PNG load/save/resize (no Pillow). Matches ctype=6 8-bit non-interlaced."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


def save_rgba(path: Path | str, w: int, h: int, pixels: list[tuple[int, int, int, int]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        row = y * w
        for x in range(w):
            raw.extend(pixels[row + x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    path.write_bytes(
        b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)),
                chunk(b"IDAT", zlib.compress(bytes(raw), 6)),
                chunk(b"IEND", b""),
            ]
        )
    )


def load_rgba(path: Path | str) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    pos = 8
    w = h = None
    bit = ctype = inter = None
    idat = b""
    while pos + 8 <= len(data):
        ln = struct.unpack(">I", data[pos : pos + 4])[0]
        pos += 4
        tag = data[pos : pos + 4]
        pos += 4
        chunk = data[pos : pos + ln]
        pos += ln + 4
        if tag == b"IHDR":
            w, h, bit, ctype, _comp, _filt, inter = struct.unpack(">IIBBBBB", chunk)
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
    if w is None or h is None:
        raise ValueError(f"bad PNG header: {path}")
    if bit != 8 or ctype != 6 or inter != 0:
        raise ValueError(f"unsupported PNG (need 8-bit RGBA non-interlaced): {path}")
    raw = zlib.decompress(idat)
    bpp = 4
    stride = 1 + w * bpp
    # Undo PNG filters
    rows = []
    prev = bytearray(w * bpp)
    for y in range(h):
        start = y * stride
        ftype = raw[start]
        cur = bytearray(raw[start + 1 : start + stride])
        if ftype == 0:
            pass
        elif ftype == 1:  # Sub
            for i in range(bpp, len(cur)):
                cur[i] = (cur[i] + cur[i - bpp]) & 255
        elif ftype == 2:  # Up
            for i in range(len(cur)):
                cur[i] = (cur[i] + prev[i]) & 255
        elif ftype == 3:  # Average
            for i in range(len(cur)):
                left = cur[i - bpp] if i >= bpp else 0
                up = prev[i]
                cur[i] = (cur[i] + ((left + up) >> 1)) & 255
        elif ftype == 4:  # Paeth
            for i in range(len(cur)):
                a = cur[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                cur[i] = (cur[i] + pr) & 255
        else:
            raise ValueError(f"unsupported filter {ftype} in {path}")
        rows.append(bytes(cur))
        prev = cur
    pixels = []
    for row in rows:
        for x in range(w):
            i = x * 4
            pixels.append((row[i], row[i + 1], row[i + 2], row[i + 3]))
    return w, h, pixels


def resize_box(
    src_w: int,
    src_h: int,
    src: list[tuple[int, int, int, int]],
    dst_w: int,
    dst_h: int,
) -> list[tuple[int, int, int, int]]:
    """Box-filter resize."""
    out = []
    for y in range(dst_h):
        y0 = y * src_h // dst_h
        y1 = max(y0 + 1, (y + 1) * src_h // dst_h)
        for x in range(dst_w):
            x0 = x * src_w // dst_w
            x1 = max(x0 + 1, (x + 1) * src_w // dst_w)
            r = g = b = a = n = 0
            for yy in range(y0, y1):
                row = yy * src_w
                for xx in range(x0, x1):
                    p = src[row + xx]
                    r += p[0]
                    g += p[1]
                    b += p[2]
                    a += p[3]
                    n += 1
            out.append((r // n, g // n, b // n, a // n))
    return out


def blit(
    dst_w: int,
    dst: list[tuple[int, int, int, int]],
    src_w: int,
    src_h: int,
    src: list[tuple[int, int, int, int]],
    dx: int,
    dy: int,
) -> None:
    for y in range(src_h):
        sy = dy + y
        if sy < 0:
            continue
        for x in range(src_w):
            sx = dx + x
            if sx < 0:
                continue
            # assume caller sized correctly; skip OOB
            di = sy * dst_w + sx
            if 0 <= di < len(dst):
                dst[di] = src[y * src_w + x]


def solid(w: int, h: int, color=(0, 0, 0, 255)) -> list[tuple[int, int, int, int]]:
    return [color] * (w * h)
