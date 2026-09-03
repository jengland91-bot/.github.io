#!/usr/bin/env python3
"""Generate 3D-printable Moza / D1-spec QR steering-wheel wall mounts.

The stub copies the working hangers: a slimmer lead-in, then a collar with
round 6.5 mm ball dimples in Moza's 6-up / 4-down clock. Dimple centres sit
so the top of each cup is 22.7 mm from the pad face. A free-spin ring-groove
variant is also generated.

Also writes the 8020 accessory kit via accessories.py.

Units: millimetres.
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import zipfile
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]
Tri = Tuple[Vec3, Vec3, Vec3]


# ---------------------------------------------------------------------------
# Tunable geometry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Fit:
    """QR stub diameters. Tweak these if a printed test ring is tight/loose."""

    name: str
    shaft_d: float
    groove_d: float


# Sleeve ID 40.9 mm. Lead-in is extra-undersize so it slides; the collar
# carries the dimples at the working hangers' diameter.
_SEAT_DEPTH = 4.2  # free-spin ring only
FITS = {
    "tight": Fit("tight", shaft_d=40.2, groove_d=40.2 - 2 * _SEAT_DEPTH),
    "nominal": Fit("nominal", shaft_d=39.8, groove_d=39.8 - 2 * _SEAT_DEPTH),
    "loose": Fit("loose", shaft_d=39.4, groove_d=39.4 - 2 * _SEAT_DEPTH),
}

DEFAULT_FIT = "nominal"

# Working hangers (green Moza-style + black dimple hub) use round cups, not a
# lathed ring. Josh: balls 6.5 mm, top of the cutout 22.7 mm in.
#
#   z = 0       pad face
#   z = 0–15    slimmer lead-in (slides through the 40.9 mm sleeve)
#   z = 19.45   dimple centres (6.5 mm cups, 6-up / 4-down)
#   z = 22.7    top of each dimple
#   z ≈ 25.7    stub tip, open 22 mm bore, short of the 28.8 mm pin plate
BALL_D = 6.5
BALL_CUTOUT_TOP = 22.7
BALL_RING_FROM_FACE = BALL_CUTOUT_TOP - BALL_D / 2.0  # 19.45 mm
PIN_PLATE_DEPTH = 28.8
DIMPLE_R = BALL_D / 2.0 + 0.2  # slight oversize so 6.5 mm balls sit down
DIMPLE_INSET = 0.75  # centre inside the collar → ~4.2 mm deep cups
LEAD_D_DELTA = 2.0  # lead-in is this much smaller than shaft_d
COLLAR_BLEND = 2.0  # taper from lead-in up to the dimple collar
CHAMFER = 2.0
FILLET_R = 0.0
STUB_BORE_D = 22.0
# Keep these names so the free-spin ring path still compiles
GROOVE_FLAT = BALL_D
GROOVE_PLATE_AXIAL = 1.2
GROOVE_TIP_AXIAL = 2.0
LIP_FLAT = 3.0  # rim past the top of the dimple
NOSE_D = 21.0
NOSE_LEN = 0.0
NOSE_BORE_D = 14.0

SHAFT_LEN = BALL_CUTOUT_TOP + LIP_FLAT  # 25.7 mm
GROOVE_FROM_TIP = SHAFT_LEN - BALL_RING_FROM_FACE

if SHAFT_LEN >= PIN_PLATE_DEPTH - 2.5:
    raise RuntimeError(
        f"SHAFT_LEN={SHAFT_LEN} would reach the pogo-pin plate at {PIN_PLATE_DEPTH} mm"
    )

# Moza official hanger: six dimples on top, four on the bottom.
POCKET_ANGLES_DEG = (15, 45, 75, 105, 135, 165, 225, 255, 285, 315)
POCKET_COUNT = len(POCKET_ANGLES_DEG)
POCKET_WIDTH_DEG = math.degrees(BALL_D / (FITS["nominal"].shaft_d / 2.0))
POCKET_BLEND_DEG = 3.0
POCKET_OFFSET_DEG = 90.0
LAND_RECESS = 2.4  # free-spin ring depth
STUB_SEGMENTS = 240
DIMPLE_Z_SLICES = 18

# Wall plate
PLATE_D = 98.0
PLATE_T = 8.0
RIM_CHAMFER = 1.8
SCREW_R = 36.0  # plus-pattern: N/E/S/W, so two screws can hit a stud
SCREW_D = 4.8  # clearance for #8 wood screw / 4.5 mm / M4
SCREW_CSK_D = 9.8
SCREW_CSK_DEPTH = 2.4
CENTER_HOLE_D = 8.4  # M8 through the pad / plate (short bolt into a T-nut)
CENTER_CSK_D = 14.0  # M8 socket-cap head is ~13 mm
PAD_BOLT_WEB = 3.0  # plastic under the head in the pad (pocket is the rest of the 8 mm)
FIT_SCREW_X = 15.0  # four #8 at the corners of the pad
FIT_SCREW_Y = 26.0
FIT_LUG_PAD_R = 11.0  # meat around each #8
FIT_LUG_T = 8.0  # same as the 4040 strip so the screws have meat
FIT_FLANGE_EXTRA = 7.0  # extra ring all around the stub (green)
FIT_CORNER_R = 10.0  # flattened top/bottom ears
SKIRT_WINDOW_COUNT = 6  # filament-saver holes around the stub (red)
SKIRT_WINDOW_W = 14.0  # mm of opening at the outer wall
FIT_SCALLOP_NS_R = 11.0  # top / bottom edge bites (leave ~2.7 mm at the #8 CSK)
FIT_SCALLOP_EW_R = 10.0  # left / right edge bites
FIT_SCALLOP_SEGS = 16

# Product bezel — raised ring so the plate looks finished, not like a raw disc
BEZEL_W = 4.2
BEZEL_H = 1.6

# Accessories still use a tab outline; the wheel mount itself is a round disc.
TAB_W = 54.0
TAB_BOTTOM = -114.0
TAB_CORNER_R = 14.0
PROFILE_HOLE_D = 8.4  # M8 clearance (accessories)
PROFILE_HOLE_CSK_D = 14.0

SEGMENTS = 96  # circle resolution
FILLET_SEGS = 10


# ---------------------------------------------------------------------------
# Tiny vector / mesh helpers
# ---------------------------------------------------------------------------

def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(v: Vec3) -> Vec3:
    l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if l < 1e-18:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


def tri_normal(t: Tri) -> Vec3:
    return _norm(_cross(_sub(t[1], t[0]), _sub(t[2], t[0])))


def _tri_area2(t: Tri) -> float:
    n = _cross(_sub(t[1], t[0]), _sub(t[2], t[0]))
    return math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])


def clean_tris(tris: Sequence[Tri]) -> List[Tri]:
    return [t for t in tris if _tri_area2(t) > 1e-8]


def write_binary_stl(path: str, tris: Sequence[Tri], name: str = "moza_qr") -> None:
    tris = clean_tris(tris)
    buf = bytearray()
    header = name.encode("ascii", "replace")[:80]
    buf.extend(header.ljust(80, b"\0"))
    buf.extend(struct.pack("<I", len(tris)))
    for t in tris:
        n = tri_normal(t)
        buf.extend(struct.pack("<3f", *n))
        for p in t:
            buf.extend(struct.pack("<3f", *p))
        buf.extend(struct.pack("<H", 0))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(buf)


def bbox(tris: Sequence[Tri]) -> Tuple[Vec3, Vec3]:
    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    zs = [p[2] for t in tris for p in t]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


# ---------------------------------------------------------------------------
# 2D polygons
# ---------------------------------------------------------------------------

def circle_pts(cx: float, cy: float, r: float, n: int, ccw: bool = True) -> List[Vec2]:
    s = 1 if ccw else -1
    return [
        (
            cx + r * math.cos(s * 2 * math.pi * i / n),
            cy + r * math.sin(s * 2 * math.pi * i / n),
        )
        for i in range(n)
    ]


def annular_sector_pts(
    inner_r: float, outer_r: float, a0: float, a1: float, n: int = 14
) -> List[Vec2]:
    """CCW outline of a wall segment (outer arc, then inner arc back)."""
    pts: List[Vec2] = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((outer_r * math.cos(a), outer_r * math.sin(a)))
    for i in range(n + 1):
        a = a1 + (a0 - a1) * i / n
        pts.append((inner_r * math.cos(a), inner_r * math.sin(a)))
    return ensure_winding(pts, True)


def rounded_rect_pts(w: float, h: float, r: float, n_each: int = 8) -> List[Vec2]:
    r = min(r, w / 2 - 0.1, h / 2 - 0.1)
    corners = [
        (w / 2 - r, h / 2 - r, 0.0),
        (-w / 2 + r, h / 2 - r, math.pi / 2),
        (-w / 2 + r, -h / 2 + r, math.pi),
        (w / 2 - r, -h / 2 + r, 3 * math.pi / 2),
    ]
    pts: List[Vec2] = []
    for cx, cy, a0 in corners:
        for i in range(n_each):
            a = a0 + (math.pi / 2) * i / (n_each - 1 if n_each > 1 else 1)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _arc_pts(cx: float, cy: float, r: float, a0: float, a1: float, n: int) -> List[Vec2]:
    """Arc including both endpoints. a0 -> a1, n segments (n+1 points)."""
    return [
        (cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n))
        for i in range(n + 1)
    ]


def _corner_pts(cx: float, cy: float, r: float, a0: float, n: int) -> List[Vec2]:
    return [
        (cx + r * math.cos(a0 + (math.pi / 2) * i / max(n - 1, 1)),
         cy + r * math.sin(a0 + (math.pi / 2) * i / max(n - 1, 1)))
        for i in range(n)
    ]


def scalloped_rect_pts(
    half_w: float,
    half_l: float,
    corner_r: float,
    ns_r: float,
    ew_r: float,
    n_corner: int = 10,
    n_scallop: int = FIT_SCALLOP_SEGS,
) -> List[Vec2]:
    """Rounded rectangle with U-bites at N/E/S/W. CCW, starting at the TR corner."""
    cr = min(corner_r, half_w - 0.4, half_l - 0.4)
    ns_r = min(ns_r, half_w - cr - 1.0)
    ew_r = min(ew_r, half_l - cr - 1.0)
    pts: List[Vec2] = []
    # TR corner (0 -> 90), then top scallop, TL, left scallop, BL, bottom, BR, right.
    pts.extend(_corner_pts(half_w - cr, half_l - cr, cr, 0.0, n_corner))
    pts.extend(_arc_pts(0.0, half_l, ns_r, 0.0, -math.pi, n_scallop))
    pts.extend(_corner_pts(-half_w + cr, half_l - cr, cr, math.pi / 2, n_corner))
    pts.extend(_arc_pts(-half_w, 0.0, ew_r, math.pi / 2, -math.pi / 2, n_scallop))
    pts.extend(_corner_pts(-half_w + cr, -half_l + cr, cr, math.pi, n_corner))
    pts.extend(_arc_pts(0.0, -half_l, ns_r, math.pi, 0.0, n_scallop))
    pts.extend(_corner_pts(half_w - cr, -half_l + cr, cr, 3 * math.pi / 2, n_corner))
    pts.extend(_arc_pts(half_w, 0.0, ew_r, 3 * math.pi / 2, math.pi / 2, n_scallop))
    return pts


def area2(poly: Sequence[Vec2]) -> float:
    a = 0.0
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        a += p[0] * q[1] - q[0] * p[1]
    return a


def ensure_winding(poly: Sequence[Vec2], ccw: bool) -> List[Vec2]:
    pts = list(poly)
    if (area2(pts) > 0) != ccw:
        pts.reverse()
    return pts


def _dist2(a: Vec2, b: Vec2) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _seg_intersect(a: Vec2, b: Vec2, c: Vec2, d: Vec2) -> bool:
    def cross(p: Vec2, q: Vec2, r: Vec2) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    d1 = cross(c, d, a)
    d2 = cross(c, d, b)
    d3 = cross(a, b, c)
    d4 = cross(a, b, d)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True
    return False


def bridge_holes(outer: Sequence[Vec2], holes: Sequence[Sequence[Vec2]]) -> List[Vec2]:
    """Build a simple polygon by bridging CCW outer to CW holes."""
    poly = ensure_winding(outer, True)
    for hole in holes:
        hole_cw = ensure_winding(hole, False)
        best_i = best_j = 0
        best = 1e18
        for i, p in enumerate(poly):
            for j, q in enumerate(hole_cw):
                d = _dist2(p, q)
                if d >= best:
                    continue
                # skip if the bridge crosses existing edges
                crosses = False
                b0, b1 = p, q
                for k, r in enumerate(poly):
                    s = poly[(k + 1) % len(poly)]
                    if r is p or s is p:
                        continue
                    if _seg_intersect(b0, b1, r, s):
                        crosses = True
                        break
                if crosses:
                    continue
                best = d
                best_i, best_j = i, j
        # insert hole, duplicating bridge endpoints
        ordered = hole_cw[best_j:] + hole_cw[:best_j]
        # ... P_i, H_j, ... H_j, P_i, P_{i+1} ...
        poly = poly[: best_i + 1] + ordered + [ordered[0]] + poly[best_i:]
    return poly


def _orient(a: Vec2, b: Vec2, c: Vec2) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _in_tri(p: Vec2, a: Vec2, b: Vec2, c: Vec2) -> bool:
    # strict interior — points on edges/vertices are not "inside"
    eps = 1e-9
    return (
        _orient(a, b, p) > eps
        and _orient(b, c, p) > eps
        and _orient(c, a, p) > eps
    )


def _same(a: Vec2, b: Vec2, eps: float = 1e-9) -> bool:
    return abs(a[0] - b[0]) < eps and abs(a[1] - b[1]) < eps


def earclip(poly: Sequence[Vec2]) -> List[Tuple[int, int, int]]:
    verts = list(poly)
    n = len(verts)
    idx = list(range(n))
    tris: List[Tuple[int, int, int]] = []
    guard = 0
    while len(idx) > 3:
        guard += 1
        if guard > n * n + 10:
            raise RuntimeError("earclip failed — polygon may be self-intersecting")
        found = False
        m = len(idx)
        for ii in range(m):
            i0 = idx[(ii - 1) % m]
            i1 = idx[ii]
            i2 = idx[(ii + 1) % m]
            a, b, c = verts[i0], verts[i1], verts[i2]
            if _orient(a, b, c) <= 1e-12:
                continue
            occupied = False
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                p = verts[j]
                if _same(p, a) or _same(p, b) or _same(p, c):
                    continue
                if _in_tri(p, a, b, c):
                    occupied = True
                    break
            if occupied:
                continue
            tris.append((i0, i1, i2))
            del idx[ii]
            found = True
            break
        if not found:
            rest = [verts[i] for i in idx]
            if area2(rest) < 0:
                idx.reverse()
                continue
            raise RuntimeError("earclip: no ear found")
    tris.append((idx[0], idx[1], idx[2]))
    return tris


# ---------------------------------------------------------------------------
# 3D primitives
# ---------------------------------------------------------------------------

def _shift(poly: Sequence[Vec2], dx: float, dy: float) -> List[Vec2]:
    return [(p[0] + dx, p[1] + dy) for p in poly]


def _connect_rings(ring0: Sequence[Vec2], ring1: Sequence[Vec2], z0: float, z1: float, inward: bool) -> List[Tri]:
    if len(ring0) != len(ring1):
        raise ValueError("rings must have the same vertex count")
    n = len(ring0)
    tris: List[Tri] = []
    for i in range(n):
        p = ring0[i]
        q = ring0[(i + 1) % n]
        r = ring1[(i + 1) % n]
        s = ring1[i]
        a = (p[0], p[1], z0)
        b = (q[0], q[1], z0)
        c = (r[0], r[1], z1)
        d = (s[0], s[1], z1)
        if inward:
            tris.append((a, d, c))
            tris.append((a, c, b))
        else:
            tris.append((a, b, c))
            tris.append((a, c, d))
    return tris


def _cap(outer: Sequence[Vec2], holes: Sequence[Sequence[Vec2]], z: float, flip: bool) -> List[Tri]:
    poly = bridge_holes(outer, holes)
    tris: List[Tri] = []
    for i0, i1, i2 in earclip(poly):
        t = (
            (poly[i0][0], poly[i0][1], z),
            (poly[i1][0], poly[i1][1], z),
            (poly[i2][0], poly[i2][1], z),
        )
        tris.append((t[0], t[2], t[1]) if flip else t)
    return tris


def loft_layers(layers: Sequence[Dict]) -> List[Tri]:
    """Watertight loft. Each layer: {z, outer, holes}. Caps only on first/last."""
    if len(layers) < 2:
        raise ValueError("need at least two layers")
    tris: List[Tri] = []
    first, last = layers[0], layers[-1]
    tris.extend(_cap(first["outer"], first["holes"], first["z"], flip=True))
    tris.extend(_cap(last["outer"], last["holes"], last["z"], flip=False))
    for a, b in zip(layers, layers[1:]):
        tris.extend(
            _connect_rings(
                ensure_winding(a["outer"], True),
                ensure_winding(b["outer"], True),
                a["z"],
                b["z"],
                inward=False,
            )
        )
        for ha, hb in zip(a["holes"], b["holes"]):
            tris.extend(
                _connect_rings(
                    ensure_winding(ha, False),
                    ensure_winding(hb, False),
                    a["z"],
                    b["z"],
                    inward=False,
                )
            )
    return tris


def extrude_with_holes(
    outer: Sequence[Vec2],
    holes_bottom: Sequence[Sequence[Vec2]],
    holes_top: Sequence[Sequence[Vec2]],
    z0: float,
    z1: float,
) -> List[Tri]:
    return loft_layers(
        [
            {"z": z0, "outer": ensure_winding(outer, True), "holes": holes_bottom},
            {"z": z1, "outer": ensure_winding(outer, True), "holes": holes_top},
        ]
    )


def _angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def pocket_t(theta: float) -> float:
    """1 inside a ball seat, 0 on the land between seats."""
    half = math.radians(POCKET_WIDTH_DEG / 2.0)
    blend = math.radians(POCKET_BLEND_DEG)
    best = min(_angle_diff(theta, math.radians(a)) for a in POCKET_ANGLES_DEG)
    if best <= max(0.0, half - blend):
        return 1.0
    if best >= half + blend:
        return 0.0
    x = (half + blend - best) / (2 * blend)
    return x * x * (3.0 - 2.0 * x)


def _dimple_centers_xy(shaft_r: float) -> List[Tuple[float, float]]:
    cr = shaft_r - DIMPLE_INSET
    return [
        (cr * math.cos(math.radians(a)), cr * math.sin(math.radians(a)))
        for a in POCKET_ANGLES_DEG
    ]


def _cut_dimples(
    r: float, theta: float, z: float, z_base: float, shaft_r: float
) -> float:
    """Pull this (r, theta, z) onto any 6.5 mm spherical cup it sits inside."""
    z_c = z_base + FILLET_R + BALL_RING_FROM_FACE
    if abs(z - z_c) > DIMPLE_R + 0.15:
        return r
    xh, yh = math.cos(theta), math.sin(theta)
    out = r
    r2 = DIMPLE_R * DIMPLE_R
    for cx, cy in _dimple_centers_xy(shaft_r):
        b_lin = cx * xh + cy * yh
        c0 = cx * cx + cy * cy + (z - z_c) ** 2 - r2
        disc = b_lin * b_lin - c0
        if disc < 0.0:
            continue
        r_hit = b_lin - math.sqrt(disc)
        if 0.8 < r_hit < out:
            out = r_hit
    return out


def _ring_cut(r: float, z: float, z_base: float, shaft_r: float) -> float:
    """Shallow free-spin ring at the same height as the dimples."""
    z_c = z_base + FILLET_R + BALL_RING_FROM_FACE
    half = BALL_D / 2.0
    dz = abs(z - z_c)
    if dz >= half:
        return r
    t = 1.0 - dz / half
    t = t * t * (3.0 - 2.0 * t)
    return min(r, shaft_r - LAND_RECESS * t)


def _groove_tapers(fit: Fit) -> Tuple[float, float, float]:
    """Plate-side axial, tip-side axial, radial depth of the free-spin ring."""
    depth = fit.shaft_d / 2.0 - fit.groove_d / 2.0
    tip_axial = min(depth, GROOVE_TIP_AXIAL)
    plate_axial = min(depth, GROOVE_PLATE_AXIAL)
    return plate_axial, tip_axial, depth


def _groove_z_band(z_base: float, fit: Fit) -> Tuple[float, float]:
    g_mid = z_base + FILLET_R + BALL_RING_FROM_FACE
    return g_mid - DIMPLE_R, g_mid + DIMPLE_R


def lathe(
    profile: Sequence[Vec2],
    n: int = SEGMENTS,
    *,
    fit: Fit | None = None,
    z_base: float | None = None,
    indexed: bool = False,
) -> List[Tri]:
    """Revolve an (r, z) polyline around Z. Open profiles stay open (no end cap).

    indexed=True cuts round 6.5 mm dimples (working-hanger style).
    """
    prof = list(profile)
    thetas = [2 * math.pi * i / n for i in range(n)]
    shaft_r = fit.shaft_d / 2.0 if fit is not None else 0.0
    rings: List[List[Vec3]] = []
    for r, z in prof:
        r = max(r, 0.0)
        ring: List[Vec3] = []
        for t in thetas:
            rr = r
            if (
                fit is not None
                and z_base is not None
                and r > STUB_BORE_D / 2.0 + 0.5
            ):
                if indexed:
                    rr = _cut_dimples(r, t, z, z_base, shaft_r)
                else:
                    rr = _ring_cut(r, z, z_base, shaft_r)
            ring.append((rr * math.cos(t), rr * math.sin(t), z))
        rings.append(ring)
    tris: List[Tri] = []
    for i in range(len(rings) - 1):
        a = rings[i]
        b = rings[i + 1]
        for j in range(n):
            p00 = a[j]
            p01 = a[(j + 1) % n]
            p10 = b[j]
            p11 = b[(j + 1) % n]
            if abs(p00[0]) < 1e-7 and abs(p00[1]) < 1e-7 and abs(p01[0]) < 1e-7 and abs(p01[1]) < 1e-7:
                if abs(p10[0] - p11[0]) + abs(p10[1] - p11[1]) < 1e-7:
                    continue
                tris.append((p00, p10, p11))
                continue
            if abs(p10[0]) < 1e-7 and abs(p10[1]) < 1e-7 and abs(p11[0]) < 1e-7 and abs(p11[1]) < 1e-7:
                tris.append((p00, p01, p10))
                continue
            if _tri_area2((p00, p10, p11)) > 1e-8:
                tris.append((p00, p10, p11))
            if _tri_area2((p00, p11, p01)) > 1e-8:
                tris.append((p00, p11, p01))
    # If the open profile starts and ends at the same z, cap the annulus so the
    # stub is a closed solid (sits in the plate's centre cut-out).
    if rings and abs(rings[0][0][2] - rings[-1][0][2]) < 1e-6:
        a = rings[0]
        b = rings[-1]
        for j in range(n):
            p00, p01 = a[j], a[(j + 1) % n]
            p10, p11 = b[j], b[(j + 1) % n]
            # normal should point -Z (out of the stub base)
            t0 = (p00, p11, p10)
            t1 = (p00, p01, p11)
            if _tri_area2(t0) > 1e-8:
                tris.append(t0)
            if _tri_area2(t1) > 1e-8:
                tris.append(t1)
    return tris


def qr_stub_profile(
    fit: Fit, z_base: float, inner_r: float | None = None, z_from: float | None = None
) -> List[Vec2]:
    """Lead-in + dimple collar. Extra Z rings tessellate the spherical cups."""
    shaft_r = fit.shaft_d / 2.0
    lead_r = (fit.shaft_d - LEAD_D_DELTA) / 2.0
    inner = STUB_BORE_D / 2.0
    z_start = z_base if z_from is None else z_from
    z_tip = z_base + FILLET_R + SHAFT_LEN
    z_c = z_base + FILLET_R + BALL_RING_FROM_FACE
    z_collar = z_c - DIMPLE_R - COLLAR_BLEND
    chamfer_z = z_tip - CHAMFER

    def r_at(z: float) -> float:
        if z >= z_collar + COLLAR_BLEND:
            return shaft_r
        if z <= z_collar:
            return lead_r
        t = (z - z_collar) / COLLAR_BLEND
        return lead_r + (shaft_r - lead_r) * t

    pts: List[Vec2] = [
        (inner, z_start),
        (inner, z_tip),
        (shaft_r - CHAMFER, z_tip),
    ]
    zs = [chamfer_z, z_collar + COLLAR_BLEND, z_collar, z_start]
    z_lo = z_c - DIMPLE_R - 0.2
    z_hi = min(chamfer_z - 0.05, z_c + DIMPLE_R + 0.2)
    for i in range(DIMPLE_Z_SLICES + 1):
        zs.append(z_lo + (z_hi - z_lo) * i / DIMPLE_Z_SLICES)
    seen = set()
    outer_z: List[float] = []
    for z in sorted(zs, reverse=True):
        z = min(max(z, z_start), chamfer_z)
        key = round(z, 4)
        if key in seen:
            continue
        seen.add(key)
        outer_z.append(z)
    for z in outer_z:
        pts.append((r_at(z), z))
    return pts


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

def _center_cut_d(fit: Fit) -> float:
    """Plate opening the stub sits in — slightly smaller than the stub root so they overlap."""
    return 2.0 * (fit.shaft_d / 2.0 + FILLET_R) - 0.4


def circle_tab_outline(
    circle_r: float,
    tab_w: float,
    tab_bottom: float,
    corner_r: float,
    n_circle: int = SEGMENTS,
    n_corner: int = 10,
) -> List[Vec2]:
    """CCW outline: circle through the top, tab hanging down."""
    tw = tab_w / 2.0
    join_y = -math.sqrt(max(circle_r * circle_r - tw * tw, 1.0))
    a_right = math.atan2(join_y, tw)
    a_left = math.atan2(join_y, -tw)
    start = a_right
    end = a_left
    if end <= start:
        end += 2 * math.pi
    pts: List[Vec2] = []
    for i in range(n_circle + 1):
        a = start + (end - start) * i / n_circle
        pts.append((circle_r * math.cos(a), circle_r * math.sin(a)))
    cx_l, cy = -tw + corner_r, tab_bottom + corner_r
    for i in range(n_corner):
        a = math.pi + (math.pi / 2) * i / max(n_corner - 1, 1)
        pts.append((cx_l + corner_r * math.cos(a), cy + corner_r * math.sin(a)))
    cx_r = tw - corner_r
    for i in range(1, n_corner):
        a = 1.5 * math.pi + (math.pi / 2) * i / max(n_corner - 1, 1)
        pts.append((cx_r + corner_r * math.cos(a), cy + corner_r * math.sin(a)))
    return ensure_winding(pts, True)


def wall_screw_centres() -> List[Vec2]:
    return [
        (0.0, SCREW_R),
        (SCREW_R, 0.0),
        (0.0, -SCREW_R),
        (-SCREW_R, 0.0),
    ]


def loft_stepped_m8(
    outer: Sequence[Vec2],
    thickness: float,
    screw_centres: Sequence[Vec2],
) -> List[Tri]:
    """Plate/pad with a 14 mm pocket from the stub side, 8.4 mm through, plus #8 CSK."""
    hole_n = 32
    screw_n = 24
    z_web = PAD_BOLT_WEB
    z_csk = max(z_web + 0.4, thickness - SCREW_CSK_DEPTH)
    outer = ensure_winding(outer, True)
    m8 = circle_pts(0.0, 0.0, CENTER_HOLE_D / 2.0, hole_n, False)
    pocket = circle_pts(0.0, 0.0, CENTER_CSK_D / 2.0, hole_n, False)
    screws = [
        circle_pts(c[0], c[1], SCREW_D / 2.0, screw_n, False) for c in screw_centres
    ]
    csks = [
        circle_pts(c[0], c[1], SCREW_CSK_D / 2.0, screw_n, False) for c in screw_centres
    ]
    return loft_layers(
        [
            {"z": 0.0, "outer": outer, "holes": [m8] + screws},
            {"z": z_web, "outer": outer, "holes": [m8] + screws},
            {"z": z_web, "outer": outer, "holes": [pocket] + screws},
            {"z": z_csk, "outer": outer, "holes": [pocket] + screws},
            {"z": thickness, "outer": outer, "holes": [pocket] + csks},
        ]
    )


def wall_plate_tris(fit: Fit) -> List[Tri]:
    """Round plate: 4× #8 around the rim, stepped M8 in the middle (short bolt)."""
    outer = circle_pts(0.0, 0.0, PLATE_D / 2.0, SEGMENTS, True)
    return loft_stepped_m8(outer, PLATE_T, wall_screw_centres())


def profile_plate_tris(fit: Fit) -> List[Tri]:
    return wall_plate_tris(fit)


def stub_tris(
    fit: Fit, z_front: float, indexed: bool = True, z_from: float | None = None
) -> List[Tri]:
    inner_r = STUB_BORE_D / 2.0
    return lathe(
        qr_stub_profile(fit, z_front, inner_r, z_from=z_from),
        STUB_SEGMENTS,
        fit=fit,
        z_base=z_front,
        indexed=indexed,
    )


def fit_pad_half(fit: Fit) -> Tuple[float, float]:
    """Half-width (X) and half-length (Y) of the racetrack pad."""
    shaft_r = fit.shaft_d / 2.0
    half_w = max(shaft_r + FIT_FLANGE_EXTRA, FIT_SCREW_X + FIT_LUG_PAD_R)
    half_l = FIT_SCREW_Y + FIT_LUG_PAD_R
    return half_w, half_l


def fit_screw_centres() -> List[Vec2]:
    return [
        (FIT_SCREW_X, FIT_SCREW_Y),
        (-FIT_SCREW_X, FIT_SCREW_Y),
        (FIT_SCREW_X, -FIT_SCREW_Y),
        (-FIT_SCREW_X, -FIT_SCREW_Y),
    ]


def fit_flange_tris(fit: Fit) -> List[Tri]:
    """8 mm pad: stepped M8 in the middle, U-bites at the edges, 4× #8 at the corners.

    Drop an M8 × 20 mm in from the open stub; the cap sits in the pad, not at the tip.
    """
    half_w, half_l = fit_pad_half(fit)
    outer = scalloped_rect_pts(half_w, half_l, FIT_CORNER_R, FIT_SCALLOP_NS_R, FIT_SCALLOP_EW_R)
    return loft_stepped_m8(outer, FIT_LUG_T, fit_screw_centres())


def fit_skirt_tris(fit: Fit, z0: float, z1: float) -> List[Tri]:
    """Six pillars with windows between them (filament savers around the stub)."""
    shaft_r = fit.shaft_d / 2.0
    inner_r = STUB_BORE_D / 2.0
    gap_a = SKIRT_WINDOW_W / max(shaft_r, 1.0)
    pitch = 2.0 * math.pi / SKIRT_WINDOW_COUNT
    pillar_a = pitch - gap_a
    if pillar_a < math.radians(12.0):
        pillar_a = math.radians(12.0)
    tris: List[Tri] = []
    # Windows sit between the 12/6 o'clock screw pads.
    a_off = math.radians(POCKET_OFFSET_DEG) + pitch / 2.0
    for k in range(SKIRT_WINDOW_COUNT):
        mid = a_off + k * pitch
        a0 = mid - pillar_a / 2.0
        a1 = mid + pillar_a / 2.0
        poly = annular_sector_pts(inner_r, shaft_r, a0, a1, 12)
        tris.extend(
            loft_layers(
                [
                    {"z": z0, "outer": poly, "holes": []},
                    {"z": z1, "outer": poly, "holes": []},
                ]
            )
        )
    return tris


def fit_test_tris(fit: Fit, indexed: bool = True) -> List[Tri]:
    """QR coupon: 6.5 mm spherical dimples, top at 22.7 mm, 6-up/4-down."""
    z_front = FIT_LUG_T
    z_from = z_front + 0.8
    tris: List[Tri] = []
    tris.extend(fit_flange_tris(fit))
    tris.extend(fit_skirt_tris(fit, z_front - 0.2, z_from + 0.2))
    tris.extend(stub_tris(fit, z_front, indexed=indexed, z_from=z_from))
    return tris


def wall_mount_tris(fit: Fit, indexed: bool = True) -> List[Tri]:
    return wall_plate_tris(fit) + stub_tris(fit, PLATE_T, indexed=indexed)


def profile_mount_tris(fit: Fit, indexed: bool = True) -> List[Tri]:
    return profile_plate_tris(fit) + stub_tris(fit, PLATE_T, indexed=indexed)


def svg_preview(path: str, fit: Fit) -> None:
    """Top + side view of the wall mount, dimensioned."""
    w, h = 640, 360
    scale = 2.4
    # origins
    top_c = (170, 180)
    side_c = (430, 180)

    def tx(x: float, y: float) -> str:
        return f"{top_c[0] + x * scale:.1f},{top_c[1] - y * scale:.1f}"

    def sx(z: float, r: float) -> str:
        return f"{side_c[0] + z * scale:.1f},{side_c[1] - r * scale:.1f}"

    shaft_r = fit.shaft_d / 2
    plate_r = PLATE_D / 2
    z_tip = PLATE_T + FILLET_R + SHAFT_LEN

    # side profile outline (upper half, mirrored)
    prof = qr_stub_profile(fit, PLATE_T, STUB_BORE_D / 2)
    # only the outer envelope for a readable sketch
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#111"/>',
        '<text x="170" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">Top</text>',
        '<text x="470" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">Side</text>',
        f'<text x="320" y="348" fill="#bbb" font-family="system-ui,sans-serif" font-size="13" text-anchor="middle">6.5 mm round dimples  ·  6-up/4-down  ·  top of cup at 22.7 mm</text>',
    ]
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{plate_r * scale}" fill="#2a2a2a" stroke="#f5a623" stroke-width="2"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{shaft_r * scale}" fill="#3d3d3d" stroke="#f5a623" stroke-width="1.5"/>'
    )
    lead_r = (fit.shaft_d - LEAD_D_DELTA) / 2
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{lead_r * scale:.1f}" fill="none" stroke="#888" stroke-dasharray="4 3"/>'
    )
    dimple_cr = shaft_r - DIMPLE_INSET
    for a_deg in POCKET_ANGLES_DEG:
        a = math.radians(a_deg)
        cx = top_c[0] + dimple_cr * math.cos(a) * scale
        cy = top_c[1] - dimple_cr * math.sin(a) * scale
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DIMPLE_R * scale:.1f}" fill="#111" stroke="#9d6" stroke-width="1.6"/>'
        )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{STUB_BORE_D / 2 * scale}" fill="#111" stroke="#6cf" stroke-dasharray="4 3"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{CENTER_CSK_D / 2 * scale}" fill="none" stroke="#6cf" stroke-width="1.4"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{CENTER_HOLE_D / 2 * scale}" fill="#111" stroke="#6cf"/>'
    )
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        x = SCREW_R * math.cos(a)
        y = SCREW_R * math.sin(a)
        parts.append(
            f'<circle cx="{top_c[0] + x * scale:.1f}" cy="{top_c[1] - y * scale:.1f}" r="{SCREW_CSK_D / 2 * scale}" fill="none" stroke="#6cf" stroke-width="1.2"/>'
        )
        parts.append(
            f'<circle cx="{top_c[0] + x * scale:.1f}" cy="{top_c[1] - y * scale:.1f}" r="{SCREW_D / 2 * scale}" fill="#111" stroke="#6cf"/>'
        )
    # side
    # plate
    parts.append(
        f'<rect x="{side_c[0]:.1f}" y="{side_c[1] - plate_r * scale:.1f}" width="{PLATE_T * scale:.1f}" height="{PLATE_D * scale:.1f}" fill="#2a2a2a" stroke="#f5a623"/>'
    )
    # shaft as two lines (upper/lower)
    def poly_side(sign: float) -> str:
        pts = []
        z0 = PLATE_T
        lead_r = (fit.shaft_d - LEAD_D_DELTA) / 2
        g_mid = z0 + FILLET_R + BALL_RING_FROM_FACE
        z_collar = g_mid - DIMPLE_R - COLLAR_BLEND
        z_full = z_collar + COLLAR_BLEND
        z_tip_l = z0 + FILLET_R + SHAFT_LEN
        pts.append(sx(0, sign * plate_r))
        pts.append(sx(z0, sign * plate_r))
        pts.append(sx(z0, sign * lead_r))
        pts.append(sx(z_collar, sign * lead_r))
        pts.append(sx(z_full, sign * shaft_r))
        pts.append(sx(z_tip_l - CHAMFER, sign * shaft_r))
        pts.append(sx(z_tip_l, sign * (shaft_r - CHAMFER)))
        return " ".join(pts)

    parts.append(
        f'<polyline points="{poly_side(1)}" fill="none" stroke="#f5a623" stroke-width="2"/>'
    )
    parts.append(
        f'<polyline points="{poly_side(-1)}" fill="none" stroke="#f5a623" stroke-width="2"/>'
    )
    parts.append(
        f'<line x1="{side_c[0] + z_tip * scale:.1f}" y1="{side_c[1] - (shaft_r - CHAMFER) * scale:.1f}" x2="{side_c[0] + z_tip * scale:.1f}" y2="{side_c[1] + (shaft_r - CHAMFER) * scale:.1f}" stroke="#f5a623"/>'
    )
    g_mid = PLATE_T + FILLET_R + BALL_RING_FROM_FACE
    for sign in (1.0, -1.0):
        cx = side_c[0] + g_mid * scale
        cy = side_c[1] - sign * dimple_cr * scale
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DIMPLE_R * scale:.1f}" fill="#111" stroke="#9d6" stroke-width="1.6"/>'
        )
    # dimensions
    parts.append(
        f'<text x="{top_c[0]}" y="{top_c[1] + plate_r * scale + 22}" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">{PLATE_D:.0f} mm plate</text>'
    )
    parts.append(
        f'<text x="{side_c[0] + (z_tip / 2) * scale:.1f}" y="{side_c[1] + plate_r * scale + 22}" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">~{z_tip:.0f} mm stand-off</text>'
    )
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def generate_all(out_dir: str, fit_name: str = DEFAULT_FIT) -> None:
    fit = FITS[fit_name]
    os.makedirs(out_dir, exist_ok=True)
    print(
        f"QR stub {SHAFT_LEN:.1f} mm  ·  6.5 mm spherical dimples  ·  "
        f"top {BALL_CUTOUT_TOP:.1f} mm  ·  6-up/4-down  ·  "
        f"{PIN_PLATE_DEPTH - SHAFT_LEN:.1f} mm short of pins"
    )
    jobs = [
        ("stl/moza_qr_universal_mount.stl", wall_mount_tris(fit, True), f"moza_qr_uni_{fit.name}"),
        ("stl/moza_qr_wall_mount.stl", wall_mount_tris(fit, True), f"moza_qr_wall_{fit.name}"),
        (
            "stl/moza_qr_wall_mount_free.stl",
            wall_mount_tris(fit, False),
            f"moza_qr_wall_free_{fit.name}",
        ),
        ("stl/moza_qr_8020_mount.stl", wall_mount_tris(fit, True), f"moza_qr_8020_{fit.name}"),
    ]
    for key, f in FITS.items():
        jobs.append((f"stl/fit_test_{key}.stl", fit_test_tris(f), f"fit_test_{key}"))

    for rel, tris, name in jobs:
        path = os.path.join(out_dir, rel)
        write_binary_stl(path, tris, name)
        lo, hi = bbox(tris)
        print(
            f"wrote {rel:32s}  tris={len(tris):6d}  "
            f"bbox=[{hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f}] mm"
        )
    svg_preview(os.path.join(out_dir, "preview.svg"), fit)
    print("wrote preview.svg")
    from accessories import generate_accessories

    generate_accessories(out_dir)
    write_kit_zip(out_dir)


KIT_ZIP_FILES = (
    "PRINT.txt",
    "stl/fit_test_nominal.stl",
    "stl/fit_test_tight.stl",
    "stl/fit_test_loose.stl",
    "stl/moza_qr_universal_mount.stl",
    "stl/moza_qr_wall_mount_free.stl",
    "stl/8020_phone_holder.stl",
    "stl/8020_cup_holder.stl",
    "stl/8020_headphone_hook.stl",
    "stl/8020_cable_clip.stl",
    "stl/8020_mouse_tray.stl",
)


def write_kit_zip(out_dir: str) -> None:
    zip_path = os.path.join(out_dir, "sim-rig-kit.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in KIT_ZIP_FILES:
            src = os.path.join(out_dir, rel)
            zf.write(src, arcname=os.path.basename(rel))
    print(f"wrote sim-rig-kit.zip  ({os.path.getsize(zip_path) // 1024} KB)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--fit",
        choices=list(FITS),
        default=DEFAULT_FIT,
        help="shaft/groove clearance for the full mounts (fit-test STLs always include all three)",
    )
    p.add_argument(
        "--out",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="output directory",
    )
    args = p.parse_args()
    generate_all(args.out, args.fit)


if __name__ == "__main__":
    main()
