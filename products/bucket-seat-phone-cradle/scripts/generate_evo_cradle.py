#!/usr/bin/env python3
"""
Sparco EVO–style bucket phone cradle — faceted shell (v4)
========================================================
Explicit panel geometry (not voxel blobs). Reference cues from EVO bucket:
  - rounded headrest crown
  - twin trapezoid harness openings + bezels
  - shoulder wings that flare then tuck
  - recessed centre back / seat pad
  - deep thigh bolsters + front lip
  - vertical spine on rear shell

Phone: iPhone 18 Pro Max + case (92 × 18 mm), charge notch at bottom.
Backs unchanged — same 4× M3 pattern on flat boss.
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "stl"
OUT.mkdir(parents=True, exist_ok=True)

PHONE_W = 92.0
PHONE_T = 18.0
PHONE_H = 62.0
CHARGE_W = 14.0
M3 = 3.2
BACK_PATTERN = 30.0


# ---------------------------------------------------------------------------
# Mesh builder
# ---------------------------------------------------------------------------

class Mesh:
    def __init__(self):
        self.verts: list[np.ndarray] = []
        self.faces: list[tuple[int, int, int]] = []
        self._key: dict[tuple, int] = {}

    def v(self, x, y, z) -> int:
        k = (round(x, 3), round(y, 3), round(z, 3))
        if k not in self._key:
            self._key[k] = len(self.verts)
            self.verts.append(np.array([x, y, z], dtype=np.float64))
        return self._key[k]

    def tri(self, a, b, c):
        self.faces.append((a, b, c))

    def quad(self, a, b, c, d):
        self.tri(a, b, c)
        self.tri(a, c, d)

    def extend(self, other: "Mesh"):
        remap = {}
        for i, p in enumerate(other.verts):
            remap[i] = self.v(*p)
        for a, b, c in other.faces:
            self.tri(remap[a], remap[b], remap[c])

    def to_arrays(self):
        return np.array(self.verts), np.array(self.faces, dtype=np.int32)

    def write_stl(self, path: Path, name: str = "part"):
        verts, faces = self.to_arrays()
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
        print(f"  {path.name:36s}  {len(faces):6d} tris  {path.stat().st_size/1024:7.1f} KiB")


def center_bed(m: Mesh) -> Mesh:
    if not m.verts:
        return m
    v = np.array(m.verts)
    mn, mx = v.min(0), v.max(0)
    mid = (mn + mx) / 2
    shift = np.array([-mid[0], -mid[1], -mn[2]])
    m2 = Mesh()
    idx_map: dict[int, int] = {}
    for old_i, p in enumerate(m.verts):
        idx_map[old_i] = m2.v(*(p + shift))
    for a, b, c in m.faces:
        m2.tri(idx_map[a], idx_map[b], idx_map[c])
    return m2


def loft_rings(rings: list[list[tuple]], cap_bottom=False, cap_top=False):
    """Loft closed rings (same point count). Each point is (x,y,z)."""
    m = Mesh()
    n = len(rings[0])
    for r in rings:
        assert len(r) == n

    for ri in range(len(rings) - 1):
        a, b = rings[ri], rings[ri + 1]
        for i in range(n):
            j = (i + 1) % n
            m.quad(m.v(*a[i]), m.v(*a[j]), m.v(*b[j]), m.v(*b[i]))

    if cap_bottom and len(rings) >= 2:
        c = np.mean(rings[0], axis=0)
        ci = m.v(*c)
        for i in range(n):
            j = (i + 1) % n
            m.tri(ci, m.v(*rings[0][j]), m.v(*rings[0][i]))

    if cap_top and len(rings) >= 2:
        c = np.mean(rings[-1], axis=0)
        ci = m.v(*c)
        for i in range(n):
            j = (i + 1) % n
            m.tri(ci, m.v(*rings[-1][i]), m.v(*rings[-1][j]))
    return m


def ring_rounded_rect(cx, cy, cz, hw, hd, r=4, n=12):
    """Rounded rectangle in X-Y at fixed Z (CCW from +X)."""
    pts = []
    corners = [
        (cx + hw - r, cy + hd - r),
        (cx - hw + r, cy + hd - r),
        (cx - hw + r, cy - hd + r),
        (cx + hw - r, cy - hd + r),
    ]
    for ci, (px, py) in enumerate(corners):
        a0 = ci * math.pi / 2 + math.pi / 4
        a1 = a0 + math.pi / 2
        for k in range(n // 4 + 1):
            t = k / (n // 4)
            a = a0 + t * (a1 - a0)
            pts.append((px + r * math.cos(a), py + r * math.sin(a), cz))
    return pts[:n]


def ring_trapezoid(cx, cy, cz, top_w, bot_w, h, depth=3, n=4):
    """Trapezoid bezel frame (harness hole trim)."""
    tw, bw = top_w / 2, bot_w / 2
    hh = h / 2
    # outer
    outer = [
        (cx - tw, cy + depth, cz + hh),
        (cx + tw, cy + depth, cz + hh),
        (cx + bw, cy + depth, cz - hh),
        (cx - bw, cy + depth, cz - hh),
    ]
    return outer


def _harness_void(cx, cz, top_w, bot_w, h, y0, y1):
    """Open trapezoid tunnel through the shell."""
    m = Mesh()
    tw, bw, hh = top_w / 2, bot_w / 2, h / 2
    back = [
        (cx - tw, y0, cz + hh),
        (cx + tw, y0, cz + hh),
        (cx + bw, y0, cz - hh),
        (cx - bw, y0, cz - hh),
    ]
    front = [(p[0], y1, p[2]) for p in back]
    for k in range(4):
        j = (k + 1) % 4
        m.quad(m.v(*back[k]), m.v(*back[j]), m.v(*front[j]), m.v(*front[k]))
    return m


def build_harness_bezel(cx, cz, top_w=24, bot_w=17, h=13, depth=5):
    """Trapezoid frame (harness hole surround)."""
    m = Mesh()
    tw, bw, hh = top_w / 2, bot_w / 2, h / 2
    y0, y1 = 38, 38 + depth
    # outer front
    o = [
        (cx - tw, y1, cz + hh),
        (cx + tw, y1, cz + hh),
        (cx + bw, y1, cz - hh),
        (cx - bw, y1, cz - hh),
    ]
    # inner
    inset = 3.2
    i = [
        (cx - tw + inset, y1, cz + hh - inset * 0.6),
        (cx + tw - inset, y1, cz + hh - inset * 0.6),
        (cx + bw - inset, y1, cz - hh + inset * 0.6),
        (cx - bw + inset, y1, cz - hh + inset * 0.6),
    ]
    # extrude bezel y0..y1
    for a, b in zip(o, o[1:] + o[:1]):
        pass
    for k in range(4):
        j = (k + 1) % 4
        m.quad(m.v(*o[k]), m.v(*o[j]), m.v(*(o[j][0], y0, o[j][2])), m.v(*(o[k][0], y0, o[k][2])))
    # front face (frame only — quad ring)
    for k in range(4):
        j = (k + 1) % 4
        m.quad(m.v(*o[k]), m.v(*o[j]), m.v(*i[j]), m.v(*i[k]))
    return m


def profile_front_xz(z, hw_outer, hw_inner, y_front):
    """Return (x,y,z) points on front silhouette at height z."""
    return hw_outer, hw_inner, y_front


# ---------------------------------------------------------------------------
# EVO cradle shell
# ---------------------------------------------------------------------------

def build_evo_cradle() -> Mesh:
    m = Mesh()

    # --- Scale & key heights ---
    # Z: 0 = seat base, 138 = headrest top
    # Y: 0 = back shell, 48 = front lip
    # X: shoulder max ~ ±58

    def shell_ring(z, hw, y_back, y_front, n=16, squash=1.0):
        """Outer shell cross-section: back line + front arc."""
        pts = []
        # back centre spine inset
        spine_x = 0
        for i in range(n):
            t = i / n
            ang = math.pi * (1 - t)  # pi..0 left to right over front
            x = spine_x + hw * math.cos(ang) * squash
            y = y_back + (y_front - y_back) * (0.15 + 0.85 * math.sin(ang * 0.5 + 0.3))
            pts.append((x, y, z))
        return pts

    def inner_ring(z, hw, y_back, y_front, n=16):
        pts = []
        for i in range(n):
            t = i / n
            ang = math.pi * (1 - t)
            x = hw * math.cos(ang)
            y = y_back + (y_front - y_back) * (0.2 + 0.8 * math.sin(ang * 0.5 + 0.3))
            pts.append((x, y, z))
        return pts

    # Outer shell loft (EVO proportions from reference)
    outer_slices = [
        # z,   hw,  y_back, y_front, squash
        (2,   48,  2,     28,    1.0),   # seat base
        (12,  52,  1,     38,    1.0),   # thigh
        (28,  50,  0,     42,    0.98),  # hip
        (48,  46,  -1,    44,    0.95),  # lumbar
        (68,  42,  -2,    43,    0.92),  # mid back
        (88,  50,  -2,    42,    1.05),  # shoulder flare START
        (102, 56,  -1,    40,    1.12),  # shoulder max
        (118, 44,  0,     36,    0.95),  # below headrest
        (130, 32,  2,     32,    0.88),  # headrest
        (138, 22,  4,     28,    0.82),  # crown
    ]

    outer_rings = [shell_ring(z, hw, yb, yf, n=32, squash=sq) for z, hw, yb, yf, sq in outer_slices]
    m.extend(loft_rings(outer_rings))

    # --- Rear shell (matte back with centre spine — reference rear 3/4 view) ---
    def back_shell_ring(z, hw, n=24):
        pts = []
        for i in range(n):
            t = i / n
            ang = math.pi * (1 - t)
            x = hw * 0.92 * math.cos(ang)
            y = -2.5 - 3.5 * (1 - math.sin(ang * 0.55))
            pts.append((x, y, z))
        return pts

    back_slices = [(8, 46), (35, 44), (60, 40), (85, 46), (105, 50), (125, 34)]
    back_rings = [back_shell_ring(z, hw) for z, hw in back_slices]
    m.extend(loft_rings(back_rings))

    # --- Headrest front panel (flat face under crown — sparco logo zone) ---
    head = Mesh()
    for z0, z1 in [(118, 130), (130, 136)]:
        head.quad(head.v(-28, 44, z0), head.v(28, 44, z0), head.v(28, 44, z1), head.v(-28, 44, z1))
    # crown dome
    crown_rings = []
    for z, hw in [(136, 26), (140, 18), (142, 10)]:
        crown_rings.append([(-hw, 42, z), (hw, 42, z), (hw, 38, z), (-hw, 38, z)])
    head.extend(loft_rings(crown_rings, cap_top=True))
    m.extend(head)

    # --- Thigh bolsters (left/right wings — EVO deep bucket) ---
    def bolster_wing(side, z0, z1, x_out, x_in, y_tip):
        s = side
        n = 8
        rings = []
        for zi in range(n):
            t = zi / (n - 1)
            z = z0 + t * (z1 - z0)
            hw = x_in + t * (x_out - x_in) * 0.3
            ring = [
                (s * x_in, 18 + t * 8, z),
                (s * x_out, y_tip, z + 1),
                (s * x_out, y_tip - 4, z),
                (s * (x_in + 4), 22, z - 1),
            ]
            rings.append(ring)
        return loft_rings(rings)

    m.extend(bolster_wing(-1, 4, 32, 58, 46, 46))
    m.extend(bolster_wing(1, 4, 32, 58, 46, 46))

    # --- Shoulder wings (the iconic EVO flare) ---
    def shoulder_wing(side):
        s = side
        rings = []
        specs = [
            (82, 44, 40, 38),
            (92, 52, 42, 40),
            (102, 58, 41, 39),
            (112, 50, 38, 36),
            (122, 38, 34, 33),
        ]
        for z, x_out, y_tip, x_in in specs:
            ring = [
                (s * x_in, 20, z),
                (s * x_out, y_tip, z),
                (s * (x_out - 4), y_tip - 2, z + 3),
                (s * (x_in + 6), 24, z - 2),
            ]
            rings.append(ring)
        return loft_rings(rings)

    m.extend(shoulder_wing(-1))
    m.extend(shoulder_wing(1))

    # --- Recessed centre pad (front face — darker panel in reference) ---
    pad = Mesh()
    pad_slices = [
        (14, 38, 42, 44),
        (40, 36, 44, 46),
        (70, 34, 43, 45),
        (100, 32, 40, 42),
    ]
    for z, hw, y0, y1 in pad_slices:
        pad.extend(loft_rings([
            [( -hw, y0, z), (hw, y0, z), (hw, y1, z), (-hw, y1, z)]
        ]))
    # Actually loft between pad slices
    pad_rings = [[(-hw, y0, z), (hw, y0, z), (hw, y1, z), (-hw, y1, z)] for z, hw, y0, y1 in pad_slices]
    m.extend(loft_rings(pad_rings))

    # --- Harness openings + bezels (twin trapezoids — signature EVO look) ---
    for cx in (-20, 20):
        m.extend(build_harness_bezel(cx, 108, top_w=22, bot_w=15, h=12, depth=4.5))
        m.extend(_harness_void(cx, 108, top_w=16, bot_w=10, h=9, y0=39, y1=46))

    # --- Horizontal pad seam (centre back stitch line) ---
    seam = Mesh()
    for x in np.linspace(-28, 28, 15):
        seam.quad(seam.v(x, 44.2, 58), seam.v(x + 2, 44.2, 58), seam.v(x + 2, 44.8, 58), seam.v(x, 44.8, 58))
    m.extend(seam)

    # --- EVO badge recess (small panel below harness) ---
    badge = Mesh()
    bw, bh = 14, 6
    z0 = 92
    y = 44
    badge.quad(badge.v(-bw, y, z0), badge.v(bw, y, z0), badge.v(bw, y + 1.2, z0 - bh), badge.v(-bw, y + 1.2, z0 - bh))
    badge.quad(badge.v(-bw, y, z0), badge.v(-bw, y + 1.2, z0 - bh), badge.v(-bw, y + 1.2, z0 - bh - 0.8), badge.v(-bw, y, z0 - 0.8))
    badge.quad(badge.v(bw, y, z0), badge.v(bw, y, z0 - 0.8), badge.v(bw, y + 1.2, z0 - bh - 0.8), badge.v(bw, y + 1.2, z0 - bh))
    m.extend(badge)

    # --- Front lip (seat cushion front edge) ---
    lip_rings = []
    for z, hw in [(8, 44), (10, 46), (12, 48)]:
        lip_rings.append([( -hw, 44, z), (hw, 44, z), (hw, 48, z), (-hw, 48, z)])
    m.extend(loft_rings(lip_rings))

    # --- Phone pocket (structural rails + floor + lip) ---
    pw, pt, ph = PHONE_W / 2, PHONE_T / 2, PHONE_H
    px, py, pz = 0, 26, 22
    wall = 3.5

    def pocket_box(x0, y0, z0, x1, y1, z1):
        pm = Mesh()
        pm.quad(pm.v(x0, y0, z0), pm.v(x1, y0, z0), pm.v(x1, y1, z0), pm.v(x0, y1, z0))
        pm.quad(pm.v(x0, y0, z1), pm.v(x0, y1, z1), pm.v(x1, y1, z1), pm.v(x1, y0, z1))
        pm.quad(pm.v(x0, y0, z0), pm.v(x0, y0, z1), pm.v(x0, y1, z1), pm.v(x0, y1, z0))
        pm.quad(pm.v(x1, y0, z0), pm.v(x1, y1, z0), pm.v(x1, y1, z1), pm.v(x1, y0, z1))
        return pm

    # floor
    m.extend(pocket_box(px - pw - wall, py - pt - 1, pz, px + pw + wall, py + pt + wall, pz + 3))
    # left/right rails
    m.extend(pocket_box(px - pw - wall, py - pt - 1, pz, px - pw, py + pt + 1, pz + ph))
    m.extend(pocket_box(px + pw, py - pt - 1, pz, px + pw + wall, py + pt + 1, pz + ph))
    # back wall
    m.extend(pocket_box(px - pw - wall, py - pt - wall, pz, px + pw + wall, py - pt, pz + ph))
    # front lip (split for charge notch)
    m.extend(pocket_box(px - pw - wall, py + pt, pz, px - 8, py + pt + wall, pz + 10))
    m.extend(pocket_box(px + 8, py + pt, pz, px + pw + wall, py + pt + wall, pz + 10))
    # charge opening (leave open — no geom)

    # --- Rear shell spine + mounting boss ---
    spine = Mesh()
    for z in range(30, 95, 4):
        spine.quad(spine.v(-4, -2, z), spine.v(4, -2, z), spine.v(4, -2, z + 4), spine.v(-4, -2, z + 4))
    m.extend(spine)

    boss = Mesh()
    hs = BACK_PATTERN / 2
    cz = 62
    boss.quad(boss.v(-22, -6, 48), boss.v(22, -6, 48), boss.v(22, -6, 76), boss.v(-22, -6, 76))
    boss.quad(boss.v(-22, -6, 48), boss.v(-22, 0, 48), boss.v(-22, 0, 76), boss.v(-22, -6, 76))
    boss.quad(boss.v(22, -6, 48), boss.v(22, -6, 76), boss.v(22, 0, 76), boss.v(22, 0, 48))
    boss.quad(boss.v(-22, -6, 76), boss.v(22, -6, 76), boss.v(22, 0, 76), boss.v(-22, 0, 76))
    boss.quad(boss.v(-22, -6, 48), boss.v(22, -6, 48), boss.v(22, 0, 48), boss.v(-22, 0, 48))
    m.extend(boss)

    # M3 holes through boss (visual — actual clearance when printing)
    # (meshes don't boolean; holes noted in docs / drill)

    # Close bottom of shell
    bottom = Mesh()
    ring = shell_ring(0, 48, 2, 28, n=20)
    ci = bottom.v(0, 20, 0)
    rids = [bottom.v(*p) for p in ring]
    for i in range(20):
        j = (i + 1) % 20
        bottom.tri(ci, rids[j], rids[i])
    m.extend(bottom)

    return center_bed(m)


# ---------------------------------------------------------------------------
# Clean modular backs (same interface, simpler geometry)
# ---------------------------------------------------------------------------

def _plate_block(m: Mesh, x0, y0, z0, x1, y1, z1):
    m.quad(m.v(x0, y0, z0), m.v(x1, y0, z0), m.v(x1, y1, z0), m.v(x0, y1, z0))
    m.quad(m.v(x0, y0, z1), m.v(x0, y1, z1), m.v(x1, y1, z1), m.v(x1, y0, z1))
    m.quad(m.v(x0, y0, z0), m.v(x0, y0, z1), m.v(x0, y1, z1), m.v(x0, y1, z0))
    m.quad(m.v(x1, y0, z0), m.v(x1, y1, z0), m.v(x1, y1, z1), m.v(x1, y0, z1))
    m.quad(m.v(x0, y0, z0), m.v(x1, y0, z0), m.v(x1, y0, z1), m.v(x0, y0, z1))
    m.quad(m.v(x0, y1, z0), m.v(x0, y1, z1), m.v(x1, y1, z1), m.v(x1, y1, z0))


def build_back_rail(orientation: str) -> Mesh:
    """Clean flat plate + 4040 twist key."""
    m = Mesh()
    _plate_block(m, -20, 0, 0, 20, 4, 42)

    if orientation == "vertical":
        _plate_block(m, -3.5, 4, 10, 3.5, 11, 32)
        _plate_block(m, -7.5, 11, 12, 7.5, 15, 30)
    else:
        _plate_block(m, -12, 4, 17, 12, 11, 25)
        _plate_block(m, -10, 11, 15, 10, 15, 27)

    return center_bed(m)


def build_leg_plate() -> Mesh:
    m = Mesh()
    m.quad(m.v(-22, 0, 0), m.v(22, 0, 0), m.v(22, 0, 44), m.v(-22, 0, 44))
    m.quad(m.v(-22, 6, 0), m.v(-22, 6, 44), m.v(22, 6, 44), m.v(22, 6, 0))
    for dx, dz in [(-14, 10), (14, 10), (0, 36)]:
        m.extend(_cylinder_mesh(dx, dz, 6, 8, 3.2))
    return center_bed(m)


def _cylinder_mesh(cx, cz, y0, h, r, seg=16):
    cm = Mesh()
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        x0, z0 = cx + r * math.cos(a0), cz + r * math.sin(a0)
        x1, z1 = cx + r * math.cos(a1), cz + r * math.sin(a1)
        cm.quad(cm.v(x0, y0, z0), cm.v(x1, y0, z1), cm.v(x1, y0 + h, z1), cm.v(x0, y0 + h, z0))
    return cm


def build_desk_leg() -> Mesh:
    m = Mesh()
    for i in range(16):
        a0 = 2 * math.pi * i / 16
        a1 = 2 * math.pi * (i + 1) / 16
        r0, r1 = 9, 7
        for z0, z1, r in [(0, 4, 10), (4, 40, 7), (40, 48, 5)]:
            x00, y00 = r * math.cos(a0), r * math.sin(a0)
            x01, y01 = r * math.cos(a1), r * math.sin(a1)
            m.quad(m.v(x00, y00, z0), m.v(x01, y01, z0), m.v(x01, y01, z1), m.v(x00, y00, z1))
    return center_bed(m)


def build_kickout() -> Mesh:
    m = Mesh()
    m.quad(m.v(-20, 0, 0), m.v(20, 0, 0), m.v(20, 0, 42), m.v(-20, 0, 42))
    m.quad(m.v(-20, 5, 0), m.v(-20, 5, 42), m.v(20, 5, 42), m.v(20, 5, 0))
    # kickout arm
    m.quad(m.v(-8, 5, 16), m.v(8, 5, 16), m.v(8, 5, 28), m.v(-8, 5, 28))
    m.quad(m.v(-8, 5, 28), m.v(8, 5, 28), m.v(8, 32, 28), m.v(-8, 32, 28))
    m.quad(m.v(-8, 5, 16), m.v(-8, 32, 16), m.v(-8, 32, 28), m.v(-8, 5, 28))
    m.quad(m.v(8, 5, 16), m.v(8, 5, 28), m.v(8, 32, 28), m.v(8, 32, 16))
    return center_bed(m)


def build_clamp_desk() -> Mesh:
    m = Mesh()
    m.quad(m.v(0, 0, 0), m.v(28, 0, 0), m.v(28, 0, 22), m.v(0, 0, 22))
    m.quad(m.v(0, 0, 0), m.v(0, 28, 0), m.v(0, 28, 22), m.v(0, 0, 22))
    m.quad(m.v(0, 22, 0), m.v(28, 22, 0), m.v(28, 22, 22), m.v(0, 22, 22))
    return center_bed(m)


def build_clamp_tube() -> Mesh:
    m = Mesh()
    r = 20.2
    for i in range(24):
        a0 = math.pi + 2 * math.pi * i / 24 * 0.98
        a1 = math.pi + 2 * math.pi * (i + 1) / 24 * 0.98
        x0, y0 = r * math.cos(a0), r * math.sin(a0)
        x1, y1 = r * math.cos(a1), r * math.sin(a1)
        m.quad(m.v(x0, y0, 0), m.v(x1, y1, 0), m.v(x1, y1, 22), m.v(x0, y0, 22))
    return center_bed(m)


def build_blank_back() -> Mesh:
    return build_back_rail("vertical")  # placeholder — flat plate only
    # Actually build flat:
    m = Mesh()
    m.quad(m.v(-20, 0, 0), m.v(20, 0, 0), m.v(20, 0, 42), m.v(-20, 0, 42))
    m.quad(m.v(-20, 5, 0), m.v(-20, 5, 42), m.v(20, 5, 42), m.v(20, 5, 0))
    return center_bed(m)


def main():
    print("Building EVO faceted cradle (v4)...\n")
    cradle = build_evo_cradle()
    cradle.write_stl(OUT / "01_cradle_evo.stl", "cradle_evo")

    build_back_rail("vertical").write_stl(OUT / "02_back_rail_vertical.stl", "rail_v")
    build_back_rail("horizontal").write_stl(OUT / "03_back_rail_horizontal.stl", "rail_h")
    build_leg_plate().write_stl(OUT / "04_back_leg_plate.stl", "leg_plate")
    build_desk_leg().write_stl(OUT / "05_desk_leg.stl", "desk_leg")
    build_kickout().write_stl(OUT / "06_back_kickout_m3.stl", "kickout")
    build_clamp_desk().write_stl(OUT / "07_clamp_desk_m3.stl", "clamp_desk")
    build_clamp_tube().write_stl(OUT / "08_clamp_tube40_m3.stl", "clamp_tube")

    m = Mesh()
    m.quad(m.v(-20, 0, 0), m.v(20, 0, 0), m.v(20, 0, 42), m.v(-20, 0, 42))
    m.quad(m.v(-20, 5, 0), m.v(-20, 5, 42), m.v(20, 5, 42), m.v(20, 5, 0))
    center_bed(m).write_stl(OUT / "09_back_blank_diy.stl", "blank")

    # sync download folder
    dl = ROOT / "download"
    dl.mkdir(exist_ok=True)
    import shutil
    for f in OUT.glob("*.stl"):
        shutil.copy2(f, dl / f.name)
    print("\nSynced to download/")


if __name__ == "__main__":
    main()
