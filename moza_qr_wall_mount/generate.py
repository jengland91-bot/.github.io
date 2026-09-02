#!/usr/bin/env python3
"""Generate 3D-printable Moza / D1-spec QR steering-wheel wall mounts.

The wheel-side quick release uses six spring-loaded balls. This mount is a
male-side stand-in with a continuous locking groove so you can hang the wheel
in any rotation — no lining up slots.

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

# 8020 / 4040 variant (lollipop tab hanging below the QR stub)
PROFILE_PLATE_W = 70.0
PROFILE_PLATE_H = 136.0
PROFILE_PLATE_Y = -30.0  # rectangle centre, so the tab hangs downward
PROFILE_HOLE_D = 8.4  # M8 clearance
PROFILE_HOLE_CSK_D = 14.0
PROFILE_HOLE_CSK_DEPTH = 4.0
PROFILE_HOLE_SPACING = 40.0  # 4040 T-nut spacing
PROFILE_HOLE_Y = (-46.0, -86.0)  # both below the ~29 mm fillet

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


def lathe(profile: Sequence[Vec2], n: int = SEGMENTS) -> List[Tri]:
    """Revolve an (r, z) polyline around Z. Open profiles stay open (no end cap)."""
    prof = list(profile)
    thetas = [2 * math.pi * i / n for i in range(n)]
    rings: List[List[Vec3]] = []
    for r, z in prof:
        r = max(r, 0.0)
        rings.append(
            [(r * math.cos(t), r * math.sin(t), z) for t in thetas]
        )
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


def wall_plate_tris(fit: Fit) -> List[Tri]:
    hole_n = 32
    centres: List[Vec2] = [
        (0.0, SCREW_R),
        (SCREW_R, 0.0),
        (0.0, -SCREW_R),
        (-SCREW_R, 0.0),
        (0.0, 0.0),
    ]
    cut = _center_cut_d(fit)
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
    outer = circle_pts(0.0, 0.0, PLATE_D / 2.0, SEGMENTS, ccw=True)
    outer_back = circle_pts(0.0, 0.0, PLATE_D / 2.0 - RIM_CHAMFER, SEGMENTS, True)
    outer_front = circle_pts(0.0, 0.0, PLATE_D / 2.0 - RIM_CHAMFER * 0.4, SEGMENTS, True)
    z_mid = PLATE_T - SCREW_CSK_DEPTH
    return loft_layers(
        [
            {"z": 0.0, "outer": outer_back, "holes": holes_small},
            {"z": RIM_CHAMFER, "outer": outer, "holes": holes_small},
            {"z": z_mid, "outer": outer, "holes": holes_small},
            {"z": PLATE_T, "outer": outer_front, "holes": holes_csk},
        ]
    )


def profile_plate_tris(fit: Fit) -> List[Tri]:
    outer = _shift(
        rounded_rect_pts(PROFILE_PLATE_W, PROFILE_PLATE_H, 12.0, n_each=10),
        0.0,
        PROFILE_PLATE_Y,
    )
    cut = _center_cut_d(fit)
    centres = [(0.0, y) for y in PROFILE_HOLE_Y] + [(0.0, 0.0)]
    ds = [PROFILE_HOLE_D, PROFILE_HOLE_D, cut]
    csk = [PROFILE_HOLE_CSK_D, PROFILE_HOLE_CSK_D, cut]
    hole_n = 32
    holes_s = [
        circle_pts(c[0], c[1], d / 2.0, hole_n, False) for c, d in zip(centres, ds)
    ]
    holes_c = [
        circle_pts(c[0], c[1], d / 2.0, hole_n, False) for c, d in zip(centres, csk)
    ]
    z_mid = PLATE_T - PROFILE_HOLE_CSK_DEPTH
    return loft_layers(
        [
            {"z": 0.0, "outer": outer, "holes": holes_s},
            {"z": z_mid, "outer": outer, "holes": holes_s},
            {"z": PLATE_T, "outer": outer, "holes": holes_c},
        ]
    )


def stub_tris(fit: Fit, z_front: float) -> List[Tri]:
    inner_r = CENTER_HOLE_D / 2.0
    return lathe(qr_stub_profile(fit, z_front, inner_r), SEGMENTS)


def fit_test_tris(fit: Fit) -> List[Tri]:
    """Short QR coupon with a small finger flange — ~15 min print."""
    flange_d = 62.0
    flange_t = 5.0
    outer = circle_pts(0.0, 0.0, flange_d / 2.0, SEGMENTS, True)
    inner = [circle_pts(0.0, 0.0, CENTER_HOLE_D / 2.0, 32, False)]
    tris = extrude_with_holes(outer, inner, inner, 0.0, flange_t)
    tris.extend(stub_tris(fit, flange_t))
    return tris


def wall_mount_tris(fit: Fit) -> List[Tri]:
    return wall_plate_tris(fit) + stub_tris(fit, PLATE_T)


def profile_mount_tris(fit: Fit) -> List[Tri]:
    return profile_plate_tris(fit) + stub_tris(fit, PLATE_T)


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
        f'<text x="320" y="340" fill="#bbb" font-family="system-ui,sans-serif" font-size="13" text-anchor="middle">Moza / D1-spec QR wall mount  ·  {fit.name} fit  ·  shaft {fit.shaft_d:.1f} mm</text>',
    ]
    # top: plate + screws + shaft
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{plate_r * scale}" fill="#2a2a2a" stroke="#f5a623" stroke-width="2"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{shaft_r * scale}" fill="#3d3d3d" stroke="#f5a623" stroke-width="1.5"/>'
    )
    parts.append(
        f'<circle cx="{top_c[0]}" cy="{top_c[1]}" r="{groove_r * scale}" fill="none" stroke="#888" stroke-dasharray="4 3"/>'
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
        ("stl/moza_qr_wall_mount.stl", wall_mount_tris(fit), f"moza_qr_wall_{fit.name}"),
        ("stl/moza_qr_8020_mount.stl", profile_mount_tris(fit), f"moza_qr_8020_{fit.name}"),
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
