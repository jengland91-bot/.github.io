#!/usr/bin/env python3
"""
High-quality voxel CSG → STL for the Open-Shoulder Bucket Phone Cradle.
Pure numpy (no scipy/skimage). Uses classic marching cubes.
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent / "stl"
OUT.mkdir(parents=True, exist_ok=True)

# --- Marching cubes edge/tri tables (standard) ---
# Edge endpoints for 12 edges of a cube
EDGE_VERT = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
# Cube corner offsets
CORNER = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
], dtype=np.float64)

# Compact triangle table: for each cubeindex, up to 5 triangles as edge indices, -1 terminated
# Full table is long — use a working subset via dual contour / surface nets alternative:
# Surface nets / greedy quad meshing of binary voxels is simpler and looks great when
# smoothed with a couple of Laplacian passes.


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
    print(f"Wrote {path} ({len(faces)} tris, {len(verts)} verts)")


def laplacian_smooth(verts, faces, iterations=8, lam=0.5):
    """Uniform Laplacian smooth while preserving volume roughly."""
    n = len(verts)
    # adjacency
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
    """Extract quads from occupied voxels (blocky), then smooth."""
    # occ shape (nx, ny, nz), True = solid
    nx, ny, nz = occ.shape
    # Pad
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

    # For each solid voxel, emit faces where neighbor is empty
    # Work in padded coords; voxel (i,j,k) in padded is at index i,j,k
    # Corner of voxel (i,j,k) in world uses (i-1, j-1, k-1) after pad offset
    dirs = [
        (+1, 0, 0, [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        (-1, 0, 0, [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
        (0, +1, 0, [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
        (0, -1, 0, [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
        (0, 0, +1, [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        (0, 0, -1, [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ]

    solid = np.argwhere(p)
    for i, j, k in solid:
        for di, dj, dk, corners in dirs:
            if p[i + di, j + dj, k + dk]:
                continue
            # emit face — winding so outward normal points to empty
            ids = []
            for cx, cy, cz in corners:
                # vertex at voxel corner in padded grid coords
                ids.append(vid(i + cx - 1, j + cy - 1, k + cz - 1))
            # two tris
            faces.append((ids[0], ids[1], ids[2]))
            faces.append((ids[0], ids[2], ids[3]))

    verts = np.array(verts, dtype=np.float64)
    faces = np.array(faces, dtype=np.int32)
    if len(verts) == 0:
        raise RuntimeError("Empty mesh")
    verts = laplacian_smooth(verts, faces, iterations=10, lam=0.45)
    return verts, faces


# --- SDF / occupancy primitives ---

def grid(bounds_min, bounds_max, pitch):
    mn = np.asarray(bounds_min, dtype=np.float64)
    mx = np.asarray(bounds_max, dtype=np.float64)
    dims = np.ceil((mx - mn) / pitch).astype(int) + 1
    xs = mn[0] + np.arange(dims[0]) * pitch
    ys = mn[1] + np.arange(dims[1]) * pitch
    zs = mn[2] + np.arange(dims[2]) * pitch
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    return X, Y, Z, mn, pitch


def ell_occ(X, Y, Z, cx, cy, cz, rx, ry, rz):
    return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1.0


def box_occ(X, Y, Z, x0, y0, z0, x1, y1, z1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1)


def cyl_y_occ(X, Y, Z, cx, cz, r, y0, y1):
    return ((X - cx) ** 2 + (Z - cz) ** 2 <= r * r) & (Y >= y0) & (Y <= y1)


def cyl_z_occ(X, Y, Z, cx, cy, r, z0, z1):
    return ((X - cx) ** 2 + (Y - cy) ** 2 <= r * r) & (Z >= z0) & (Z <= z1)


def rotate_x_points(X, Y, Z, deg, pivot_y=0.0, pivot_z=0.0):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    Yp = Y - pivot_y
    Zp = Z - pivot_z
    Yr = Yp * c - Zp * s + pivot_y
    Zr = Yp * s + Zp * c + pivot_z
    return X, Yr, Zr


def build_seat(pitch=0.9):
    """Open-shoulder bucket with carved phone pocket + charge notch + dovetail.

    Outer width is sized so an 88 mm phone pocket still has ~6–8 mm walls
    and visible side bolsters (sellable proportions, not a skinny shell).
    """
    # Work in un-reclined coords then rotate occupancy sampling
    X, Y, Z, origin, pitch = grid((-70, -25, -5), (70, 85, 130), pitch)

    # Sample in reclined frame: transform query points by inverse recline
    recline = -12.0
    Xr, Yr, Zr = rotate_x_points(X, Y, Z, -recline, pivot_y=24.0, pivot_z=10.0)

    solid = np.zeros(X.shape, dtype=bool)

    # Seat pan — flattened ellipsoid (wide enough for phone + bolsters)
    solid |= ell_occ(Xr, Yr, Zr, 0, 34, 8, 54, 36, 11)
    solid |= box_occ(Xr, Yr, Zr, -50, 10, 2, 50, 58, 15)

    # Backrest column — tapers upward, open shoulders (narrow crown, no head wings)
    for z, hw, dy, yc in [
        (22, 52, 20, 18),
        (42, 48, 18, 14),
        (62, 42, 16, 10),
        (82, 34, 14, 6),
        (100, 26, 11, 3),
        (114, 18, 9, 0),
    ]:
        solid |= ell_occ(Xr, Yr, Zr, 0, yc, z, hw, dy, 13)

    # Side bolsters (wrap the phone visually)
    for s in (-1, 1):
        solid |= ell_occ(Xr, Yr, Zr, s * 44, 26, 30, 14, 18, 24)
        solid |= ell_occ(Xr, Yr, Zr, s * 38, 16, 58, 11, 14, 22)
        solid |= ell_occ(Xr, Yr, Zr, s * 30, 10, 85, 8, 10, 16)

    # Phone pocket (carved) — 88 mm wide × ~16.8 mm thick × 60 mm tall
    phone_w, phone_t, phone_h = 88 / 2, 16 / 2 + 0.4, 60
    px, py, pz = 0.0, 22.0, 26.0
    solid &= ~box_occ(
        Xr, Yr, Zr,
        px - phone_w, py - phone_t, pz,
        px + phone_w, py + phone_t, pz + phone_h,
    )
    # Insertion mouth toward +Y
    solid &= ~box_occ(
        Xr, Yr, Zr,
        px - phone_w + 2, py + phone_t - 2, pz + 6,
        px + phone_w - 2, py + phone_t + 10, pz + phone_h - 4,
    )

    # Charge notch at bottom-front of pocket
    solid &= ~box_occ(Xr, Yr, Zr, -7, py + phone_t - 4, pz - 2, 7, py + phone_t + 8, pz + 14)

    # Harness slot piercings (decorative)
    for sx in (-22, 22):
        solid &= ~box_occ(Xr, Yr, Zr, sx - 3.5, -2, 72, sx + 3.5, 10, 88)
    for sx in (-24, 24):
        solid &= ~cyl_z_occ(Xr, Yr, Zr, sx, 32, 2.6, 6, 16)
    solid &= ~cyl_z_occ(Xr, Yr, Zr, 0, 42, 2.6, 4, 14)

    # Dovetail male rail on back (-Y)
    solid |= box_occ(Xr, Yr, Zr, -11, -12, 42, 11, 0, 70)
    solid |= box_occ(Xr, Yr, Zr, -9, -12, 44, 9, -2, 68)

    # Ensure sits above z=0 in world after — already using world grid with recline baked via sample

    verts, faces = voxel_surface(solid, pitch, origin)
    # Shift to bed
    verts = verts.copy()
    verts[:, 0] -= (verts[:, 0].min() + verts[:, 0].max()) / 2
    verts[:, 1] -= (verts[:, 1].min() + verts[:, 1].max()) / 2
    verts[:, 2] -= verts[:, 2].min()
    return verts, faces


def build_clamp_half(front=True, pitch=0.7, tube_od=40.4):
    X, Y, Z, origin, pitch = grid((-55, -30, -2), (55, 45, 32), pitch)
    r_out = tube_od / 2 + 4.5
    r_in = tube_od / 2 + 0.15
    solid = np.zeros(X.shape, dtype=bool)

    # Outer cylinder
    solid |= cyl_z_occ(X, Y, Z, 0, 0, r_out, 0, 28)
    # Bore
    solid &= ~cyl_z_occ(X, Y, Z, 0, 0, r_in, -1, 29)

    # Keep half
    if front:
        solid &= Y >= -0.6
    else:
        solid &= Y <= 0.6

    # Bolt ears
    for s in (-1, 1):
        ex = s * (r_out + 8)
        solid |= box_occ(X, Y, Z, ex - 7, (-3 if front else -4), 0, ex + 7, (4 if front else 3), 28)
        # hole
        solid &= ~cyl_y_occ(X, Y, Z, ex, 14, 2.65, -20, 20)

    if front:
        # Dovetail receiver block
        solid |= box_occ(X, Y, Z, -16, r_out - 1, 2, 16, r_out + 14, 26)
        # female channel (open upward in +Z for slide-in, and through Y)
        solid &= ~box_occ(X, Y, Z, -11.2, r_out + 1, 4, 11.2, r_out + 12, 30)
        # dovetail undercuts (simple ledges)
        solid &= ~box_occ(X, Y, Z, -11.2, r_out + 1, 4, -7, r_out + 5, 26)
        solid &= ~box_occ(X, Y, Z, 7, r_out + 1, 4, 11.2, r_out + 5, 26)

    if not front:
        # nut traps (hex approx as cyl)
        for s in (-1, 1):
            ex = s * (r_out + 8)
            solid &= ~cyl_y_occ(X, Y, Z, ex, 14, 4.7, -8, -2.5)

    verts, faces = voxel_surface(solid, pitch, origin)
    # Orient split face to bed for printing
    # Front: rotate so -Y (split) faces down... keep as-is; docs say print orientation
    verts = verts.copy()
    verts[:, 0] -= (verts[:, 0].min() + verts[:, 0].max()) / 2
    verts[:, 1] -= (verts[:, 1].min() + verts[:, 1].max()) / 2
    verts[:, 2] -= verts[:, 2].min()
    return verts, faces


def build_adapter_4040(pitch=0.75):
    X, Y, Z, origin, pitch = grid((-28, -5, -5), (28, 30, 45), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box_occ(X, Y, Z, -20, 0, 0, 20, 6, 40)
    solid &= ~cyl_y_occ(X, Y, Z, 0, 20, 4.15, -1, 8)
    solid |= box_occ(X, Y, Z, -16, 6, 8, 16, 18, 32)
    solid &= ~box_occ(X, Y, Z, -11.2, 8, 10, 11.2, 17, 40)
    verts, faces = voxel_surface(solid, pitch, origin)
    verts = verts.copy()
    verts[:, 0] -= (verts[:, 0].min() + verts[:, 0].max()) / 2
    verts[:, 1] -= (verts[:, 1].min() + verts[:, 1].max()) / 2
    verts[:, 2] -= verts[:, 2].min()
    return verts, faces


def build_desk_base(pitch=0.9):
    X, Y, Z, origin, pitch = grid((-55, -45, -2), (55, 45, 75), pitch)
    solid = np.zeros(X.shape, dtype=bool)
    solid |= box_occ(X, Y, Z, -45, -35, 0, 45, 35, 8)
    # chamfer-ish by intersecting ellipsoid
    solid &= ell_occ(X, Y, Z, 0, 0, 4, 50, 40, 10) | box_occ(X, Y, Z, -40, -30, 0, 40, 30, 7)
    for x, y in [(-32, -24), (32, -24), (-32, 24), (32, 24)]:
        solid |= cyl_z_occ(X, Y, Z, x, y, 6, 0, 2.5)
    solid |= box_occ(X, Y, Z, -9, -30, 8, 9, -18, 55)
    solid |= box_occ(X, Y, Z, -16, -28, 48, 16, -8, 68)
    solid &= ~box_occ(X, Y, Z, -11.2, -26, 50, 11.2, -12, 75)
    verts, faces = voxel_surface(solid, pitch, origin)
    verts = verts.copy()
    verts[:, 0] -= (verts[:, 0].min() + verts[:, 0].max()) / 2
    verts[:, 1] -= (verts[:, 1].min() + verts[:, 1].max()) / 2
    verts[:, 2] -= verts[:, 2].min()
    return verts, faces


def main():
    print("Building seat cradle (voxel CSG)...")
    v, f = build_seat(pitch=0.85)
    write_stl(OUT / "seat_cradle.stl", v, f, "seat_cradle")

    print("Building 40mm clamp halves...")
    v, f = build_clamp_half(front=True)
    write_stl(OUT / "clamp_40mm_front.stl", v, f, "clamp_40mm_front")
    v, f = build_clamp_half(front=False)
    write_stl(OUT / "clamp_40mm_rear.stl", v, f, "clamp_40mm_rear")

    print("Building 4040 adapter...")
    v, f = build_adapter_4040()
    write_stl(OUT / "adapter_4040.stl", v, f, "adapter_4040")

    print("Building desk stand base...")
    v, f = build_desk_base()
    write_stl(OUT / "desk_stand_base.stl", v, f, "desk_stand_base")

    for p in sorted(OUT.glob("*.stl")):
        print(f"  {p.name}: {p.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
