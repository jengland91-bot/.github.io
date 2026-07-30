#!/usr/bin/env python3
"""Minimal PNG writers (no Pillow). Supports 8-bit L/RGB and 16-bit grayscale."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png16_gray(path: Path | str, arr: np.ndarray) -> None:
    """Write HxW uint16 array as 16-bit grayscale PNG (big-endian samples)."""
    if arr.dtype != np.uint16:
        raise TypeError("expected uint16")
    if arr.ndim != 2:
        raise ValueError("expected 2D array")
    h, w = arr.shape
    # Filter byte 0 + big-endian 16-bit samples per row
    rows = []
    be = arr.astype(">u2", copy=False)
    for y in range(h):
        rows.append(b"\x00" + be[y].tobytes())
    raw = b"".join(rows)
    ihdr = struct.pack(">IIBBBBB", w, h, 16, 0, 0, 0, 0)  # 16-bit grayscale
    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _chunk(b"IHDR", ihdr),
            _chunk(b"IDAT", zlib.compress(raw, 6)),
            _chunk(b"IEND", b""),
        ]
    )
    Path(path).write_bytes(png)


def write_png8(path: Path | str, arr: np.ndarray) -> None:
    """Write HxW uint8 (L) or HxWx3 uint8 (RGB) PNG."""
    if arr.dtype != np.uint8:
        raise TypeError("expected uint8")
    if arr.ndim == 2:
        h, w = arr.shape
        color_type = 0
        channels = 1
    elif arr.ndim == 3 and arr.shape[2] == 3:
        h, w, _ = arr.shape
        color_type = 2
        channels = 3
    else:
        raise ValueError("expected HxW or HxWx3")
    rows = []
    flat = arr.reshape(h, w * channels)
    for y in range(h):
        rows.append(b"\x00" + flat[y].tobytes())
    raw = b"".join(rows)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0)
    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _chunk(b"IHDR", ihdr),
            _chunk(b"IDAT", zlib.compress(raw, 6)),
            _chunk(b"IEND", b""),
        ]
    )
    Path(path).write_bytes(png)
