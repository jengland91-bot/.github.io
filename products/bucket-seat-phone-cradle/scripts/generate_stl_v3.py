#!/usr/bin/env python3
"""
Evo-style Bucket Phone Cradle — modular product family (v3)
===========================================================
Original geometry for selling. Inspired by Sparco EVO III open-shoulder
silhouette (race-truck seat cue) — not a remix of MakerWorld / Recaro STLs.

Phone target: iPhone 18 Pro Max (78.0 x 8.75 mm) + thick case headroom
  pocket ≈ 92 mm wide × 18 mm thick, charge notch at bottom.

Mount system (mix-and-match):
  - back_rail_vertical.stl / back_rail_horizontal.stl  → 4040-style T-slot
  - back_leg_plate.stl + desk_leg.stl                  → desk stand
  - back_kickout_m3.stl + clamp_desk_m3 / clamp_tube40 → bolt-on clamps

Cradle back uses a common 4× M3 pattern (30 mm square) so backs swap.
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "stl"
OUT.mkdir(parents=True, exist_ok=True)

# --- Product constants ---
PHONE_W = 92.0          # mm — iPhone 18 Pro Max 78 + case
PHONE_T = 18.0          # mm — 8.75 body + thick case
PHONE_POCKET_H = 62.0   # how deep phone sits in the seat
CHARGE_W = 14.0
CHARGE_H = 12.0

# Shared back interface (M3 clearance holes)
M3 = 3.2
BACK_PATTERN = 30.0     # square spacing between holes
BACK_BOSS_T = 6.0


def write_stl(path: Path, verts: np.ndarray, faces: np.ndarray, name: str = "part"):
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
    kb = path.stat().st_size / 1024
    print(f"  Wrote {path.name:36s}  {len(faces):7d} tris  {kb:8.1f} KiB")


def laplacian_smooth(verts, faces, iterations=8, lam=0.45):
    n = len(verts)
    adj = [[] for _ in range(n)]
    for a, b, c in faces:
        adj[a].extend([b, c])
        adj[b].extend([a, c])
        adj[c].extend([a, b])
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
    verts = laplacian_smooth(verts, faces, iterations=8, lam=0.45)
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


def center_on_bed(verts):
    v = verts.copy()
    v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2
    v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2
    v[:, 2] -= v[:, 2].min()
    return v


def m3_pattern_holes(X, Y, Z, cx, cy, cz_face, into="-Y", depth=10):
    """Carve 4× M3 holes on BACK_PATTERN square centered at (cx, cz_face)."""
    hs = BACK_PATTERN / 2
    holes = np.zeros(X.shape, dtype=bool)
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        if into == "-Y":
            holes |= cyl_y(X, Y, Z, cx + dx, cz_face + dz, M3 / 2, cy - depth, cy + 1)
        elif into == "+Y":
            holes |= cyl_y(X, Y, Z, cx + dx, cz_face + dz, M3 / 2, cy - 1, cy + depth)
        elif into == "-Z":
            holes |= cyl_z(X, Y, Z, cx + dx, cy + dz, M3 / 2, cz_face - depth, cz_face + 1)
    return holes


# ---------------------------------------------------------------------------
# 1) Main cradle — EVO III open-shoulder silhouette
# ---------------------------------------------------------------------------

def build_cradle(pitch=0.9):
    """
    EVO-3 cues (original proportions, not a scan/copy):
      - no head side guards / open crown
      - reduced upper shoulder vs hip bolsters
      - stronger back rake
      - raised harness piercings
      - low front leg cushion lip
    """
    X, Y, Z, origin, pitch = grid((-72, -28, -6), (72, 88, 138), pitch)
    recline = -15.0  # EVO has aggressive rake
    Xr, Yr, Zr = rot_x(X, Y, Z, -recline, py=26.0, pz=12.0)

    solid = np.zeros(X.shape, dtype=bool)

    # Seat pan + low front cushion (EVO single-piece leg cushion cue)
    solid |= ell(Xr, Yr, Zr, 0, 36, 9, 56, 38, 11)
    solid |= box(Xr, Yr, Zr, -52, 12, 2, 52, 62, 15)
    solid |= ell(Xr, Yr, Zr, 0, 52, 8, 40, 18, 8)  # front lip

    # Backrest loft — wide at lumbar, tapering open shoulders, low crown
    for z, hw, dy, yc in [
        (24, 54, 20, 20),   # lower back / hip
        (45, 50, 18, 15),   # lumbar
        (65, 42, 15, 10),   # mid — shoulders start reducing
        (85, 32, 12, 6),    # open shoulder zone
        (105, 22, 10, 2),   # upper back
        (120, 14, 8, -1),   # crown — intentionally narrow, no wings
    ]:
        solid |= ell(Xr, Yr, Zr, 0, yc, z, hw, dy, 12)

    # Side bolsters — stronger at hips, fade before head height
    for s in (-1, 1):
        solid |= ell(Xr, Yr, Zr, s * 46, 28, 28, 15, 18, 22)
        solid |= ell(Xr, Yr, Zr, s * 40, 18, 55, 11, 14, 20)
        solid |= ell(Xr, Yr, Zr, s * 28, 10, 78, 7, 9, 12)  # fade out

    # Phone pocket
    hw, ht = PHONE_W / 2, PHONE_T / 2
    px, py, pz = 0.0, 24.0, 28.0
    solid &= ~box(Xr, Yr, Zr, px - hw, py - ht, pz, px + hw, py + ht, pz + PHONE_POCKET_H)
    # insertion mouth
    solid &= ~box(
        Xr, Yr, Zr,
        px - hw + 1, py + ht - 1, pz + 5,
        px + hw - 1, py + ht + 12, pz + PHONE_POCKET_H - 3,
    )
    # charge hole / notch at bottom center
    solid &= ~box(
        Xr, Yr, Zr,
        -CHARGE_W / 2, py + ht - 3, pz - 2,
        CHARGE_W / 2, py + ht + 10, pz + CHARGE_H,
    )
    # also pierce through floor slightly for cable drop
    solid &= ~cyl_z(Xr, Yr, Zr, 0, py + ht + 2, 5.0, pz - 4, pz + 6)

    # Raised harness piercings (EVO cue — decorative)
    for sx in (-24, 24):
        solid &= ~box(Xr, Yr, Zr, sx - 4, -2, 88, sx + 4, 10, 105)
    for sx in (-26, 26):
        solid &= ~cyl_z(Xr, Yr, Zr, sx, 34, 2.8, 8, 18)
    solid &= ~cyl_z(Xr, Yr, Zr, 0, 46, 2.8, 5, 15)

    # Back mounting boss (flat pad for modular backs) facing -Y
    solid |= box(Xr, Yr, Zr, -22, -14, 48, 22, -2, 88)
    # M3 pattern (carved in world-ish coords using reclined sample)
    solid &= ~m3_pattern_holes(Xr, Yr, Zr, 0, -8, 68, into="-Y", depth=12)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


# ---------------------------------------------------------------------------
# 2–3) Rail backs — vertical vs horizontal T-slot twist keys (4040-class)
# ---------------------------------------------------------------------------

def build_rail_back(orientation: str, pitch=0.7):
    """
    Plate that screws to cradle + twist-lock key for aluminum profile.

    orientation:
      'vertical'   — key aligned for upright 4040 posts
      'horizontal' — key rotated 90° for horizontal rails
    """
    X, Y, Z, origin, pitch = grid((-30, -8, -5), (30, 28, 50), pitch)
    solid = np.zeros(X.shape, dtype=bool)

    # Mount plate (mates to cradle boss)
    solid |= box(X, Y, Z, -20, 0, 0, 20, 5, 42)
    # countersink-ish pad
    solid |= box(X, Y, Z, -18, 0, 2, 18, 4, 40)

    # M3 through holes matching cradle (30 mm square, centered on plate)
    hs = BACK_PATTERN / 2
    cz = 21.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 8)

    # Twist key for ~8 mm T-slot (4040). Insert at 90°, rotate to lock.
    # Key sits on +Y face of plate.
    if orientation == "vertical":
        # Key long axis along Z (rail vertical)
        solid |= box(X, Y, Z, -3.6, 5, 8, 3.6, 11.5, 34)          # neck through slot opening
        solid |= box(X, Y, Z, -7.5, 11.0, 10, 7.5, 16.5, 32)       # locking wings
    else:
        # Key long axis along X (rail horizontal)
        solid |= box(X, Y, Z, -13, 5, 17.4, 13, 11.5, 24.6)        # neck
        solid |= box(X, Y, Z, -11, 11.0, 13.5, 11, 16.5, 28.5)     # locking wings

    # Small chamfer helpers via ellipsoid blend on wing tips
    if orientation == "vertical":
        solid |= ell(X, Y, Z, 0, 13.5, 21, 7.2, 3.2, 11)
    else:
        solid |= ell(X, Y, Z, 0, 13.5, 21, 11, 3.2, 7.2)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


# ---------------------------------------------------------------------------
# 4–5) Desk legs system
# ---------------------------------------------------------------------------

def build_leg_plate(pitch=0.7):
    """Back plate with 3× M3 leg sockets (tripod) + cradle M3 pattern."""
    X, Y, Z, origin, pitch = grid((-32, -8, -5), (32, 18, 50), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box(X, Y, Z, -22, 0, 0, 22, 6, 44)

    # Cradle screw pattern
    hs = BACK_PATTERN / 2
    cz = 22.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 9)

    # Three leg sockets (M3 threads / heat-set) pointing -Y / down when mounted
    # Arranged as wide tripod on the plate face
    for dx, dz in [(-14, 10), (14, 10), (0, 36)]:
        solid |= cyl_y(X, Y, Z, dx, dz, 5.5, 6, 14)  # boss
        solid &= ~cyl_y(X, Y, Z, dx, dz, M3 / 2, 5, 15)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


def build_desk_leg(pitch=0.55):
    """Single desk leg — print ×3. M3 stud clearance + foot pad."""
    X, Y, Z, origin, pitch = grid((-14, -14, -2), (14, 14, 55), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    # Tapered leg
    for z, r in [(0, 9), (8, 7), (30, 5), (45, 4.2)]:
        solid |= cyl_z(X, Y, Z, 0, 0, r, z, z + 8)
    # foot
    solid |= cyl_z(X, Y, Z, 0, 0, 10, 0, 3)
    # M3 hole from top
    solid &= ~cyl_z(X, Y, Z, 0, 0, M3 / 2, 35, 52)
    # hex nut trap near top
    solid &= ~cyl_z(X, Y, Z, 0, 0, 4.0, 38, 42)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


# ---------------------------------------------------------------------------
# 6–8) Kick-out + clamps (M3 / also fits M2 with sleeve)
# ---------------------------------------------------------------------------

def build_kickout_m3(pitch=0.65):
    """
    Back plate with a rearward kick-out tab and M3 hole.
    Bolt on a desk clamp or round tube clamp.
    Also includes the cradle M3 pattern.
    """
    X, Y, Z, origin, pitch = grid((-28, -8, -5), (28, 45, 50), pitch)
    solid = np.zeros(X.shape, dtype=bool)

    # Mount plate
    solid |= box(X, Y, Z, -20, 0, 0, 20, 5, 42)
    hs = BACK_PATTERN / 2
    cz = 21.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 8)

    # Kick-out arm (goes away from seat, +Y)
    solid |= box(X, Y, Z, -8, 5, 16, 8, 28, 28)
    solid |= ell(X, Y, Z, 0, 30, 22, 8, 10, 8)
    # M3 hole through kick-out (axis X — bolt sideways) AND Z option
    # Primary: hole along X so clamp can pivot
    solid &= ~cyl_x(X, Y, Z, 30, 22, M3 / 2, -12, 12)
    # Also a vertical M3 for alternate clamp orientation
    solid &= ~cyl_z(X, Y, Z, 0, 32, M3 / 2, 12, 32)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


def build_clamp_desk_m3(pitch=0.65):
    """Small desk-edge C-clamp, mates with M3 to kick-out."""
    X, Y, Z, origin, pitch = grid((-20, -8, -5), (40, 35, 30), pitch)
    solid = np.zeros(X.shape, dtype=bool)

    # C shape for desks up to ~22 mm thick
    solid |= box(X, Y, Z, 0, 0, 0, 28, 6, 22)       # top jaw
    solid |= box(X, Y, Z, 0, 0, 0, 6, 28, 22)       # spine
    solid |= box(X, Y, Z, 0, 22, 0, 28, 28, 22)     # bottom jaw
    # throat clearance
    solid &= ~box(X, Y, Z, 6, 6, -1, 30, 22, 23)

    # Thumb screw hole in bottom jaw (M5 suggested) + M3 ear for kick-out
    solid &= ~cyl_z(X, Y, Z, 18, 25, 2.65, -1, 30)  # M5 clearance for clamp screw
    # M3 ear
    solid |= box(X, Y, Z, -12, 8, 6, 0, 18, 16)
    solid &= ~cyl_x(X, Y, Z, 13, 11, M3 / 2, -14, 2)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


def build_clamp_tube_m3(tube_od=40.4, pitch=0.65):
    """Two-ear round clamp for tubular sim rigs; M3 pivot to kick-out."""
    X, Y, Z, origin, pitch = grid((-40, -40, -5), (40, 40, 28), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    r_out = tube_od / 2 + 4.2
    r_in = tube_od / 2 + 0.2

    # Full ring then split — we output ONE half; print ×2
    solid |= cyl_z(X, Y, Z, 0, 0, r_out, 0, 22)
    solid &= ~cyl_z(X, Y, Z, 0, 0, r_in, -1, 23)
    solid &= Y >= -0.8  # half

    # Bolt ears
    for s in (-1, 1):
        ex = s * (r_out + 7)
        solid |= box(X, Y, Z, ex - 6, -1, 0, ex + 6, 5, 22)
        solid &= ~cyl_z(X, Y, Z, ex, 2, 2.65, -1, 23)  # M5 clamp bolts

    # M3 pivot tab toward +Y
    solid |= box(X, Y, Z, -6, r_out - 1, 5, 6, r_out + 12, 17)
    solid &= ~cyl_x(X, Y, Z, r_out + 6, 11, M3 / 2, -8, 8)

    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


# ---------------------------------------------------------------------------
# Blank back (just holes — customer adds own legs / hardware)
# ---------------------------------------------------------------------------

def build_blank_back(pitch=0.7):
    X, Y, Z, origin, pitch = grid((-28, -6, -4), (28, 12, 48), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box(X, Y, Z, -20, 0, 0, 20, 5, 42)
    hs = BACK_PATTERN / 2
    cz = 21.0
    for dx, dz in [(-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs)]:
        solid &= ~cyl_y(X, Y, Z, dx, cz + dz, M3 / 2, -1, 8)
    # Extra 4 peripheral holes for DIY legs (M3)
    for dx, dz in [(-14, 8), (14, 8), (-14, 34), (14, 34)]:
        solid &= ~cyl_y(X, Y, Z, dx, dz, M3 / 2, -1, 8)
    verts, faces = voxel_surface(solid, pitch, origin)
    return center_on_bed(verts), faces


def main():
    print("Building modular EVO-style cradle kit...\n")

    parts = [
        ("01_cradle_evo.stl", lambda: build_cradle(0.9)),
        ("02_back_rail_vertical.stl", lambda: build_rail_back("vertical")),
        ("03_back_rail_horizontal.stl", lambda: build_rail_back("horizontal")),
        ("04_back_leg_plate.stl", build_leg_plate),
        ("05_desk_leg.stl", build_desk_leg),
        ("06_back_kickout_m3.stl", build_kickout_m3),
        ("07_clamp_desk_m3.stl", build_clamp_desk_m3),
        ("08_clamp_tube40_m3.stl", build_clamp_tube_m3),
        ("09_back_blank_diy.stl", build_blank_back),
    ]

    for name, fn in parts:
        print(f"→ {name}")
        v, f = fn()
        write_stl(OUT / name, v, f, name.replace(".stl", ""))

    # Remove obsolete one-piece files from v2 if present
    for old in [
        "seat_cradle.stl",
        "clamp_40mm_front.stl",
        "clamp_40mm_rear.stl",
        "adapter_4040.stl",
        "desk_stand_base.stl",
    ]:
        p = OUT / old
        if p.exists():
            p.unlink()
            print(f"  removed obsolete {old}")

    print("\nDone.")


if __name__ == "__main__":
    main()
