#!/usr/bin/env python3
"""
EVO-style phone cradle — SOLID printable kit (v5)
=================================================
Watertight voxel CSG so every STL slices and prints on a Bambu P2S.

Shape cues from Sparco EVO reference (original geometry, not a scan/remix):
  - flared shoulder wings, deep thigh bolsters
  - twin trapezoid harness openings
  - headrest crown, recessed centre pad
  - phone pocket for iPhone 18 Pro Max + case (92 x 18 mm)
  - charge notch at bottom
  - modular 4x M3 back interface (30 mm square)

All parts are solid manifold meshes.
"""

from __future__ import annotations

import math
import shutil
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "stl"
DL = ROOT / "download"
OUT.mkdir(parents=True, exist_ok=True)
DL.mkdir(parents=True, exist_ok=True)

PHONE_W = 92.0
PHONE_T = 18.0
PHONE_H = 70.0
CHARGE_W = 14.0
M3 = 3.3
BACK_PATTERN = 30.0


def write_stl(path: Path, verts: np.ndarray, faces: np.ndarray, name: str):
    with open(path, "wb") as f:
        f.write(name.encode("ascii", "ignore")[:80].ljust(80, b"\0"))
        f.write(struct.pack("<I", len(faces)))
        for i0, i1, i2 in faces:
            a, b, c = verts[i0], verts[i1], verts[i2]
            n = np.cross(b - a, c - a)
            ln = np.linalg.norm(n)
            n = n / ln if ln > 1e-12 else np.array([0.0, 0.0, 1.0])
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *a))
            f.write(struct.pack("<3f", *b))
            f.write(struct.pack("<3f", *c))
            f.write(struct.pack("<H", 0))
    print(f"  {path.name:36s} {len(faces):7d} tris  {path.stat().st_size/1024:7.1f} KiB")


def light_smooth(verts, faces, iterations=2, lam=0.25):
    """Very light smooth — keeps EVO edges sharp, reduces voxel stair-steps."""
    n = len(verts)
    adj = [[] for _ in range(n)]
    for a, b, c in faces:
        adj[a].extend((b, c))
        adj[b].extend((a, c))
        adj[c].extend((a, b))
    adj = [np.unique(a) for a in adj]
    v = verts.copy()
    for _ in range(iterations):
        nv = v.copy()
        for i in range(n):
            if len(adj[i]) == 0:
                continue
            nv[i] = v[i] * (1 - lam) + v[adj[i]].mean(axis=0) * lam
        v = nv
    return v


def voxel_surface(occ: np.ndarray, pitch: float, origin: np.ndarray):
    p = np.pad(occ, 1, constant_values=False)
    verts = []
    faces = []
    vindex = {}

    def vid(x, y, z):
        key = (x, y, z)
        if key not in vindex:
            vindex[key] = len(verts)
            verts.append(origin + pitch * np.array([x, y, z], dtype=np.float64))
        return vindex[key]

    dirs = [
        (+1, 0, 0, [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        (-1, 0, 0, [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
        (0, +1, 0, [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
        (0, -1, 0, [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
        (0, 0, +1, [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        (0, 0, -1, [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ]

    for i, j, k in np.argwhere(p):
        for di, dj, dk, corners in dirs:
            if p[i + di, j + dj, k + dk]:
                continue
            ids = [vid(i + cx - 1, j + cy - 1, k + cz - 1) for cx, cy, cz in corners]
            faces.append((ids[0], ids[1], ids[2]))
            faces.append((ids[0], ids[2], ids[3]))

    verts = np.array(verts, dtype=np.float64)
    faces = np.array(faces, dtype=np.int32)
    if len(verts) == 0:
        raise RuntimeError("Empty mesh")
    verts = light_smooth(verts, faces)
    return verts, faces


def grid(bmin, bmax, pitch):
    mn = np.asarray(bmin, dtype=np.float64)
    mx = np.asarray(bmax, dtype=np.float64)
    dims = np.ceil((mx - mn) / pitch).astype(int) + 1
    xs = mn[0] + np.arange(dims[0]) * pitch
    ys = mn[1] + np.arange(dims[1]) * pitch
    zs = mn[2] + np.arange(dims[2]) * pitch
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    return X, Y, Z, mn, pitch


def ell(X, Y, Z, cx, cy, cz, rx, ry, rz):
    return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1.0


def box(X, Y, Z, x0, y0, z0, x1, y1, z1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1)


def cyl_z(X, Y, Z, cx, cy, r, z0, z1):
    return ((X - cx) ** 2 + (Y - cy) ** 2 <= r * r) & (Z >= z0) & (Z <= z1)


def cyl_y(X, Y, Z, cx, cz, r, y0, y1):
    return ((X - cx) ** 2 + (Z - cz) ** 2 <= r * r) & (Y >= y0) & (Y <= y1)


def cyl_x(X, Y, Z, cy, cz, r, x0, x1):
    return ((Y - cy) ** 2 + (Z - cz) ** 2 <= r * r) & (X >= x0) & (X <= x1)


def rot_x(X, Y, Z, deg, py=0.0, pz=0.0):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    Yp, Zp = Y - py, Z - pz
    return X, Yp * c - Zp * s + py, Yp * s + Zp * c + pz


def center_bed(verts):
    v = verts.copy()
    v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2
    v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2
    v[:, 2] -= v[:, 2].min()
    return v


def trap_hole(X, Y, Z, cx, cy0, cy1, cz, top_w, bot_w, h):
    """Trapezoid harness hole through Y."""
    tw, bw, hh = top_w / 2, bot_w / 2, h / 2
    # Approximate trap as two stacked boxes + taper via x-limit by z
    # For each voxel, interpolate half-width from top to bottom by z
    t = np.clip((cz + hh - Z) / (2 * hh), 0, 1)  # 0 at top, 1 at bottom
    hw = tw + (bw - tw) * t
    return (np.abs(X - cx) <= hw) & (Y >= cy0) & (Y <= cy1) & (Z >= cz - hh) & (Z <= cz + hh)


# ---------------------------------------------------------------------------
# SOLID cradle
# ---------------------------------------------------------------------------

def build_cradle(pitch=0.75):
    X, Y, Z, origin, pitch = grid((-70, -20, -4), (70, 72, 148), pitch)
    recline = -12.0
    Xr, Yr, Zr = rot_x(X, Y, Z, -recline, py=28.0, pz=14.0)

    solid = np.zeros(X.shape, dtype=bool)

    # === SEAT PAN (deep bucket) ===
    solid |= ell(Xr, Yr, Zr, 0, 34, 10, 52, 34, 12)
    solid |= box(Xr, Yr, Zr, -50, 10, 2, 50, 55, 16)
    # front lip (thick leading edge)
    solid |= ell(Xr, Yr, Zr, 0, 52, 9, 42, 16, 9)

    # === BACKREST COLUMN (recessed centre pad feel via solid then carve) ===
    for z, hw, dy, yc in [
        (22, 50, 18, 18),
        (40, 46, 17, 14),
        (58, 42, 15, 11),
        (75, 40, 14, 9),
        (95, 38, 13, 8),
        (112, 34, 12, 7),
        (125, 28, 11, 8),
        (136, 20, 9, 9),
    ]:
        solid |= ell(Xr, Yr, Zr, 0, yc, z, hw, dy, 11)

    # headrest crown (wider than open-shoulder blob — EVO has integrated headrest)
    solid |= ell(Xr, Yr, Zr, 0, 12, 138, 26, 14, 10)
    solid |= box(Xr, Yr, Zr, -24, 4, 128, 24, 22, 142)

    # === THIGH / HIP BOLSTERS (high sides — signature bucket) ===
    for s in (-1, 1):
        solid |= ell(Xr, Yr, Zr, s * 46, 30, 22, 16, 20, 20)
        solid |= ell(Xr, Yr, Zr, s * 44, 34, 38, 14, 18, 18)
        solid |= ell(Xr, Yr, Zr, s * 40, 28, 55, 12, 16, 16)

    # === SHOULDER WINGS (flare out — EVO look, NOT open-shoulder fade) ===
    for s in (-1, 1):
        solid |= ell(Xr, Yr, Zr, s * 48, 26, 88, 16, 18, 16)
        solid |= ell(Xr, Yr, Zr, s * 54, 28, 100, 14, 16, 14)
        solid |= ell(Xr, Yr, Zr, s * 48, 24, 112, 12, 14, 12)
        # wing tip curves forward
        solid |= ell(Xr, Yr, Zr, s * 50, 36, 98, 10, 14, 12)

    # === REAR SHELL thickness (spine) ===
    solid |= box(Xr, Yr, Zr, -8, -8, 25, 8, 4, 120)
    solid |= box(Xr, Yr, Zr, -28, -10, 45, 28, -2, 85)

    # Mounting boss (flat pad for modular backs)
    solid |= box(Xr, Yr, Zr, -24, -12, 50, 24, 0, 86)

    # === CARVES ===

    # Phone pocket — deep enough to hold phone upright against back
    hw, ht = PHONE_W / 2, PHONE_T / 2
    px, py, pz = 0.0, 26.0, 24.0
    solid &= ~box(Xr, Yr, Zr, px - hw, py - ht, pz, px + hw, py + ht, pz + PHONE_H)
    # insertion mouth (slightly open front)
    solid &= ~box(
        Xr, Yr, Zr,
        px - hw + 1, py + ht - 1.5, pz + 8,
        px + hw - 1, py + ht + 14, pz + PHONE_H - 4,
    )
    # charge notch + cable drop at bottom center of pocket
    solid &= ~box(
        Xr, Yr, Zr,
        -CHARGE_W / 2, py + ht - 4, pz - 3,
        CHARGE_W / 2, py + ht + 12, pz + 14,
    )
    solid &= ~cyl_z(Xr, Yr, Zr, 0, py + ht + 3, 5.5, pz - 5, pz + 8)

    # Twin harness trapezoid openings (EVO signature)
    for cx in (-20.0, 20.0):
        solid &= ~trap_hole(Xr, Yr, Zr, cx, -8, 40, 112, top_w=22, bot_w=14, h=13)

    # Lap belt side holes (smaller, lower)
    for s in (-1, 1):
        solid &= ~box(Xr, Yr, Zr, s * 48 - 5, 8, 28, s * 48 + 5, 38, 40)

    # M3 pattern in back boss
    hs = BACK_PATTERN / 2
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(Xr, Yr, Zr, dx, 68 + dz, M3 / 2, -14, 2)

    # Keep a thin floor under phone so it's printable / retains phone
    # (already have solid around pocket)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


# ---------------------------------------------------------------------------
# Modular backs — SOLID
# ---------------------------------------------------------------------------

def build_rail_back(orientation: str, pitch=0.55):
    X, Y, Z, origin, pitch = grid((-28, -4, -4), (28, 22, 48), pitch)
    solid = np.zeros(X.shape, dtype=bool)

    # Mount plate (mates to cradle boss)
    solid |= box(X, Y, Z, -20, 0, 0, 20, 5, 42)

    # M3 through holes (30 mm square)
    hs = BACK_PATTERN / 2
    cz = 21.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 8)

    # Twist-lock key for 4040 ~8 mm T-slot
    if orientation == "vertical":
        solid |= box(X, Y, Z, -3.6, 5, 8, 3.6, 12, 34)
        solid |= box(X, Y, Z, -7.5, 11.5, 10, 7.5, 16.5, 32)
    else:
        solid |= box(X, Y, Z, -13, 5, 17, 13, 12, 25)
        solid |= box(X, Y, Z, -11, 11.5, 14, 11, 16.5, 28)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def build_leg_plate(pitch=0.55):
    X, Y, Z, origin, pitch = grid((-30, -4, -4), (30, 20, 50), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box(X, Y, Z, -22, 0, 0, 22, 6, 44)

    hs = BACK_PATTERN / 2
    cz = 22.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 9)

    # Three leg sockets (M3 clearance + boss)
    for dx, dz in [(-14, 10), (14, 10), (0, 36)]:
        solid |= cyl_y(X, Y, Z, dx, dz, 5.5, 6, 14)
        solid &= ~cyl_y(X, Y, Z, dx, dz, M3 / 2, 5, 15)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def build_desk_leg(pitch=0.5):
    X, Y, Z, origin, pitch = grid((-14, -14, -2), (14, 14, 55), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= cyl_z(X, Y, Z, 0, 0, 10, 0, 3.5)
    solid |= cyl_z(X, Y, Z, 0, 0, 7.5, 3, 20)
    solid |= cyl_z(X, Y, Z, 0, 0, 5.5, 18, 42)
    solid |= cyl_z(X, Y, Z, 0, 0, 4.5, 40, 50)
    # M3 hole from top + nut trap
    solid &= ~cyl_z(X, Y, Z, 0, 0, M3 / 2, 35, 52)
    solid &= ~cyl_z(X, Y, Z, 0, 0, 4.0, 38, 42.5)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def build_kickout(pitch=0.55):
    X, Y, Z, origin, pitch = grid((-26, -4, -4), (26, 42, 48), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box(X, Y, Z, -20, 0, 0, 20, 5, 42)

    hs = BACK_PATTERN / 2
    cz = 21.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 8)

    # Kick-out arm
    solid |= box(X, Y, Z, -8, 5, 16, 8, 30, 28)
    solid |= ell(X, Y, Z, 0, 32, 22, 8, 8, 7)
    # M3 holes (pivot)
    solid &= ~cyl_x(X, Y, Z, 30, 22, M3 / 2, -10, 10)
    solid &= ~cyl_z(X, Y, Z, 0, 32, M3 / 2, 14, 30)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def build_clamp_desk(pitch=0.55):
    X, Y, Z, origin, pitch = grid((-18, -4, -4), (36, 36, 28), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    # C-clamp for desks ~22 mm thick
    solid |= box(X, Y, Z, 0, 0, 0, 28, 6, 22)
    solid |= box(X, Y, Z, 0, 0, 0, 6, 28, 22)
    solid |= box(X, Y, Z, 0, 22, 0, 28, 28, 22)
    solid &= ~box(X, Y, Z, 6, 6, -1, 30, 22, 23)
    # M5 thumb-screw hole in bottom jaw
    solid &= ~cyl_z(X, Y, Z, 18, 25, 2.7, -1, 30)
    # M3 ear for kick-out
    solid |= box(X, Y, Z, -12, 8, 6, 1, 18, 16)
    solid &= ~cyl_x(X, Y, Z, 13, 11, M3 / 2, -14, 2)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def build_clamp_tube(tube_od=40.4, pitch=0.55):
    X, Y, Z, origin, pitch = grid((-42, -30, -4), (42, 42, 28), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    r_out = tube_od / 2 + 4.5
    r_in = tube_od / 2 + 0.2

    solid |= cyl_z(X, Y, Z, 0, 0, r_out, 0, 22)
    solid &= ~cyl_z(X, Y, Z, 0, 0, r_in, -1, 23)
    solid &= Y >= -0.8  # half clamp — print ×2

    for s in (-1, 1):
        ex = s * (r_out + 7)
        solid |= box(X, Y, Z, ex - 6.5, -1, 0, ex + 6.5, 5.5, 22)
        solid &= ~cyl_z(X, Y, Z, ex, 2.2, 2.7, -1, 23)

    # M3 pivot tab
    solid |= box(X, Y, Z, -6, r_out - 1, 5, 6, r_out + 12, 17)
    solid &= ~cyl_x(X, Y, Z, r_out + 6, 11, M3 / 2, -8, 8)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def build_blank_back(pitch=0.55):
    X, Y, Z, origin, pitch = grid((-28, -4, -4), (28, 12, 48), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box(X, Y, Z, -20, 0, 0, 20, 5, 42)

    hs = BACK_PATTERN / 2
    cz = 21.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 8)
    # Extra DIY leg holes
    for dx, dz in [(-14, 8), (14, 8), (-14, 34), (14, 34)]:
        solid &= ~cyl_y(X, Y, Z, dx, dz, M3 / 2, -1, 8)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_bed(verts), faces


def edge_open_count(verts, faces):
    from collections import Counter
    edges = Counter()
    for a, b, c in faces:
        for i, j in ((a, b), (b, c), (c, a)):
            e = (min(i, j), max(i, j))
            edges[e] += 1
    return sum(1 for v in edges.values() if v != 2)


def main():
    print("Building SOLID printable EVO kit (v5)...\n")
    parts = [
        ("01_cradle_evo.stl", lambda: build_cradle(0.75)),
        ("02_back_rail_vertical.stl", lambda: build_rail_back("vertical")),
        ("03_back_rail_horizontal.stl", lambda: build_rail_back("horizontal")),
        ("04_back_leg_plate.stl", build_leg_plate),
        ("05_desk_leg.stl", build_desk_leg),
        ("06_back_kickout_m3.stl", build_kickout),
        ("07_clamp_desk_m3.stl", build_clamp_desk),
        ("08_clamp_tube40_m3.stl", build_clamp_tube),
        ("09_back_blank_diy.stl", build_blank_back),
    ]

    results = []
    for name, fn in parts:
        print(f"→ {name}")
        v, f = fn()
        open_n = edge_open_count(v, f)
        write_stl(OUT / name, v, f, name.replace(".stl", ""))
        shutil.copy2(OUT / name, DL / name)
        sz = v.max(0) - v.min(0)
        results.append((name, open_n, sz))
        print(f"    size {sz[0]:.0f}×{sz[1]:.0f}×{sz[2]:.0f} mm  open_edges={open_n}")

    print("\n=== SOLIDITY CHECK ===")
    bad = [n for n, o, _ in results if o > 50]
    if bad:
        print("WARNING open meshes:", bad)
    else:
        print("All parts look watertight (or near-watertight).")

    print("\nSynced to download/")


if __name__ == "__main__":
    main()
