#!/usr/bin/env python3
"""Generate 3D-printable Moza / D1-spec QR steering-wheel wall mounts.

The wheel-side quick release uses six spring-loaded balls. The default stub has
six ball pockets so the wheel cannot spin when bumped (same idea as the metal
QR on the base). A free-spin ring-groove variant is also generated.

Also writes the 8020 accessory kit (phone holder, cup, headphone hook, cable
clip) via accessories.py.

Units: millimetres.
"""

from __future__ import annotations

import argparse
import math
import os
import struct
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


FITS = {
    "tight": Fit("tight", shaft_d=49.8, groove_d=45.8),
    "nominal": Fit("nominal", shaft_d=49.4, groove_d=45.4),
    "loose": Fit("loose", shaft_d=49.0, groove_d=45.0),
}

DEFAULT_FIT = "nominal"

# Stub
SHAFT_LEN = 26.0  # plate front -> tip, including chamfer
CHAMFER = 2.4
FILLET_R = 4.5
GROOVE_FLAT = 1.4  # mm of constant-depth groove between 45° walls
GROOVE_FROM_TIP = 8.8  # centre of groove, measured from the free end

# Six ball pockets — anti-rotation stops (Moza QR has 6 balls at 60°)
POCKET_COUNT = 6
POCKET_WIDTH_DEG = 24.0  # seat width; lands between them block spin
POCKET_BLEND_DEG = 5.0
POCKET_OFFSET_DEG = 90.0  # first pocket at 12 o'clock when the top screw is up
STUB_SEGMENTS = 144  # finer around the pockets

# Wall plate
PLATE_D = 98.0
PLATE_T = 8.0
RIM_CHAMFER = 1.8
SCREW_R = 36.0  # plus-pattern: N/E/S/W, so two screws can hit a stud
SCREW_D = 4.8  # clearance for #8 wood screw / 4.5 mm / M4
SCREW_CSK_D = 9.8
SCREW_CSK_DEPTH = 2.4
CENTER_HOLE_D = 5.5  # optional M5 into a stud, hidden by the wheel
CENTER_CSK_D = 11.0
CENTER_CSK_DEPTH = 3.0

# Product bezel — raised ring so the plate looks finished, not like a raw disc
BEZEL_W = 4.2
BEZEL_H = 1.6

# Accessories still use a tab outline; the wheel mount itself is a round disc.
TAB_W = 54.0
TAB_BOTTOM = -114.0
TAB_CORNER_R = 14.0
PROFILE_HOLE_D = 8.4  # M8 clearance
PROFILE_HOLE_CSK_D = 14.0
# M8 at 12 o'clock and 6 o'clock on the round plate.
# Outboard of the stub opening so the Ø14 CSK does not kiss the centre cut.
PROFILE_HOLE_R = 39.0

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
    best = min(
        _angle_diff(
            theta, math.radians(POCKET_OFFSET_DEG) + k * (2 * math.pi / POCKET_COUNT)
        )
        for k in range(POCKET_COUNT)
    )
    if best <= max(0.0, half - blend):
        return 1.0
    if best >= half + blend:
        return 0.0
    x = (half + blend - best) / (2 * blend)
    return x * x * (3.0 - 2.0 * x)


def _groove_z_band(z_base: float, fit: Fit) -> Tuple[float, float]:
    shaft_r = fit.shaft_d / 2.0
    groove_r = fit.groove_d / 2.0
    taper = shaft_r - groove_r
    z_tip = z_base + FILLET_R + SHAFT_LEN
    g_mid = z_tip - GROOVE_FROM_TIP
    z0 = g_mid - GROOVE_FLAT / 2.0 - taper
    z3 = g_mid + GROOVE_FLAT / 2.0 + taper
    return z0, z3


def lathe(
    profile: Sequence[Vec2],
    n: int = SEGMENTS,
    *,
    fit: Fit | None = None,
    z_base: float | None = None,
    indexed: bool = False,
) -> List[Tri]:
    """Revolve an (r, z) polyline around Z. Open profiles stay open (no end cap).

    indexed=True cuts six ball pockets into the groove so the wheel cannot spin.
    """
    prof = list(profile)
    thetas = [2 * math.pi * i / n for i in range(n)]
    shaft_r = fit.shaft_d / 2.0 if fit is not None else 0.0
    z0 = z3 = 0.0
    if indexed and fit is not None and z_base is not None:
        z0, z3 = _groove_z_band(z_base, fit)
    rings: List[List[Vec3]] = []
    for r, z in prof:
        r = max(r, 0.0)
        ring: List[Vec3] = []
        for t in thetas:
            rr = r
            if indexed and z0 - 0.05 <= z <= z3 + 0.05 and r > 12.0:
                rr = shaft_r + (r - shaft_r) * pocket_t(t)
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


def qr_stub_profile(fit: Fit, z_base: float, inner_r: float) -> List[Vec2]:
    """Closed (r, z) loop for the tubular QR stub, including fillet and groove."""
    shaft_r = fit.shaft_d / 2.0
    groove_r = fit.groove_d / 2.0
    depth = shaft_r - groove_r
    taper = depth  # 45° print-friendly walls
    z_tip = z_base + FILLET_R + SHAFT_LEN
    g_mid = z_tip - GROOVE_FROM_TIP
    g_half_flat = GROOVE_FLAT / 2.0
    z_g0 = g_mid - g_half_flat - taper  # closer to plate
    z_g1 = g_mid - g_half_flat
    z_g2 = g_mid + g_half_flat
    z_g3 = g_mid + g_half_flat + taper  # closer to tip

    z_shaft0 = z_base + FILLET_R
    chamfer_z = z_tip - CHAMFER
    csk_z = z_tip - CENTER_CSK_DEPTH
    csk_r = CENTER_CSK_D / 2.0

    pts: List[Vec2] = [
        (inner_r, z_base),
        (inner_r, csk_z),
        (csk_r, z_tip),
        (shaft_r - CHAMFER, z_tip),
        (shaft_r, chamfer_z),
        (shaft_r, z_g3),
        (groove_r, z_g2),
        (groove_r, z_g1),
        (shaft_r, z_g0),
        (shaft_r, z_shaft0),
    ]
    # fillet: centre (shaft_r, z_base), from (shaft_r, z_base+R) to (shaft_r+R, z_base)
    for i in range(FILLET_SEGS + 1):
        a = math.pi / 2 * (1.0 - i / FILLET_SEGS)  # pi/2 -> 0
        pts.append((shaft_r + FILLET_R * math.cos(a), z_base + FILLET_R * math.sin(a)))
    return pts


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

def _center_cut_d(fit: Fit) -> float:
    """Plate opening the stub sits in — slightly smaller than the fillet so they overlap."""
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


def wall_plate_tris(fit: Fit) -> List[Tri]:
    """Round plate: #8 left/right for a wall, M8 top/bottom for 4040 / 2020."""
    hole_n = 32
    cut = _center_cut_d(fit)
    centres: List[Vec2] = [
        (SCREW_R, 0.0),
        (-SCREW_R, 0.0),
        (0.0, PROFILE_HOLE_R),
        (0.0, -PROFILE_HOLE_R),
        (0.0, 0.0),
    ]
    small_ds = [SCREW_D, SCREW_D, PROFILE_HOLE_D, PROFILE_HOLE_D, cut]
    csk_ds = [
        SCREW_CSK_D,
        SCREW_CSK_D,
        PROFILE_HOLE_CSK_D,
        PROFILE_HOLE_CSK_D,
        cut,
    ]
    holes_small = [
        circle_pts(c[0], c[1], d / 2.0, hole_n, ccw=False)
        for c, d in zip(centres, small_ds)
    ]
    holes_csk = [
        circle_pts(c[0], c[1], d / 2.0, hole_n, ccw=False)
        for c, d in zip(centres, csk_ds)
    ]
    outer = circle_pts(0.0, 0.0, PLATE_D / 2.0, SEGMENTS, True)
    z_mid = PLATE_T - 4.0
    return loft_layers(
        [
            {"z": 0.0, "outer": outer, "holes": holes_small},
            {"z": z_mid, "outer": outer, "holes": holes_small},
            {"z": PLATE_T, "outer": outer, "holes": holes_csk},
        ]
    )


def profile_plate_tris(fit: Fit) -> List[Tri]:
    return wall_plate_tris(fit)


def stub_tris(fit: Fit, z_front: float, indexed: bool = True) -> List[Tri]:
    inner_r = CENTER_HOLE_D / 2.0
    return lathe(
        qr_stub_profile(fit, z_front, inner_r),
        STUB_SEGMENTS,
        fit=fit,
        z_base=z_front,
        indexed=indexed,
    )


def fit_test_tris(fit: Fit, indexed: bool = True) -> List[Tri]:
    """Short QR coupon with a small finger flange — ~15 min print."""
    flange_d = 62.0
    flange_t = 5.0
    outer = circle_pts(0.0, 0.0, flange_d / 2.0, SEGMENTS, True)
    inner = [circle_pts(0.0, 0.0, CENTER_HOLE_D / 2.0, 32, False)]
    tris = extrude_with_holes(outer, inner, inner, 0.0, flange_t)
    tris.extend(stub_tris(fit, flange_t, indexed=indexed))
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
    groove_r = fit.groove_d / 2
    plate_r = PLATE_D / 2
    z_tip = PLATE_T + FILLET_R + SHAFT_LEN

    # side profile outline (upper half, mirrored)
    prof = qr_stub_profile(fit, PLATE_T, CENTER_HOLE_D / 2)
    # only the outer envelope for a readable sketch
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#111"/>',
        '<text x="170" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">Top</text>',
        '<text x="470" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">Side</text>',
        f'<text x="320" y="348" fill="#bbb" font-family="system-ui,sans-serif" font-size="13" text-anchor="middle">Round plate  ·  M8 top & bottom  ·  6 anti-spin pockets</text>',
    ]
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{plate_r * scale}" fill="#2a2a2a" stroke="#f5a623" stroke-width="2"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{shaft_r * scale}" fill="#3d3d3d" stroke="#f5a623" stroke-width="1.5"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{groove_r * scale}" fill="none" stroke="#888" stroke-dasharray="4 3"/>'
    )
    for k in range(POCKET_COUNT):
        a = math.radians(POCKET_OFFSET_DEG + k * 360.0 / POCKET_COUNT)
        x0 = (groove_r + 0.4) * math.cos(a) * scale
        y0 = (groove_r + 0.4) * math.sin(a) * scale
        x1 = (shaft_r + 2.5) * math.cos(a) * scale
        y1 = (shaft_r + 2.5) * math.sin(a) * scale
        parts.append(
            f'<line x1="{top_c[0] + x0:.1f}" y1="{top_c[1] - y0:.1f}" x2="{top_c[0] + x1:.1f}" y2="{top_c[1] - y1:.1f}" stroke="#6cf" stroke-width="2"/>'
        )
    for x, y, csk, d in (
        (SCREW_R, 0.0, SCREW_CSK_D, SCREW_D),
        (-SCREW_R, 0.0, SCREW_CSK_D, SCREW_D),
        (0.0, PROFILE_HOLE_R, PROFILE_HOLE_CSK_D, PROFILE_HOLE_D),
        (0.0, -PROFILE_HOLE_R, PROFILE_HOLE_CSK_D, PROFILE_HOLE_D),
    ):
        parts.append(
            f'<circle cx="{top_c[0] + x * scale:.1f}" cy="{top_c[1] - y * scale:.1f}" r="{csk / 2 * scale}" fill="none" stroke="#6cf" stroke-width="1.2"/>'
        )
        parts.append(
            f'<circle cx="{top_c[0] + x * scale:.1f}" cy="{top_c[1] - y * scale:.1f}" r="{d / 2 * scale}" fill="#111" stroke="#6cf"/>'
        )
    # side
    # plate
    parts.append(
        f'<rect x="{side_c[0]:.1f}" y="{side_c[1] - plate_r * scale:.1f}" width="{PLATE_T * scale:.1f}" height="{PLATE_D * scale:.1f}" fill="#2a2a2a" stroke="#f5a623"/>'
    )
    # shaft as two lines (upper/lower)
    def poly_side(sign: float) -> str:
        pts = []
        # plate front to tip along outer
        z0 = PLATE_T
        pts.append(sx(0, sign * plate_r))
        pts.append(sx(z0, sign * plate_r))
        pts.append(sx(z0, sign * (shaft_r + FILLET_R)))
        for i in range(FILLET_SEGS + 1):
            a = math.pi / 2 * (1 - i / FILLET_SEGS)
            pts.append(
                sx(
                    z0 + FILLET_R * math.sin(a),
                    sign * (shaft_r + FILLET_R * math.cos(a)),
                )
            )
        depth = shaft_r - groove_r
        z_tip_l = z0 + FILLET_R + SHAFT_LEN
        g_mid = z_tip_l - GROOVE_FROM_TIP
        z_g0 = g_mid - GROOVE_FLAT / 2 - depth
        z_g1 = g_mid - GROOVE_FLAT / 2
        z_g2 = g_mid + GROOVE_FLAT / 2
        z_g3 = g_mid + GROOVE_FLAT / 2 + depth
        pts.append(sx(z_g0, sign * shaft_r))
        pts.append(sx(z_g1, sign * groove_r))
        pts.append(sx(z_g2, sign * groove_r))
        pts.append(sx(z_g3, sign * shaft_r))
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
