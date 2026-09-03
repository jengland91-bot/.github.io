#!/usr/bin/env python3
"""Generate the Stream Deck Plus ring, back plate, and hinged 4040 clamp."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cad import params as P
from cad.voxels import Voxels, bounds_of_tris, greedy_triangles, write_binary_stl


ROOT = Path(__file__).resolve().parent.parent
STL_DIR = ROOT / "stls"
TEMPLATE_DIR = ROOT / "templates"


def export(voxels: Voxels, path: Path, name: str):
    tris = greedy_triangles(voxels.occ, voxels.origin, voxels.pitch)
    write_binary_stl(path, tris, name)
    lo, hi = bounds_of_tris(tris)
    print(
        f"  {path.name}: {len(tris):,} tris, "
        f"bbox {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f} mm"
    )
    return len(tris)


def outer_size():
    return P.BODY_W + 2 * P.WALL, P.FACE_H + 2 * P.WALL


def inner_window():
    return P.BODY_W - 2 * P.LIP, P.FACE_H - 2 * P.LIP


def pocket_size():
    return P.BODY_W + P.CLEAR, P.FACE_H + P.CLEAR


def screw_xy():
    ow, oh = outer_size()
    x = ow / 2 - P.SCREW_INSET
    y = oh / 2 - P.SCREW_INSET
    return [(-x, -y), (x, -y), (-x, y), (x, y)]


def hinge_stack():
    """Half-width of the three-ear stack (outer face from centre)."""
    return P.HINGE_INNER_T / 2 + P.HINGE_GAP + P.HINGE_EAR_T


def build_front_ring(pitch=0.22) -> Voxels:
    """
    Skeletal ring: four screw corners with a lip, thin straps between them,
    and a wide cable gate on the logo end so a USB-C plug can drop in.
    """
    ow, oh = outer_size()
    iw, ih = inner_window()
    pw, ph = pocket_size()
    z_rim = P.RIM_T
    z_wall = z_rim + P.BODY_THICK + P.WALL_EXTRA
    r_out = P.BODY_CORNER_R + P.WALL
    r_win = max(P.BODY_CORNER_R - P.LIP, 2.0)
    post = P.POST

    v = Voxels(
        (-ow / 2 - 2, ow / 2 + 2, -oh / 2 - 2, oh / 2 + 2, -0.4, z_wall + 2),
        pitch=pitch,
    )
    v.add_rounded_box_z(0, 0, ow, oh, r_out, 0, z_rim)
    v.add_rounded_box_z(0, 0, ow, oh, r_out, z_rim, z_wall)
    v.sub_rounded_box_z(0, 0, iw, ih, r_win, -0.2, z_rim + 0.2)
    v.sub_rounded_box_z(0, 0, pw, ph, P.BODY_CORNER_R, z_rim - 0.05, z_wall + 0.3)

    # Hollow the mid-span walls; keep a thin face strap on three sides.
    # Left / right walls
    for sign in (-1, 1):
        x0, x1 = (pw / 2 - 0.2, ow / 2 + 1) if sign > 0 else (-ow / 2 - 1, -pw / 2 + 0.2)
        v.sub_box(x0, x1, -(oh / 2 - post), (oh / 2 - post), P.STRAP_T, z_wall + 0.4)
    # Dial-end wall
    v.sub_box(-(ow / 2 - post), (ow / 2 - post), ph / 2 - 0.2, oh / 2 + 1, P.STRAP_T, z_wall + 0.4)

    # Logo end: open cable gate (no strap) so the charger plugs through.
    v.sub_box(-(ow / 2 - post), (ow / 2 - post), -oh / 2 - 1, -ph / 2 + 1, -0.2, z_wall + 0.4)
    v.sub_box(-P.CABLE_W / 2, P.CABLE_W / 2, -oh / 2 - 1, -ph / 2 + P.CABLE_DEPTH, -0.2, z_wall + 0.4)

    # Slim the remaining face straps (leave STRAP_W of rim).
    v.sub_box(
        -(ow / 2 - post),
        (ow / 2 - post),
        (oh / 2 - P.STRAP_W),
        (ih / 2 - 0.2),
        -0.2,
        z_rim + 0.2,
    )
    for sign in (-1, 1):
        inner = sign * (iw / 2 - 0.2)
        outer = sign * (ow / 2 - P.STRAP_W)
        if inner > outer:
            inner, outer = outer, inner
        v.sub_box(inner, outer, -(oh / 2 - post), (oh / 2 - post), -0.2, z_rim + 0.2)

    for x, y in screw_xy():
        v.sub_cyl_z(x, y, P.M3_TAP / 2, z_rim + 0.3, z_wall + 0.3)
    return v


def build_back_plate(pitch=0.24) -> Voxels:
    """
    Plate the Plus sits on, plus one hinge ear on the back.

    Print plus-face on the bed (z=0). Hinge grows in +Z toward the clamp.
    Hinge axis is X (left-right) so the face nods up and down.
    """
    ow, oh = outer_size()
    pw, ph = pocket_size()
    r_out = P.BODY_CORNER_R + P.WALL
    z_top = P.PLATE_T
    pivot_z = z_top + P.HINGE_STANDOFF
    half_inner = P.HINGE_INNER_T / 2

    v = Voxels(
        (
            -ow / 2 - 2,
            ow / 2 + 2,
            -max(oh / 2, P.HINGE_EAR_R) - 2,
            max(oh / 2, P.HINGE_EAR_R) + 2,
            -0.4,
            pivot_z + P.HINGE_EAR_R + 2,
        ),
        pitch=pitch,
    )

    v.add_rounded_box_z(0, 0, ow, oh, r_out, 0, z_top)
    v.sub_rounded_box_z(0, 0, pw, ph, P.BODY_CORNER_R, -0.2, 1.0)

    # Four pockets — leave a border, corner pads, and a + rib into the hinge.
    rib = P.PLATE_RIB
    border = P.PLATE_BORDER
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        x0, x1 = sx * (rib / 2 + 1.5), sx * (ow / 2 - border)
        y0, y1 = sy * (rib / 2 + 1.5), sy * (oh / 2 - border)
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        v.sub_rounded_box_z(cx, cy, max(x1 - x0, 2), max(y1 - y0, 2), 3.5, -0.2, z_top + 0.3)

    # Open charger gate on the logo end — plug drops in, no threading.
    v.sub_box(-P.CABLE_W / 2, P.CABLE_W / 2, -oh / 2 - 1, -oh / 2 + P.CABLE_DEPTH, -0.2, z_top + 0.3)

    for x, y in screw_xy():
        v.sub_cyl_z(x, y, P.M3_SCREW / 2, -0.2, z_top + 0.3)
        v.sub_cyl_z(x, y, P.M3_HEAD / 2, z_top - 1.8, z_top + 0.3)

    for sign in (-1, 1):
        cx = sign * P.M3_STAND_SPACING / 2
        cy = -ph / 2 + P.M3_STAND_FROM_USB_EDGE
        v.sub_rounded_box_z(
            cx, cy, P.M3_STAND_HOLE, P.M3_STAND_SLOT, P.M3_STAND_HOLE / 2 - 0.05,
            -0.2, z_top + 0.3,
        )

    # Neck + round ear on the back. Hole along X.
    v.add_box(-half_inner, half_inner, -P.HINGE_EAR_R, P.HINGE_EAR_R, z_top - 0.2, pivot_z)
    v.add_cyl_x(0, pivot_z, P.HINGE_EAR_R, -half_inner, half_inner)
    v.sub_cyl_x(0, pivot_z, P.HINGE_HOLE / 2, -half_inner - 0.2, half_inner + 0.2)
    return v


def build_clamp(pitch=0.25) -> Voxels:
    """
    40-series U-clamp with two hinge ears. Extrusion runs along Y.
    Hinge axis is X — same as the back plate — so the deck nods.

    Print with the U opening up, or on the back wall.
    """
    inner = P.EXT + P.EXT_CLEAR
    wall = P.CLAMP_WALL
    length = P.CLAMP_LEN
    lip = P.CLAMP_LIP
    stack = hinge_stack()
    pivot_z = 0.0

    # 4040 sits past the ears in +Z.
    u_z0 = P.HINGE_EAR_R + 3
    bounds = (
        -stack - 2,
        stack + inner + wall + 2,
        -length / 2 - 2,
        length / 2 + 2,
        -P.HINGE_EAR_R - wall - 2,
        u_z0 + inner + wall + 2,
    )
    v = Voxels(bounds, pitch=pitch)

    # Two outer ears, gap in the middle for the back-plate ear.
    inner_half = P.HINGE_INNER_T / 2 + P.HINGE_GAP
    for sign in (-1, 1):
        x0 = sign * inner_half
        x1 = sign * stack
        if x0 > x1:
            x0, x1 = x1, x0
        v.add_box(x0, x1, -P.HINGE_EAR_R, P.HINGE_EAR_R, -P.HINGE_EAR_R, P.HINGE_EAR_R)
        v.add_cyl_x(0, pivot_z, P.HINGE_EAR_R, x0, x1)
        v.sub_cyl_x(0, pivot_z, P.HINGE_HOLE / 2, x0 - 0.2, x1 + 0.2)

    # Bridge behind the ears into the U back wall (lightened).
    v.add_box(-stack, stack, -length / 2, length / 2, P.HINGE_EAR_R - 4, u_z0 + wall)
    v.sub_box(-stack + 3, stack - 3, -length / 2 + 8, length / 2 - 8, P.HINGE_EAR_R - 1, u_z0 + wall + 0.2)

    # U-channel, extrusion along Y, opens +X so it slides onto a 40 mm face.
    # Inner: x stack..stack+inner, z u_z0..u_z0+inner
    x0 = stack
    x1 = stack + inner
    z0 = u_z0
    z1 = u_z0 + inner
    v.add_box(x0, x1 + wall, -length / 2, length / 2, z0 - wall, z0)  # floor
    v.add_box(x0, x1 + wall, -length / 2, length / 2, z1, z1 + wall)  # ceiling
    v.add_box(x1, x1 + wall, -length / 2, length / 2, z0, z1)  # back wall
    v.add_box(x0 - lip, x0, -length / 2, length / 2, z0 - wall, z0)  # lips
    v.add_box(x0 - lip, x0, -length / 2, length / 2, z1, z1 + wall)

    for sign in (-1, 1):
        v.sub_cyl_x(
            sign * P.M8_SPACING / 2,
            (z0 + z1) / 2,
            P.M8_HOLE / 2,
            x1 - 0.2,
            x1 + wall + 0.2,
        )
        v.sub_cyl_x(
            sign * P.M8_SPACING / 2,
            (z0 + z1) / 2,
            7.2,
            x1 + wall - 1.6,
            x1 + wall + 0.2,
        )
    return v


def write_template():
    page_w, page_h = 210.0, 297.0
    ow, oh = outer_size()
    iw, ih = inner_window()
    ox, oy = page_w / 2, 48 + oh / 2

    def sx(x):
        return ox + x

    def sy(y):
        return oy + y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_w}mm" height="{page_h}mm" viewBox="0 0 {page_w} {page_h}">',
        "<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#111} .dim{font-size:3.2px;fill:#333}</style>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<text x="12" y="14" font-size="5.5" font-weight="700">Stream Deck Plus outer ring — print at 100% scale</text>',
        '<text x="12" y="21" font-size="3.4">Measured 139.6 × 135.0 × 29.9 mm. Skeletal frame — corners + thin straps. Logo end is the cable gate.</text>',
        f'<text x="12" y="27" class="dim">Outer {ow:.1f} × {oh:.1f} mm  ·  window {iw:.1f} × {ih:.1f} mm  ·  lip {P.LIP:.1f} mm  ·  pocket {P.BODY_W + P.CLEAR:.1f} × {P.FACE_H + P.CLEAR:.1f}</text>',
        f'<rect x="{sx(-ow/2):.3f}" y="{sy(-oh/2):.3f}" width="{ow:.3f}" height="{oh:.3f}" rx="{P.BODY_CORNER_R + P.WALL}" fill="#e8e8e8" stroke="#111" stroke-width="0.35"/>',
        f'<rect x="{sx(-iw/2):.3f}" y="{sy(-ih/2):.3f}" width="{iw:.3f}" height="{ih:.3f}" rx="{max(P.BODY_CORNER_R - P.LIP, 2)}" fill="#fff" stroke="#111" stroke-width="0.35"/>',
        f'<rect x="{sx(-P.BODY_W/2):.3f}" y="{sy(-P.FACE_H/2):.3f}" width="{P.BODY_W:.3f}" height="{P.FACE_H:.3f}" rx="{P.BODY_CORNER_R}" fill="none" stroke="#888" stroke-width="0.25" stroke-dasharray="2 1.2"/>',
        f'<text x="{sx(0):.3f}" y="{sy(-oh/2 - 4):.3f}" text-anchor="middle" class="dim">logo / USB edge</text>',
        f'<text x="{sx(0):.3f}" y="{sy(oh/2 + 6):.3f}" text-anchor="middle" class="dim">dial edge</text>',
        "</svg>",
    ]
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    path = TEMPLATE_DIR / "ring-1to1.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"  wrote {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--part",
        choices=["all", "ring", "back", "clamp", "template"],
        default="all",
    )
    args = parser.parse_args()
    STL_DIR.mkdir(parents=True, exist_ok=True)

    ow, oh = outer_size()
    iw, ih = inner_window()
    print(
        f"Measured  {P.BODY_W} x {P.FACE_H} x {P.BODY_THICK} mm  "
        f"ring outer {ow:.1f} x {oh:.1f}  window {iw:.1f} x {ih:.1f}"
    )

    if args.part in ("all", "template"):
        write_template()
    if args.part in ("all", "ring"):
        export(build_front_ring(), STL_DIR / "front_ring.stl", "front_ring")
    if args.part in ("all", "back"):
        export(build_back_plate(), STL_DIR / "back_plate.stl", "back_plate")
    if args.part in ("all", "clamp"):
        export(build_clamp(), STL_DIR / "clamp_4040.stl", "clamp_4040")


if __name__ == "__main__":
    main()
