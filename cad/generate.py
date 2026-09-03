#!/usr/bin/env python3
"""Generate the Stream Deck Plus outer ring and 6 Sigma back plate."""

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


def build_front_ring(pitch=0.22) -> Voxels:
    """
    Picture-frame ring. Big open window — nothing over the keys or dials.
    Walls go back and meet the back plate. Four posts take M3 from the back.

    Print: visible rim on the bed, walls growing in +Z.
    +Y is the dial edge, -Y is the logo / USB edge.
    """
    ow, oh = outer_size()
    iw, ih = inner_window()
    pw, ph = pocket_size()
    z_rim = P.RIM_T
    z_wall = z_rim + P.BODY_THICK
    r_out = P.BODY_CORNER_R + P.WALL
    r_win = max(P.BODY_CORNER_R - P.LIP, 2.0)
    r_pocket = P.BODY_CORNER_R

    v = Voxels(
        (-ow / 2 - 2, ow / 2 + 2, -oh / 2 - 2, oh / 2 + 2, -0.4, z_wall + 2),
        pitch=pitch,
    )

    # Rim on the face, then walls around the body.
    v.add_rounded_box_z(0, 0, ow, oh, r_out, 0, z_rim)
    v.add_rounded_box_z(0, 0, ow, oh, r_out, z_rim, z_wall)
    v.sub_rounded_box_z(0, 0, iw, ih, r_win, -0.2, z_rim + 0.2)
    v.sub_rounded_box_z(0, 0, pw, ph, r_pocket, z_rim - 0.05, z_wall + 0.3)

    # USB notch through the logo-end wall.
    v.sub_box(-P.USB_W / 2, P.USB_W / 2, -oh / 2 - 1, -ph / 2 + 2, z_rim + 4, z_wall + 0.3)

    # M3 tap holes in the four corner posts. Stop before the visible rim
    # so the front of the frame stays clean. Screws come from the back.
    for x, y in screw_xy():
        v.sub_cyl_z(x, y, P.M3_TAP / 2, z_rim + 0.3, z_wall + 0.3)

    return v


def build_back_plate(pitch=0.25) -> Voxels:
    """
    Back plate the Plus sits on. Four M3 clearance holes match the ring.
    Two slotted M8 holes on a pad bolt into 40-series T-nuts on the rig.

    Print: extrusion pad on the bed (M8 holes up), Plus-facing side up.
    """
    ow, oh = outer_size()
    pw, ph = pocket_size()
    r_out = P.BODY_CORNER_R + P.WALL
    z0 = 0
    z_pad = P.M8_PAD_T
    z_top = z_pad + P.PLATE_T

    v = Voxels(
        (-ow / 2 - 2, ow / 2 + 2, -oh / 2 - 2, oh / 2 + 2, -0.4, z_top + 2),
        pitch=pitch,
    )

    v.add_rounded_box_z(0, 0, ow, oh, r_out, z_pad, z_top)
    # Shallow recess so the Plus locates on the plate.
    v.sub_rounded_box_z(0, 0, pw, ph, P.BODY_CORNER_R, z_top - 1.2, z_top + 0.3)

    # USB notch, logo end.
    v.sub_box(-P.USB_W / 2, P.USB_W / 2, -oh / 2 - 1, -ph / 2 + 3, z_pad - 0.1, z_top + 0.3)

    # Corner screws: clearance + head pocket on the extrusion side (bed).
    for x, y in screw_xy():
        v.sub_cyl_z(x, y, P.M3_SCREW / 2, -0.2, z_top + 0.3)
        v.sub_cyl_z(x, y, P.M3_HEAD / 2, -0.2, z_pad + 1.8)

    # Optional original stand-screw slots, in the recess.
    for sign in (-1, 1):
        cx = sign * P.M3_STAND_SPACING / 2
        cy = -ph / 2 + P.M3_STAND_FROM_USB_EDGE
        v.sub_rounded_box_z(
            cx, cy, P.M3_STAND_HOLE, P.M3_STAND_SLOT, P.M3_STAND_HOLE / 2 - 0.05,
            z_pad - 0.1, z_top + 0.3,
        )

    # 40-series pad on the extrusion side, two slotted M8s in one T-slot.
    pad_w = 28.0
    pad_h = P.M8_SPACING + P.M8_SLOT + 12.0
    v.add_rounded_box_z(0, 0, pad_w, pad_h, 3.0, 0, z_pad + 0.2)
    for sign in (-1, 1):
        v.sub_rounded_box_z(
            0,
            sign * P.M8_SPACING / 2,
            P.M8_HOLE,
            P.M8_SLOT,
            P.M8_HOLE / 2 - 0.05,
            -0.2,
            z_top + 0.3,
        )

    return v


def write_template():
    """1:1 SVG of the ring. Print at 100% and lay it on the Plus."""
    page_w, page_h = 210.0, 297.0
    ow, oh = outer_size()
    iw, ih = inner_window()
    ox, oy = page_w / 2, 55 + oh / 2

    def sx(x):
        return ox + x

    def sy(y):
        return oy + y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_w}mm" height="{page_h}mm" viewBox="0 0 {page_w} {page_h}">',
        "<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#111} .dim{font-size:3.2px;fill:#333}</style>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<text x="12" y="14" font-size="5.5" font-weight="700">Stream Deck Plus outer ring — print at 100% scale</text>',
        '<text x="12" y="21" font-size="3.4">Do not “fit to page”. Grey band is the frame. White window must leave every key and dial uncovered.</text>',
        f'<text x="12" y="27" class="dim">Outer {ow:.1f} × {oh:.1f} mm  ·  window {iw:.1f} × {ih:.1f} mm  ·  lip {P.LIP:.1f} mm</text>',
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
        choices=["all", "ring", "back", "template"],
        default="all",
    )
    args = parser.parse_args()
    STL_DIR.mkdir(parents=True, exist_ok=True)

    ow, oh = outer_size()
    iw, ih = inner_window()
    print(f"Ring outer {ow:.1f} x {oh:.1f} mm  window {iw:.1f} x {ih:.1f} mm  lip {P.LIP} mm")

    if args.part in ("all", "template"):
        write_template()
    if args.part in ("all", "ring"):
        export(build_front_ring(), STL_DIR / "front_ring.stl", "front_ring")
    if args.part in ("all", "back"):
        export(build_back_plate(), STL_DIR / "back_plate.stl", "back_plate")


if __name__ == "__main__":
    main()
