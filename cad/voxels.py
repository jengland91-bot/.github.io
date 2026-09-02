"""Voxel CSG and greedy-quad STL export. Units are millimetres."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np


class Voxels:
    def __init__(self, bounds, pitch=0.25, pad=1):
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        self.pitch = float(pitch)
        self.origin = np.array(
            [xmin - pad * pitch, ymin - pad * pitch, zmin - pad * pitch],
            dtype=np.float64,
        )
        self.nx = int(np.ceil((xmax - xmin) / pitch)) + 2 * pad
        self.ny = int(np.ceil((ymax - ymin) / pitch)) + 2 * pad
        self.nz = int(np.ceil((zmax - zmin) / pitch)) + 2 * pad
        self.occ = np.zeros((self.nx, self.ny, self.nz), dtype=np.uint8)

    def _axis_range(self, a0, a1, origin, n):
        i0 = int(np.floor((a0 - origin) / self.pitch))
        i1 = int(np.ceil((a1 - origin) / self.pitch))
        return max(0, i0), min(n, i1)

    def _xyz_ranges(self, x0, x1, y0, y1, z0, z1):
        i0, i1 = self._axis_range(x0, x1, self.origin[0], self.nx)
        j0, j1 = self._axis_range(y0, y1, self.origin[1], self.ny)
        k0, k1 = self._axis_range(z0, z1, self.origin[2], self.nz)
        return i0, i1, j0, j1, k0, k1

    def _coords(self, i0, i1, j0, j1):
        xs = self.origin[0] + (np.arange(i0, i1) + 0.5) * self.pitch
        ys = self.origin[1] + (np.arange(j0, j1) + 0.5) * self.pitch
        return np.meshgrid(xs, ys, indexing="ij")

    def add_box(self, x0, x1, y0, y1, z0, z1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(x0, x1, y0, y1, z0, z1)
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        self.occ[i0:i1, j0:j1, k0:k1] = 1

    def sub_box(self, x0, x1, y0, y1, z0, z1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(x0, x1, y0, y1, z0, z1)
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        self.occ[i0:i1, j0:j1, k0:k1] = 0

    def _apply_mask(self, i0, i1, j0, j1, k0, k1, mask, add=True):
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        sl = self.occ[i0:i1, j0:j1, k0:k1]
        m = mask[:, :, None]
        if add:
            sl |= m
        else:
            sl &= ~m

    def add_cyl_z(self, cx, cy, r, z0, z1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(cx - r, cx + r, cy - r, cy + r, z0, z1)
        X, Y = self._coords(i0, i1, j0, j1)
        self._apply_mask(i0, i1, j0, j1, k0, k1, (X - cx) ** 2 + (Y - cy) ** 2 <= r * r, True)

    def sub_cyl_z(self, cx, cy, r, z0, z1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(cx - r, cx + r, cy - r, cy + r, z0, z1)
        X, Y = self._coords(i0, i1, j0, j1)
        self._apply_mask(i0, i1, j0, j1, k0, k1, (X - cx) ** 2 + (Y - cy) ** 2 <= r * r, False)

    def add_cyl_x(self, cy, cz, r, x0, x1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(x0, x1, cy - r, cy + r, cz - r, cz + r)
        ys = self.origin[1] + (np.arange(j0, j1) + 0.5) * self.pitch
        zs = self.origin[2] + (np.arange(k0, k1) + 0.5) * self.pitch
        Y, Z = np.meshgrid(ys, zs, indexing="ij")
        mask = (Y - cy) ** 2 + (Z - cz) ** 2 <= r * r
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        sl = self.occ[i0:i1, j0:j1, k0:k1]
        sl |= mask[None, :, :]

    def sub_cyl_x(self, cy, cz, r, x0, x1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(x0, x1, cy - r, cy + r, cz - r, cz + r)
        ys = self.origin[1] + (np.arange(j0, j1) + 0.5) * self.pitch
        zs = self.origin[2] + (np.arange(k0, k1) + 0.5) * self.pitch
        Y, Z = np.meshgrid(ys, zs, indexing="ij")
        mask = (Y - cy) ** 2 + (Z - cz) ** 2 <= r * r
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        sl = self.occ[i0:i1, j0:j1, k0:k1]
        sl &= ~mask[None, :, :]

    def add_cyl_y(self, cx, cz, r, y0, y1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(cx - r, cx + r, y0, y1, cz - r, cz + r)
        xs = self.origin[0] + (np.arange(i0, i1) + 0.5) * self.pitch
        zs = self.origin[2] + (np.arange(k0, k1) + 0.5) * self.pitch
        X, Z = np.meshgrid(xs, zs, indexing="ij")
        mask = (X - cx) ** 2 + (Z - cz) ** 2 <= r * r
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        sl = self.occ[i0:i1, j0:j1, k0:k1]
        sl |= mask[:, None, :]

    def sub_cyl_y(self, cx, cz, r, y0, y1):
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(cx - r, cx + r, y0, y1, cz - r, cz + r)
        xs = self.origin[0] + (np.arange(i0, i1) + 0.5) * self.pitch
        zs = self.origin[2] + (np.arange(k0, k1) + 0.5) * self.pitch
        X, Z = np.meshgrid(xs, zs, indexing="ij")
        mask = (X - cx) ** 2 + (Z - cz) ** 2 <= r * r
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            return
        sl = self.occ[i0:i1, j0:j1, k0:k1]
        sl &= ~mask[:, None, :]

    def add_rounded_box_z(self, cx, cy, w, h, r, z0, z1):
        self._rounded_box_z(cx, cy, w, h, r, z0, z1, True)

    def sub_rounded_box_z(self, cx, cy, w, h, r, z0, z1):
        self._rounded_box_z(cx, cy, w, h, r, z0, z1, False)

    def _rounded_box_z(self, cx, cy, w, h, r, z0, z1, add):
        r = min(r, w / 2 - 0.05, h / 2 - 0.05)
        r = max(r, 0.0)
        hx, hy = w / 2, h / 2
        i0, i1, j0, j1, k0, k1 = self._xyz_ranges(cx - hx, cx + hx, cy - hy, cy + hy, z0, z1)
        X, Y = self._coords(i0, i1, j0, j1)
        # SDF of rounded box: q = abs(p) - b + r; length(max(q,0)) + min(max(q.x,q.y),0) - r
        qx = np.abs(X - cx) - hx + r
        qy = np.abs(Y - cy) - hy + r
        outside = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2)
        inside = np.minimum(np.maximum(qx, qy), 0)
        mask = (outside + inside - r) <= 0
        self._apply_mask(i0, i1, j0, j1, k0, k1, mask, add)

    def occupied(self):
        return int(self.occ.sum())

    def to_stl(self, path: Path, name="part"):
        tris = greedy_triangles(self.occ, self.origin, self.pitch)
        write_binary_stl(path, tris, name)
        return len(tris)


def greedy_2d(mask: np.ndarray):
    """Merge a 2D bool mask into (x, y, w, h) rectangles."""
    used = np.zeros_like(mask, dtype=bool)
    ny, nx = mask.shape
    rects = []
    for y in range(ny):
        x = 0
        row = mask[y]
        used_row = used[y]
        while x < nx:
            if not row[x] or used_row[x]:
                x += 1
                continue
            x2 = x + 1
            while x2 < nx and row[x2] and not used_row[x2]:
                x2 += 1
            y2 = y + 1
            while y2 < ny:
                sl = mask[y2, x:x2]
                us = used[y2, x:x2]
                if not sl.all() or us.any():
                    break
                y2 += 1
            used[y:y2, x:x2] = True
            rects.append((x, y, x2 - x, y2 - y))
            x = x2
    return rects


def greedy_triangles(occ: np.ndarray, origin, pitch):
    """Boundary of a voxel occupancy grid as triangles with outward normals."""
    nx, ny, nz = occ.shape
    tris = []
    o = origin
    p = pitch

    def quad(a, b, c, d):
        tris.append((a, b, c))
        tris.append((a, c, d))

    for i in range(nx - 1):
        sl = occ[i] & ~occ[i + 1]  # (ny, nz)
        if not sl.any():
            continue
        x = o[0] + (i + 1) * p
        for j, k, dj, dk in _rects_jk(sl):
            y0, y1 = o[1] + j * p, o[1] + (j + dj) * p
            z0, z1 = o[2] + k * p, o[2] + (k + dk) * p
            a = (x, y0, z0)
            b = (x, y1, z0)
            c = (x, y1, z1)
            d = (x, y0, z1)
            quad(a, b, c, d)  # +X : (0,dy,0) x (0,0,dz) wait let's verify later

    for i in range(nx - 1):
        sl = ~occ[i] & occ[i + 1]
        if not sl.any():
            continue
        x = o[0] + (i + 1) * p
        for j, k, dj, dk in _rects_jk(sl):
            y0, y1 = o[1] + j * p, o[1] + (j + dj) * p
            z0, z1 = o[2] + k * p, o[2] + (k + dk) * p
            a = (x, y0, z0)
            b = (x, y0, z1)
            c = (x, y1, z1)
            d = (x, y1, z0)
            quad(a, b, c, d)

    for j in range(ny - 1):
        sl = occ[:, j, :] & ~occ[:, j + 1, :]  # (nx, nz)
        if not sl.any():
            continue
        y = o[1] + (j + 1) * p
        for i, k, di, dk in _rects_jk(sl):
            x0, x1 = o[0] + i * p, o[0] + (i + di) * p
            z0, z1 = o[2] + k * p, o[2] + (k + dk) * p
            a = (x0, y, z0)
            b = (x0, y, z1)
            c = (x1, y, z1)
            d = (x1, y, z0)
            quad(a, b, c, d)

    for j in range(ny - 1):
        sl = ~occ[:, j, :] & occ[:, j + 1, :]
        if not sl.any():
            continue
        y = o[1] + (j + 1) * p
        for i, k, di, dk in _rects_jk(sl):
            x0, x1 = o[0] + i * p, o[0] + (i + di) * p
            z0, z1 = o[2] + k * p, o[2] + (k + dk) * p
            a = (x0, y, z0)
            b = (x1, y, z0)
            c = (x1, y, z1)
            d = (x0, y, z1)
            quad(a, b, c, d)

    for k in range(nz - 1):
        sl = occ[:, :, k] & ~occ[:, :, k + 1]  # (nx, ny)
        if not sl.any():
            continue
        z = o[2] + (k + 1) * p
        for i, j, di, dj in _rects_jk(sl):
            x0, x1 = o[0] + i * p, o[0] + (i + di) * p
            y0, y1 = o[1] + j * p, o[1] + (j + dj) * p
            a = (x0, y0, z)
            b = (x1, y0, z)
            c = (x1, y1, z)
            d = (x0, y1, z)
            quad(a, b, c, d)

    for k in range(nz - 1):
        sl = ~occ[:, :, k] & occ[:, :, k + 1]
        if not sl.any():
            continue
        z = o[2] + (k + 1) * p
        for i, j, di, dj in _rects_jk(sl):
            x0, x1 = o[0] + i * p, o[0] + (i + di) * p
            y0, y1 = o[1] + j * p, o[1] + (j + dj) * p
            a = (x0, y0, z)
            b = (x0, y1, z)
            c = (x1, y1, z)
            d = (x1, y0, z)
            quad(a, b, c, d)

    return tris


def _rects_jk(mask_2d):
    """mask[a, b] -> rectangles (a0, b0, da, db)."""
    used = np.zeros_like(mask_2d, dtype=bool)
    na, nb = mask_2d.shape
    out = []
    for a in range(na):
        b = 0
        while b < nb:
            if not mask_2d[a, b] or used[a, b]:
                b += 1
                continue
            b2 = b + 1
            while b2 < nb and mask_2d[a, b2] and not used[a, b2]:
                b2 += 1
            a2 = a + 1
            while a2 < na:
                if not mask_2d[a2, b:b2].all() or used[a2, b:b2].any():
                    break
                a2 += 1
            used[a:a2, b:b2] = True
            out.append((a, b, a2 - a, b2 - b))
            b = b2
    return out


def write_binary_stl(path: Path, tris, name="part"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = name.encode("ascii", "replace")[:80].ljust(80, b"\0")
    n = len(tris)
    buf = bytearray()
    buf.extend(header)
    buf.extend(struct.pack("<I", n))
    pack = struct.Struct("<12fH").pack
    for a, b, c in tris:
        ux = b[0] - a[0]
        uy = b[1] - a[1]
        uz = b[2] - a[2]
        vx = c[0] - a[0]
        vy = c[1] - a[1]
        vz = c[2] - a[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        ln = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
        buf.extend(
            pack(
                nx / ln,
                ny / ln,
                nz / ln,
                a[0],
                a[1],
                a[2],
                b[0],
                b[1],
                b[2],
                c[0],
                c[1],
                c[2],
                0,
            )
        )
    path.write_bytes(buf)


def bounds_of_tris(tris):
    if not tris:
        return None
    pts = np.array([p for t in tris for p in t], dtype=np.float64)
    return pts.min(axis=0), pts.max(axis=0)
