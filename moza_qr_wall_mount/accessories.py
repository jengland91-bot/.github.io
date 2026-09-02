#!/usr/bin/env python3
"""8020 sim-rig accessories that share the wheel mount's M8 / 40 mm hardware.

Print flat (or as noted). No supports. PETG.

Units: millimetres.
"""

from __future__ import annotations

import math
import os
from typing import List, Sequence, Tuple

import generate as cad

Vec2 = cad.Vec2
Vec3 = cad.Vec3
Tri = cad.Tri

# Same T-nuts as the universal QR mount
HOLE_D = cad.PROFILE_HOLE_D
CSK_D = cad.PROFILE_HOLE_CSK_D
HOLE_N = 32
PLATE_T = 8.0
TAB_W = 54.0
PITCH = 40.0  # 4040 / 2020 slot spacing


def arc_pts(cx: float, cy: float, r: float, a0: float, a1: float, n: int) -> List[Vec2]:
    n = max(n, 2)
    return [
        (
            cx + r * math.cos(a0 + (a1 - a0) * i / (n - 1)),
            cy + r * math.sin(a0 + (a1 - a0) * i / (n - 1)),
        )
        for i in range(n)
    ]


def dedup_poly(poly: Sequence[Vec2], eps: float = 1e-7) -> List[Vec2]:
    out: List[Vec2] = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) <= eps and abs(out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def csk_hole_rings(centres: Sequence[Vec2]) -> Tuple[List[List[Vec2]], List[List[Vec2]]]:
    small = [cad.circle_pts(c[0], c[1], HOLE_D / 2.0, HOLE_N, False) for c in centres]
    csk = [cad.circle_pts(c[0], c[1], CSK_D / 2.0, HOLE_N, False) for c in centres]
    return small, csk


def plate_csk(
    outer: Sequence[Vec2],
    centres: Sequence[Vec2],
    z0: float,
    z1: float,
    extra_small: Sequence[Sequence[Vec2]] | None = None,
    extra_top: Sequence[Sequence[Vec2]] | None = None,
) -> List[Tri]:
    """Extrude a plate. Countersinks face +Z (the free / phone / cup side)."""
    small, csk = csk_hole_rings(centres)
    if extra_small:
        small = list(extra_small) + small
        csk_top = list(extra_top or extra_small) + csk
    else:
        csk_top = csk
    z_mid = max(z0 + 0.4, z1 - 4.0)
    outer_ccw = dedup_poly(cad.ensure_winding(outer, True))
    return cad.loft_layers(
        [
            {"z": z0, "outer": outer_ccw, "holes": small},
            {"z": z_mid, "outer": outer_ccw, "holes": small},
            {"z": z1, "outer": outer_ccw, "holes": csk_top},
        ]
    )


def rect_tab_pts(
    body_w: float,
    body_h: float,
    tab_w: float,
    tab_h: float,
    body_r: float,
    tab_r: float,
    n: int = 8,
    *,
    tab_on_plus_y: bool = True,
) -> List[Vec2]:
    """Rounded body with a narrower tab on +Y (or -Y). Body centred on origin."""
    bw, bh = body_w / 2.0, body_h / 2.0
    tw = min(tab_w / 2.0, bw - 0.2)
    br = min(body_r, bw - 0.2, bh - 0.2)
    tr = min(tab_r, tw - 0.2, tab_h / 2.0 - 0.2)
    if tab_on_plus_y:
        y_join, y_tip = bh, bh + tab_h
    else:
        y_join, y_tip = -bh, -bh - tab_h
    pts: List[Vec2] = []
    if tab_on_plus_y:
        pts += arc_pts(-bw + br, -bh + br, br, math.pi, 1.5 * math.pi, n)
        pts += arc_pts(bw - br, -bh + br, br, 1.5 * math.pi, 2.0 * math.pi, n)
        pts += arc_pts(bw - br, bh - br, br, 0.0, 0.5 * math.pi, n)
        pts.append((tw, y_join))
        pts += arc_pts(tw - tr, y_tip - tr, tr, 0.0, 0.5 * math.pi, n)
        pts += arc_pts(-tw + tr, y_tip - tr, tr, 0.5 * math.pi, math.pi, n)
        pts.append((-tw, y_join))
        pts += arc_pts(-bw + br, bh - br, br, 0.5 * math.pi, math.pi, n)
    else:
        pts += arc_pts(-bw + br, -bh + br, br, math.pi, 1.5 * math.pi, n)
        pts.append((-tw, y_join))
        pts += arc_pts(-tw + tr, y_tip + tr, tr, math.pi, 1.5 * math.pi, n)
        pts += arc_pts(tw - tr, y_tip + tr, tr, 1.5 * math.pi, 2.0 * math.pi, n)
        pts.append((tw, y_join))
        pts += arc_pts(bw - br, -bh + br, br, 1.5 * math.pi, 2.0 * math.pi, n)
        pts += arc_pts(bw - br, bh - br, br, 0.0, 0.5 * math.pi, n)
        pts += arc_pts(-bw + br, bh - br, br, 0.5 * math.pi, math.pi, n)
    return cad.ensure_winding(pts, True)


def u_channel_pts(
    inner_w: float,
    inner_h: float,
    wall: float,
    *,
    bottom_lip: float = 0.0,
) -> List[Vec2]:
    """Open-top U. Origin at the phone-pocket centre. Same vertex count for any lip."""
    iw, ih, w, lip = inner_w, inner_h, wall, bottom_lip
    ow = iw + 2.0 * w
    y_top = ih / 2.0
    y_ob = -ih / 2.0 - w
    y_ib = -ih / 2.0 + lip
    pts: List[Vec2] = [
        (-ow / 2.0, y_top),
        (-ow / 2.0, y_ob),
        (ow / 2.0, y_ob),
        (ow / 2.0, y_top),
        (ow / 2.0 - w, y_top),
        (ow / 2.0 - w, y_ib),
        (-ow / 2.0 + w, y_ib),
        (-ow / 2.0 + w, y_top),
    ]
    return cad.ensure_winding(pts, True)


# ---------------------------------------------------------------------------
# Right-side mouse tray — 5 x 5 in deck, bolts to the RIGHT face of a 4040
# ---------------------------------------------------------------------------
# Print = installed XY for the deck:
#   +X = forward along the rig (toward you)
#   +Y = outboard, to your right (pad sticks this way)
#   +Z = up the 4040
# Bolt plate sits at y = -PLATE_T..0 against the right face of the upright.
# Plate is at the rear of the 5 in edge so most of the pad is toward your hand.

MOUSE_DEPTH = 127.0  # 5 in sticking out to the right
MOUSE_LENGTH = 127.0  # 5 in along the rig
MOUSE_FLOOR = 3.2
MOUSE_LIP = 6.0
MOUSE_LIP_W = 2.8
MOUSE_PLATE_W = TAB_W
MOUSE_PLATE_H = 88.0
MOUSE_GUSSET = 20.0
MOUSE_PLATE_INSET = 3.0
MOUSE_CABLE_R = 6.0
MOUSE_HOLE_Z0 = 34.0  # lower M8, clears the gusset
MOUSE_HOLE_Z1 = MOUSE_HOLE_Z0 + PITCH
MOUSE_RIM = 12.0
MOUSE_RIB = 8.0


def map_tris(tris: Sequence[Tri], fn) -> List[Tri]:
    return [(fn(a), fn(b), fn(c)) for a, b, c in tris]


def mouse_plate_x() -> float:
    """Centre of the bolt plate along X (rear of the deck)."""
    return -MOUSE_LENGTH / 2.0 + MOUSE_PLATE_W / 2.0 + MOUSE_PLATE_INSET


def mouse_floor_pts(length: float, depth: float, r_in: float, r_out: float) -> List[Vec2]:
    n = 8
    hl = length / 2.0
    r_in = min(r_in, length / 4.0, depth / 4.0)
    r_out = min(r_out, length / 4.0, depth / 4.0)
    pts: List[Vec2] = []
    pts += arc_pts(-hl + r_in, r_in, r_in, math.pi, 1.5 * math.pi, n)
    pts += arc_pts(hl - r_in, r_in, r_in, 1.5 * math.pi, 2.0 * math.pi, n)
    pts += arc_pts(hl - r_out, depth - r_out, r_out, 0.0, 0.5 * math.pi, n)
    pts += arc_pts(-hl + r_out, depth - r_out, r_out, 0.5 * math.pi, math.pi, n)
    return cad.ensure_winding(pts, True)


def mouse_lip_pts(length: float, depth: float, wall: float) -> List[Vec2]:
    """U-lip open on the 8020 side (y = 0)."""
    hl, d, w = length / 2.0, depth, wall
    pts: List[Vec2] = [
        (-hl, 0.0),
        (-hl, d),
        (hl, d),
        (hl, 0.0),
        (hl - w, 0.0),
        (hl - w, d - w),
        (-hl + w, d - w),
        (-hl + w, 0.0),
    ]
    return cad.ensure_winding(pts, True)


def mouse_window_holes(length: float, depth: float) -> List[List[Vec2]]:
    """Large rounded windows. Ribs stay solid so the cantilever stays stiff."""
    rim, rib = MOUSE_RIM, MOUSE_RIB
    y0 = MOUSE_GUSSET + 6.0
    y1 = depth - rim
    x0 = -length / 2.0 + rim
    x1 = length / 2.0 - rim
    cols, rows = 2, 3
    usable_w = (x1 - x0) - rib * (cols - 1)
    usable_h = (y1 - y0) - rib * (rows - 1)
    ww = usable_w / cols
    hh = usable_h / rows
    rr = min(7.0, ww / 3.0, hh / 3.0)
    holes: List[List[Vec2]] = []
    for j in range(rows):
        for i in range(cols):
            cx = x0 + ww / 2.0 + i * (ww + rib)
            cy = y0 + hh / 2.0 + j * (hh + rib)
            hole = cad._shift(cad.rounded_rect_pts(ww, hh, rr, 6), cx, cy)
            holes.append(cad.ensure_winding(hole, False))
    return holes


def mouse_tray_tris() -> List[Tri]:
    """5x5 in tray for the right side of the sim. Windowed deck, pad sticks outboard."""
    d, l = MOUSE_DEPTH, MOUSE_LENGTH
    x_plate = mouse_plate_x()
    floor_outer = mouse_floor_pts(l, d, 6.0, 16.0)
    cable_c = (x_plate + 10.0, 16.0)
    cable = cad.ensure_winding(
        cad.circle_pts(cable_c[0], cable_c[1], MOUSE_CABLE_R, 24, False), False
    )
    holes = [cable] + mouse_window_holes(l, d)
    tris = cad.loft_layers(
        [
            {"z": 0.0, "outer": floor_outer, "holes": holes},
            {"z": MOUSE_FLOOR, "outer": floor_outer, "holes": holes},
        ]
    )
    lip = mouse_lip_pts(l, d, MOUSE_LIP_W)
    tris.extend(
        cad.loft_layers(
            [
                {"z": MOUSE_FLOOR, "outer": lip, "holes": []},
                {"z": MOUSE_FLOOR + MOUSE_LIP, "outer": lip, "holes": []},
            ]
        )
    )

    # Triangle gusset in YZ, extruded along the plate width (less plastic than a block).
    g = MOUSE_GUSSET
    gusset_xy = cad.ensure_winding([(0.0, 0.0), (g, 0.0), (0.0, g)], True)
    gw = MOUSE_PLATE_W - 8.0
    gusset = cad.extrude_with_holes(gusset_xy, [], [], -gw / 2.0, gw / 2.0)

    def gusset_to_world(p: Vec3) -> Vec3:
        # local (outboard, up, along) -> world (along + x_plate, outboard, up)
        return (p[2] + x_plate, p[0], p[1])

    tris.extend(map_tris(gusset, gusset_to_world))

    def z_to_local_y(z: float) -> float:
        return z - MOUSE_PLATE_H / 2.0

    plate_outer = cad.rounded_rect_pts(MOUSE_PLATE_W, MOUSE_PLATE_H, 10.0, 8)
    centres: List[Vec2] = [
        (0.0, z_to_local_y(MOUSE_HOLE_Z0)),
        (0.0, z_to_local_y(MOUSE_HOLE_Z1)),
    ]
    slot = cad.ensure_winding(
        cad._shift(
            cad.rounded_rect_pts(16.0, 18.0, 5.0, 6),
            0.0,
            z_to_local_y((MOUSE_HOLE_Z0 + MOUSE_HOLE_Z1) / 2.0),
        ),
        False,
    )
    plate = plate_csk(
        plate_outer, centres, 0.0, PLATE_T, extra_small=[slot], extra_top=[slot]
    )

    def park_plate(p: Vec3) -> Vec3:
        # local XY plate, +Z thickness/CSK -> world XZ plate, +Y CSK (pad side)
        x, y, z = p
        return (x + x_plate, z - PLATE_T, y + MOUSE_PLATE_H / 2.0)

    tris.extend(map_tris(plate, park_plate))
    return tris

PHONE_INNER_W = 174.0  # Pro Max + thick case
PHONE_INNER_H = 88.0
PHONE_DEPTH = 16.0
PHONE_WALL = 5.5
PHONE_LIP = 7.0  # front catch at the bottom so it cannot slide out
PHONE_TAB_H = 66.0
PHONE_TAB_W = 72.0  # wide enough for a horizontal 40 mm pair too


def phone_holder_tris() -> List[Tri]:
    iw, ih, wall = PHONE_INNER_W, PHONE_INNER_H, PHONE_WALL
    body_w = iw + 2.0 * wall
    body_h = ih + wall
    # Pocket centre at origin; body is shifted down by wall/2 because of the bottom wall
    body_cy = -wall / 2.0
    outer = cad._shift(
        rect_tab_pts(body_w, body_h, PHONE_TAB_W, PHONE_TAB_H, 10.0, 12.0, tab_on_plus_y=True),
        0.0,
        body_cy,
    )
    # Tab sits on the +Y edge of the body = ih/2 in pocket space
    tab_join = ih / 2.0
    y0 = tab_join + 13.0
    centres: List[Vec2] = [
        (0.0, y0),
        (0.0, y0 + PITCH),
        (-PITCH / 2.0, y0 + PITCH / 2.0),
        (PITCH / 2.0, y0 + PITCH / 2.0),
    ]
    tris = plate_csk(outer, centres, 0.0, PLATE_T)

    u0 = dedup_poly(u_channel_pts(iw, ih, wall, bottom_lip=0.0))
    u1 = dedup_poly(u_channel_pts(iw, ih, wall, bottom_lip=PHONE_LIP))
    z1 = PLATE_T + PHONE_DEPTH - 3.0
    z2 = PLATE_T + PHONE_DEPTH
    tris.extend(
        cad.loft_layers(
            [
                {"z": PLATE_T, "outer": u0, "holes": []},
                {"z": z1, "outer": u0, "holes": []},
                {"z": z2, "outer": u1, "holes": []},
            ]
        )
    )
    return tris


# ---------------------------------------------------------------------------
# Cup holder — ring on the bed, bolt to the TOP of a 4040 / 2020 beam
# ---------------------------------------------------------------------------

CUP_ID = 86.0
CUP_WALL = 5.5
CUP_H = 52.0
CUP_FLOOR = 5.0
CUP_DRAIN = 14.0
CUP_CHAMFER = 2.4


def cup_holder_tris() -> List[Tri]:
    r_out = CUP_ID / 2.0 + CUP_WALL
    r_in = CUP_ID / 2.0
    r_drain = CUP_DRAIN / 2.0
    n = 96
    tab_bottom = -118.0
    outer = cad.circle_tab_outline(r_out, TAB_W, tab_bottom, 12.0, n_circle=n, n_corner=10)
    join_y = -math.sqrt(max(r_out * r_out - (TAB_W / 2.0) ** 2, 1.0))
    centres: List[Vec2] = [(0.0, join_y - 18.0), (0.0, join_y - 18.0 - PITCH)]
    drain = [cad.circle_pts(0.0, 0.0, r_drain, n, False)]
    cup = [cad.circle_pts(0.0, 0.0, r_in, n, False)]
    m8s, m8_csk = csk_hole_rings(centres)
    z_floor = CUP_FLOOR
    z_ch = CUP_FLOOR + CUP_CHAMFER
    z_mid = CUP_H - 4.0
    return cad.loft_layers(
        [
            {"z": 0.0, "outer": outer, "holes": drain + m8s},
            {"z": z_floor, "outer": outer, "holes": drain + m8s},
            {"z": z_ch, "outer": outer, "holes": cup + m8s},
            {"z": z_mid, "outer": outer, "holes": cup + m8s},
            {"z": CUP_H, "outer": outer, "holes": cup + m8_csk},
        ]
    )


# ---------------------------------------------------------------------------
# Headphone hook — 2.5D J, print flat
# ---------------------------------------------------------------------------

HOOK_T = 20.0
HOOK_PLATE_W = 54.0
HOOK_PLATE_H = 78.0
HOOK_SHAFT = 14.0
HOOK_DROP = 44.0
HOOK_INNER = 17.0
HOOK_LIP_DEG = -18.0


def headphone_hook_pts() -> List[Vec2]:
    pw, ph = HOOK_PLATE_W, HOOK_PLATE_H
    pr = 10.0
    sw = HOOK_SHAFT
    thick = HOOK_SHAFT
    inner_r = HOOK_INNER
    outer_r = inner_r + thick
    cx = sw / 2.0 + inner_r
    cy = -HOOK_DROP
    lip = math.radians(HOOK_LIP_DEG)
    n_c, n_h = 8, 28
    pts: List[Vec2] = []
    pts += arc_pts(-pw / 2.0 + pr, ph - pr, pr, 0.5 * math.pi, math.pi, n_c)
    pts += arc_pts(-pw / 2.0 + pr, pr, pr, math.pi, 1.5 * math.pi, n_c)
    pts.append((-sw / 2.0, 0.0))
    pts += arc_pts(cx, cy, outer_r, math.pi, lip, n_h)
    pts += arc_pts(cx, cy, inner_r, lip, -math.pi, n_h)
    pts.append((sw / 2.0, 0.0))
    pts += arc_pts(pw / 2.0 - pr, pr, pr, 1.5 * math.pi, 2.0 * math.pi, n_c)
    pts += arc_pts(pw / 2.0 - pr, ph - pr, pr, 0.0, 0.5 * math.pi, n_c)
    return cad.ensure_winding(pts, True)


def headphone_hook_tris() -> List[Tri]:
    outer = headphone_hook_pts()
    # holes in the plate: 40 mm vertical, centred in the plate
    centres: List[Vec2] = [(0.0, 20.0), (0.0, 20.0 + PITCH)]
    return plate_csk(outer, centres, 0.0, HOOK_T)


# ---------------------------------------------------------------------------
# Cable clip — two snap slots + one M8
# ---------------------------------------------------------------------------

CLIP_T = 10.0


def cable_clip_pts() -> List[Vec2]:
    w, h, r = 58.0, 40.0, 7.0
    slot_w, slot_d, slot_r = 8.0, 20.0, 4.0
    xs = (-16.0, 16.0)
    n = 8
    hw, hh = w / 2.0, h / 2.0
    # CCW outer with two U-slots cut up from the bottom edge
    pts: List[Vec2] = []
    pts += arc_pts(-hw + r, hh - r, r, 0.5 * math.pi, math.pi, n)
    pts += arc_pts(-hw + r, -hh + r, r, math.pi, 1.5 * math.pi, n)
    for x in xs:
        sl, sr = x - slot_w / 2.0, x + slot_w / 2.0
        pts.append((sl, -hh))
        pts += arc_pts(x, -hh + slot_d - slot_r, slot_r, math.pi, 0.0, n)
        pts.append((sr, -hh))
    pts += arc_pts(hw - r, -hh + r, r, 1.5 * math.pi, 2.0 * math.pi, n)
    pts += arc_pts(hw - r, hh - r, r, 0.0, 0.5 * math.pi, n)
    return cad.ensure_winding(pts, True)


def cable_clip_tris() -> List[Tri]:
    outer = cable_clip_pts()
    centres: List[Vec2] = [(0.0, 8.0)]
    return plate_csk(outer, centres, 0.0, CLIP_T)


# ---------------------------------------------------------------------------
# Preview + generate
# ---------------------------------------------------------------------------

def svg_preview(path: str) -> None:
    w, h = 880, 560
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#111"/>',
        '<text x="440" y="28" fill="#eee" font-family="system-ui,sans-serif" font-size="16" text-anchor="middle">8020 sim-rig kit  ·  same M8 / 40 mm as the wheel mount</text>',
    ]

    def draw_poly(poly: Sequence[Vec2], ox: float, oy: float, scale: float, holes: Sequence[Sequence[Vec2]] = ()) -> None:
        def pt(p: Vec2) -> str:
            return f"{ox + p[0] * scale:.1f},{oy - p[1] * scale:.1f}"

        d = "M " + " L ".join(pt(p) for p in poly) + " Z"
        for hole in holes:
            d += " M " + " L ".join(pt(p) for p in hole) + " Z"
        parts.append(
            f'<path d="{d}" fill="#2a2a2a" fill-rule="evenodd" stroke="#f5a623" stroke-width="1.6"/>'
        )

    draw_poly(
        cad._shift(
            rect_tab_pts(
                PHONE_INNER_W + 2 * PHONE_WALL,
                PHONE_INNER_H + PHONE_WALL,
                PHONE_TAB_W,
                PHONE_TAB_H,
                10,
                12,
            ),
            0,
            -PHONE_WALL / 2,
        ),
        120,
        200,
        0.85,
        [cad.circle_pts(0, PHONE_INNER_H / 2 + 13 + i * PITCH, 4.2, 16, False) for i in (0, 1)],
    )
    parts.append(
        '<text x="120" y="318" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">Phone holder</text>'
    )
    draw_poly(
        cad.circle_tab_outline(CUP_ID / 2 + CUP_WALL, TAB_W, -118, 12),
        355,
        165,
        0.85,
        [cad.circle_pts(0, 0, CUP_ID / 2, 48, False)],
    )
    parts.append(
        '<text x="355" y="318" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">Cup holder</text>'
    )
    draw_poly(headphone_hook_pts(), 560, 175, 0.95)
    parts.append(
        '<text x="560" y="318" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">Headphone hook</text>'
    )
    draw_poly(
        cable_clip_pts(),
        760,
        175,
        1.6,
        [cad.circle_pts(0, 8, HOLE_D / 2, 16, False)],
    )
    parts.append(
        '<text x="760" y="318" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">Cable clip</text>'
    )

    x_plate = mouse_plate_x()
    cable_c = (x_plate + 10.0, 16.0)
    tray_holes = [cad.circle_pts(cable_c[0], cable_c[1], MOUSE_CABLE_R, 24, False)]
    tray_holes += mouse_window_holes(MOUSE_LENGTH, MOUSE_DEPTH)
    draw_poly(mouse_floor_pts(MOUSE_LENGTH, MOUSE_DEPTH, 6.0, 16.0), 320, 510, 1.2, tray_holes)
    parts.append(
        '<text x="320" y="545" fill="#6cf" font-family="system-ui,sans-serif" font-size="12" text-anchor="middle">Mouse tray (right side, lightened deck, sticks out)</text>'
    )
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def generate_accessories(out_dir: str) -> None:
    os.makedirs(os.path.join(out_dir, "stl"), exist_ok=True)
    jobs = [
        ("stl/8020_phone_holder.stl", phone_holder_tris(), "phone_holder"),
        ("stl/8020_cup_holder.stl", cup_holder_tris(), "cup_holder"),
        ("stl/8020_headphone_hook.stl", headphone_hook_tris(), "headphone_hook"),
        ("stl/8020_cable_clip.stl", cable_clip_tris(), "cable_clip"),
        ("stl/8020_mouse_tray.stl", mouse_tray_tris(), "mouse_tray"),
    ]
    for rel, tris, name in jobs:
        path = os.path.join(out_dir, rel)
        cad.write_binary_stl(path, tris, name)
        lo, hi = cad.bbox(tris)
        print(
            f"wrote {rel:32s}  tris={len(tris):6d}  "
            f"bbox=[{hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f}] mm"
        )
    svg_preview(os.path.join(out_dir, "accessories.svg"))
    print("wrote accessories.svg")


def main() -> None:
    generate_accessories(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    main()
