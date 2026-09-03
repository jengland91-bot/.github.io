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


# Sleeve ID measured on the user's wheel: 40.9 mm. PETG prints a hair large.
# Shaft is undersized so the collar can slide on; the six balls sit in a ring
# plus six deeper spots (one per ball) so it actually clicks.
FITS = {
    "tight": Fit("tight", shaft_d=40.2, groove_d=34.2),
    "nominal": Fit("nominal", shaft_d=39.8, groove_d=33.8),
    "loose": Fit("loose", shaft_d=39.4, groove_d=33.4),
}

DEFAULT_FIT = "nominal"

# Stub
SHAFT_LEN = 26.0  # plate front -> tip, including chamfer
CHAMFER = 2.2  # keep this short so the tip still has a full-diameter lip
FILLET_R = 0.0  # no extra OD at the root — a fillet was jamming in the 40.9 mm sleeve
GROOVE_FLAT = 3.8  # balls sit on a floor, not on the 45° ramps
GROOVE_FROM_TIP = 10.2  # extra cylinder between groove and tip so it cannot spit the wheel off
GROOVE_PLATE_AXIAL = 1.2  # steep backstop on the plate side (supported when printing stub-up)
STUB_BORE_D = 26.0  # hollow through the stub (wheel centre opening measured 22.4 mm)

# Six ball pockets — anti-rotation stops (Moza QR has 6 balls at 60°)
# Indexed stubs keep a RING so every ball can drop in, then six deeper seats
# so the wheel clocks and stays put. No lead-in channels — those turned the
# catch into a ramp and launched the wheel back off.
POCKET_COUNT = 6
POCKET_WIDTH_DEG = 40.0  # wide seats, one for each ball
POCKET_BLEND_DEG = 6.0
POCKET_OFFSET_DEG = 90.0  # first pocket at 12 o'clock when the top screw is up
LAND_RECESS = 2.4  # mm of ring groove between the six deep seats (must actually catch)
STUB_SEGMENTS = 180  # finer around the pockets

# Wall plate
PLATE_D = 98.0
PLATE_T = 8.0
RIM_CHAMFER = 1.8
SCREW_R = 36.0  # plus-pattern: N/E/S/W, so two screws can hit a stud
SCREW_D = 4.8  # clearance for #8 wood screw / 4.5 mm / M4
SCREW_CSK_D = 9.8
SCREW_CSK_DEPTH = 2.4
CENTER_HOLE_D = 8.4  # M8 through the stub (one bolt into a T-nut or a stud)
CENTER_CSK_D = 14.0  # M8 socket-cap head is ~13 mm; 22 mm was too sloppy
CENTER_CSK_DEPTH = 8.5  # head is ~8 mm; a hair extra so it sits down
CENTER_WASHER_T = 3.0  # plastic under the head (real step, not a zero-thickness face)
FIT_SCREW_X = 15.0  # four #8 at the corners of the pad
FIT_SCREW_Y = 26.0
FIT_LUG_PAD_R = 11.0  # meat around each #8
FIT_LUG_T = 8.0  # same as the 4040 strip so the screws have meat
FIT_FLANGE_EXTRA = 7.0  # extra ring all around the stub (green)
FIT_CORNER_R = 10.0  # flattened top/bottom ears
SKIRT_WINDOW_COUNT = 6  # filament-saver holes around the stub (red)
SKIRT_WINDOW_W = 8.0  # mm of opening at the outer wall
FIT_LIGHTEN_D = 9.0  # four holes around the centre M8 (plus a ring and two end holes)
FIT_LIGHTEN_X = 10.0
FIT_LIGHTEN_Y = 18.0
FIT_RING_N = 6  # extra ring of cutouts around the hub
FIT_RING_R = 22.0
FIT_RING_D = 6.8
FIT_RING_PHASE_DEG = 30.0  # sits between the four existing holes
FIT_END_D = 6.5  # two more along the long axis
FIT_END_Y = 31.0

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


def _groove_tapers(fit: Fit) -> Tuple[float, float, float]:
    """Plate-side axial, tip-side axial, radial depth of the full groove."""
    depth = fit.shaft_d / 2.0 - fit.groove_d / 2.0
    tip_axial = depth  # 45° overhang toward the tip
    plate_axial = min(depth, GROOVE_PLATE_AXIAL)  # steep backstop
    return plate_axial, tip_axial, depth


def _groove_z_band(z_base: float, fit: Fit) -> Tuple[float, float]:
    plate_axial, tip_axial, _ = _groove_tapers(fit)
    z_tip = z_base + FILLET_R + SHAFT_LEN
    g_mid = z_tip - GROOVE_FROM_TIP
    z0 = g_mid - GROOVE_FLAT / 2.0 - plate_axial
    z3 = g_mid + GROOVE_FLAT / 2.0 + tip_axial
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
            if indexed and r > STUB_BORE_D / 2.0 + 0.8 and z0 - 0.05 <= z <= z3 + 0.05:
                pt = pocket_t(t)
                # Hybrid: ring for all six balls + deeper seats. Leave the
                # cylinder between groove and tip untouched — that lip is
                # what stops the wheel shooting back off.
                cut = max(0.0, shaft_r - r)
                land_cut = min(cut, LAND_RECESS)
                rr = shaft_r - (land_cut + (cut - land_cut) * pt)
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
    fit: Fit, z_base: float, inner_r: float, z_from: float | None = None
) -> List[Vec2]:
    """Closed (r, z) loop for the tubular QR stub, including fillet and groove.

    z_from starts the solid above the plate (fit-test skirt is built separately).
    """
    shaft_r = fit.shaft_d / 2.0
    groove_r = fit.groove_d / 2.0
    plate_axial, tip_axial, _ = _groove_tapers(fit)
    z_tip = z_base + FILLET_R + SHAFT_LEN
    g_mid = z_tip - GROOVE_FROM_TIP
    g_half_flat = GROOVE_FLAT / 2.0
    z_g0 = g_mid - g_half_flat - plate_axial  # closer to plate (steep backstop)
    z_g1 = g_mid - g_half_flat
    z_g2 = g_mid + g_half_flat
    z_g3 = g_mid + g_half_flat + tip_axial  # closer to tip (45° overhang)
    z_start = z_base if z_from is None else z_from

    chamfer_z = z_tip - CHAMFER
    csk_r = CENTER_CSK_D / 2.0
    m8_r = CENTER_HOLE_D / 2.0
    z_well = z_tip - CENTER_CSK_DEPTH  # floor of the 14 mm pocket
    z_washer = z_well - CENTER_WASHER_T  # 3 mm of plastic under the head
    if z_washer < z_start + 0.4:
        z_washer = z_start + 0.4
        z_well = z_washer + CENTER_WASHER_T

    pts: List[Vec2] = [
        (inner_r, z_start),
        (inner_r, z_washer),
        (m8_r, z_washer),
        (m8_r, z_well),
        (csk_r, z_well),
        (csk_r, z_tip),
        (shaft_r - CHAMFER, z_tip),
        (shaft_r, chamfer_z),
        (shaft_r, z_g3),
        (groove_r, z_g2),
        (groove_r, z_g1),
        (shaft_r, z_g0),
    ]
    if z_start < z_g0 - 0.05:
        if FILLET_R > 0.15 and z_start <= z_base + 0.05:
            for i in range(FILLET_SEGS + 1):
                a = math.pi / 2 * (1.0 - i / FILLET_SEGS)  # pi/2 -> 0
                pts.append(
                    (
                        shaft_r + FILLET_R * math.cos(a),
                        z_base + FILLET_R * math.sin(a),
                    )
                )
        else:
            pts.append((shaft_r, z_start))
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


def wall_plate_tris(fit: Fit) -> List[Tri]:
    """Round plate: 4× #8 around the rim. The M8 is the hole through the stub."""
    hole_n = 32
    cut = _center_cut_d(fit)
    centres: List[Vec2] = [
        (0.0, SCREW_R),
        (SCREW_R, 0.0),
        (0.0, -SCREW_R),
        (-SCREW_R, 0.0),
        (0.0, 0.0),
    ]
    small_ds = [SCREW_D, SCREW_D, SCREW_D, SCREW_D, cut]
    csk_ds = [SCREW_CSK_D, SCREW_CSK_D, SCREW_CSK_D, SCREW_CSK_D, cut]
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


def fit_lighten_centres() -> List[Vec2]:
    return [
        (FIT_LIGHTEN_X, FIT_LIGHTEN_Y),
        (-FIT_LIGHTEN_X, FIT_LIGHTEN_Y),
        (FIT_LIGHTEN_X, -FIT_LIGHTEN_Y),
        (-FIT_LIGHTEN_X, -FIT_LIGHTEN_Y),
    ]


def fit_ring_centres() -> List[Vec2]:
    """Six extra cutouts around the hub, rotated to sit between the four existing holes."""
    out: List[Vec2] = []
    for i in range(FIT_RING_N):
        a = math.radians(FIT_RING_PHASE_DEG + i * 360.0 / FIT_RING_N)
        out.append((FIT_RING_R * math.cos(a), FIT_RING_R * math.sin(a)))
    return out


def fit_end_centres() -> List[Vec2]:
    return [(0.0, FIT_END_Y), (0.0, -FIT_END_Y)]


def fit_flange_tris(fit: Fit) -> List[Tri]:
    """8 mm pad: stepped M8 in the middle, 4× #8 at the corners, lightening holes.

    M8 is 8.4 mm through the bottom 3 mm (into the T-nut), then a 14 mm pocket
    from the stub side so a socket-cap head can sit down if it lands on the pad.
    The stub tip has the same 14 mm step — that is where the M8 × 40 mm head sits.
    """
    half_w, half_l = fit_pad_half(fit)
    outer = ensure_winding(
        rounded_rect_pts(2.0 * half_w, 2.0 * half_l, FIT_CORNER_R, 12),
        True,
    )
    hole_n = 24
    save_n = 16
    m8_n = 32
    m8 = circle_pts(0.0, 0.0, CENTER_HOLE_D / 2.0, m8_n, False)
    m8_pocket = circle_pts(0.0, 0.0, CENTER_CSK_D / 2.0, m8_n, False)
    screws = [
        circle_pts(c[0], c[1], SCREW_D / 2.0, hole_n, False) for c in fit_screw_centres()
    ]
    csks = [
        circle_pts(c[0], c[1], SCREW_CSK_D / 2.0, hole_n, False) for c in fit_screw_centres()
    ]
    light = [
        circle_pts(c[0], c[1], FIT_LIGHTEN_D / 2.0, hole_n, False)
        for c in fit_lighten_centres()
    ]
    ring = [
        circle_pts(c[0], c[1], FIT_RING_D / 2.0, save_n, False) for c in fit_ring_centres()
    ]
    ends = [
        circle_pts(c[0], c[1], FIT_END_D / 2.0, save_n, False) for c in fit_end_centres()
    ]
    extras = light + ring + ends
    z_web = CENTER_WASHER_T  # 3 mm of plastic under a head that sits on the pad
    z_csk = max(z_web + 0.4, FIT_LUG_T - SCREW_CSK_DEPTH)
    return loft_layers(
        [
            {"z": 0.0, "outer": outer, "holes": [m8] + screws + extras},
            {"z": z_web, "outer": outer, "holes": [m8] + screws + extras},
            {"z": z_web, "outer": outer, "holes": [m8_pocket] + screws + extras},
            {"z": z_csk, "outer": outer, "holes": [m8_pocket] + screws + extras},
            {"z": FIT_LUG_T, "outer": outer, "holes": [m8_pocket] + csks + extras},
        ]
    )


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
    """QR coupon: stepped M8 in the middle for 4040, 4× #8, extra cutouts.

    Print 3 walls / 15% to test the snap. If you hang the wheel on it, use 4/25 or 6/40.
    """
    z_g0, _z_g3 = _groove_z_band(0.0, fit)
    tris: List[Tri] = []
    tris.extend(fit_flange_tris(fit))
    tris.extend(fit_skirt_tris(fit, FIT_LUG_T - 0.2, z_g0 + 0.25))
    tris.extend(stub_tris(fit, 0.0, indexed=indexed, z_from=z_g0))
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
    prof = qr_stub_profile(fit, PLATE_T, STUB_BORE_D / 2)
    # only the outer envelope for a readable sketch
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#111"/>',
        '<text x="170" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">Top</text>',
        '<text x="470" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">Side</text>',
        f'<text x="320" y="348" fill="#bbb" font-family="system-ui,sans-serif" font-size="13" text-anchor="middle">Round plate  ·  M8 through the stub  ·  6 anti-spin pockets</text>',
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
        # plate front to tip along outer
        z0 = PLATE_T
        pts.append(sx(0, sign * plate_r))
        pts.append(sx(z0, sign * plate_r))
        pts.append(sx(z0, sign * (shaft_r + FILLET_R)))
        if FILLET_R > 0.15:
            for i in range(FILLET_SEGS + 1):
                a = math.pi / 2 * (1 - i / FILLET_SEGS)
                pts.append(
                    sx(
                        z0 + FILLET_R * math.sin(a),
                        sign * (shaft_r + FILLET_R * math.cos(a)),
                    )
                )
        plate_axial, tip_axial, _ = _groove_tapers(fit)
        z_tip_l = z0 + FILLET_R + SHAFT_LEN
        g_mid = z_tip_l - GROOVE_FROM_TIP
        z_g0 = g_mid - GROOVE_FLAT / 2 - plate_axial
        z_g1 = g_mid - GROOVE_FLAT / 2
        z_g2 = g_mid + GROOVE_FLAT / 2
        z_g3 = g_mid + GROOVE_FLAT / 2 + tip_axial
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
