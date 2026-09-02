#!/usr/bin/env python3
"""Generate Stream Deck Plus faceplate + 6 Sigma / 40-series mount STLs."""

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


def report(name, voxels: Voxels, ntris: int):
    occ = voxels.occupied()
    print(f"  {name}: {occ:,} voxels, {ntris:,} triangles")


def export(voxels: Voxels, path: Path, name: str):
    tris = greedy_triangles(voxels.occ, voxels.origin, voxels.pitch)
    write_binary_stl(path, tris, name)
    lo, hi = bounds_of_tris(tris)
    print(
        f"  {path.name}: {len(tris):,} tris, "
        f"bbox {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f} mm"
    )
    return len(tris)


def punch_face_cutouts(v: Voxels, z0, z1):
    """Key / touch / dial openings through a plate in Z."""
    ks = P.KEY_SIZE + P.KEY_CLEAR
    for x in P.key_xs():
        for y in P.key_ys():
            v.sub_rounded_box_z(x, y, ks, ks, P.KEY_CORNER_R, z0, z1)

    v.sub_rounded_box_z(
        0,
        P.touch_center_y(),
        P.TOUCH_W + P.TOUCH_CLEAR * 2,
        P.TOUCH_H + P.TOUCH_CLEAR * 2,
        1.2,
        z0,
        z1,
    )

    dial_r = (P.DIAL_D + P.DIAL_CLEAR) / 2
    for x in P.dial_xs():
        v.sub_cyl_z(x, P.dial_center_y(), dial_r, z0, z1)


def build_faceplate(pitch=0.2) -> Voxels:
    """
    Print face-down (visible face on the bed). Skirt grows in +Z and clips
    around the Stream Deck Plus bezel. Pull the four dial caps off, drop
    the plate on, then press the caps back — they retain it.
    """
    outer_w = P.FACE_W + P.PLATE_MARGIN * 2
    outer_h = P.FACE_H + P.PLATE_MARGIN * 2
    z_plate = P.PLATE_THICK
    z_skirt = z_plate + P.SKIRT_H
    bounds = (
        -outer_w / 2 - 2,
        outer_w / 2 + 2,
        -outer_h / 2 - 2,
        outer_h / 2 + 2,
        -0.5,
        z_skirt + 2,
    )
    v = Voxels(bounds, pitch=pitch)

    v.add_rounded_box_z(0, 0, outer_w, outer_h, P.PLATE_R, 0, z_plate)

    # Skirt: outer rounded rect minus inner (body) opening.
    inner_w = P.BODY_W + P.CLEAR
    inner_h = P.FACE_H + P.CLEAR
    v.add_rounded_box_z(0, 0, outer_w, outer_h, P.PLATE_R, z_plate, z_skirt)
    v.sub_rounded_box_z(0, 0, inner_w, inner_h, P.BODY_CORNER_R, z_plate - 0.1, z_skirt + 0.1)

    # Inward snap lip at the rim of the skirt.
    lip_z0 = z_skirt - 1.3
    v.add_rounded_box_z(0, 0, inner_w, inner_h, P.BODY_CORNER_R, lip_z0, z_skirt)
    v.sub_rounded_box_z(
        0,
        0,
        inner_w - 2 * P.LIP,
        inner_h - 2 * P.LIP,
        max(P.BODY_CORNER_R - P.LIP, 1.0),
        lip_z0 - 0.1,
        z_skirt + 0.1,
    )

    punch_face_cutouts(v, -0.2, z_plate + 0.2)

    # Cable / finger notch at the USB-C edge (top of face = logo, bottom = dials).
    # USB is on the back of the housing; a small notch at the logo end of the
    # skirt makes it easier to lift the plate off.
    v.sub_box(-8, 8, -outer_h / 2 - 1, -inner_h / 2 + 2, z_plate, z_skirt + 0.2)

    return v


def build_fit_gauge(pitch=0.2) -> Voxels:
    """Thin 1:1 cutout plate. Print this first and lay it on the Plus."""
    outer_w = P.FACE_W + P.PLATE_MARGIN * 2
    outer_h = P.FACE_H + P.PLATE_MARGIN * 2
    t = 1.2
    v = Voxels(
        (-outer_w / 2 - 1, outer_w / 2 + 1, -outer_h / 2 - 1, outer_h / 2 + 1, -0.2, t + 0.2),
        pitch=pitch,
    )
    v.add_rounded_box_z(0, 0, outer_w, outer_h, P.PLATE_R, 0, t)
    punch_face_cutouts(v, -0.2, t + 0.2)
    return v


def build_cradle(pitch=0.28) -> Voxels:
    """
    Tray the Plus drops into after the stand is removed.

    +X right, +Y toward USB-C / hinge (back of the device), +Z toward the face.
    Floor on the print bed. Front lip at -Y keeps it from sliding toward you.
    """
    inner_w = P.CRADLE_INNER_W
    inner_d = P.CRADLE_INNER_D
    inner_h = P.CRADLE_INNER_H
    wall = P.WALL
    floor = P.FLOOR
    outer_w = inner_w + 2 * wall
    outer_d = inner_d + 2 * wall
    outer_h = floor + inner_h

    # Hinge ear sticks out past the back wall.
    ear_extra = P.HINGE_STANDOFF + P.HINGE_EAR_R + 2
    bounds = (
        -outer_w / 2 - 2,
        outer_w / 2 + 2,
        -outer_d / 2 - 2,
        outer_d / 2 + ear_extra,
        -0.5,
        outer_h + 2,
    )
    v = Voxels(bounds, pitch=pitch)

    # Outer shell and inner pocket.
    v.add_rounded_box_z(0, 0, outer_w, outer_d, P.CRADLE_CORNER_R, 0, outer_h)
    v.sub_rounded_box_z(
        0,
        0,
        inner_w,
        inner_d,
        max(P.CRADLE_CORNER_R - 2, 2.0),
        floor,
        outer_h + 0.4,
    )

    # Open the front enough that the dials are not buried, but keep a lip.
    front_y = -inner_d / 2
    v.sub_box(
        -inner_w / 2 + P.FRONT_LIP,
        inner_w / 2 - P.FRONT_LIP,
        -outer_d / 2 - 1,
        front_y + 1.0,
        floor + 8,
        outer_h + 0.4,
    )

    # USB-C drop-in slot through the back wall, open to the top.
    back_inner = inner_d / 2
    v.sub_box(
        -P.USB_W / 2,
        P.USB_W / 2,
        back_inner - 1,
        outer_d / 2 + 1,
        floor + P.USB_Z_FROM_FLOOR,
        outer_h + 0.4,
    )

    # M3 stand-screw slots in the floor (elongated front-back).
    for sign in (-1, 1):
        cx = sign * P.M3_SPACING / 2
        cy = inner_d / 2 - P.M3_FROM_BACK
        v.sub_rounded_box_z(cx, cy, P.M3_HOLE, P.M3_SLOT_LEN, P.M3_HOLE / 2 - 0.05, -0.2, floor + 0.2)
        v.sub_rounded_box_z(
            cx, cy, P.M3_HEAD, P.M3_SLOT_LEN + 2.0, P.M3_HEAD / 2 - 0.1, -0.2, 2.2
        )

    # Zip-tie slots on both side walls.
    for sign in (-1, 1):
        v.sub_box(
            sign * (inner_w / 2 + wall / 2) - 1.6,
            sign * (inner_w / 2 + wall / 2) + 1.6,
            -6,
            6,
            floor + 6,
            floor + 12,
        )

    # Single hinge ear on the back, centred. Pivot axis = X, through the ear.
    back_outer = outer_d / 2
    pivot_y = back_outer + P.HINGE_STANDOFF
    pivot_z = floor + inner_h / 2
    ear_t = 11.2
    v.add_box(-ear_t / 2, ear_t / 2, back_outer - 2, pivot_y + P.HINGE_EAR_R, 2, outer_h)
    v.add_cyl_x(pivot_y, pivot_z, P.HINGE_EAR_R, -ear_t / 2, ear_t / 2)
    v.sub_cyl_x(pivot_y, pivot_z, P.HINGE_HOLE / 2, -ear_t / 2 - 0.2, ear_t / 2 + 0.2)

    return v


def build_clamp(pitch=0.25) -> Voxels:
    """
    U-channel for 40-series extrusion (6 Sigma 4040 / 4080 face).

    Extrusion runs along Y. U opens toward -X. Hinge ears on the +X back
    wall. Two M8 holes through the back wall into the T-slot.
    Print with the back wall on the bed (layers across the bolt bosses).
    """
    inner = P.EXT + P.EXT_CLEAR
    wall = P.CLAMP_WALL
    length = P.CLAMP_LEN
    lip = P.CLAMP_LIP

    # Inner channel: x 0..inner, z 0..inner, y -length/2..length/2
    back_x = inner + wall
    pivot_x = back_x + P.HINGE_STANDOFF
    pivot_z = inner / 2

    bounds = (
        -lip - 2,
        pivot_x + P.HINGE_EAR_R + 2,
        -length / 2 - P.HINGE_EAR_T - 4,
        length / 2 + P.HINGE_EAR_T + 4,
        -wall - 2,
        inner + wall + 2,
    )
    v = Voxels(bounds, pitch=pitch)

    # Back wall
    v.add_box(inner, back_x, -length / 2, length / 2, 0, inner)
    # Floor and ceiling of the U (wrap so it cannot spin on the 4040)
    v.add_box(0, back_x, -length / 2, length / 2, -wall, 0)
    v.add_box(0, back_x, -length / 2, length / 2, inner, inner + wall)
    # Short lips around the front face of the extrusion
    v.add_box(-lip, 0, -length / 2, length / 2, -wall, 0)
    v.add_box(-lip, 0, -length / 2, length / 2, inner, inner + wall)

    # M8 through the back wall, two bolts in one T-slot.
    for sign in (-1, 1):
        v.sub_cyl_x(sign * P.M8_SPACING / 2, inner / 2, P.M8_HOLE / 2, inner - 0.2, back_x + 0.2)
        # Screw-head pocket on the outside of the back wall.
        v.sub_cyl_x(sign * P.M8_SPACING / 2, inner / 2, 7.2, back_x - 1.6, back_x + 0.2)

    # Two hinge ears, gap in the middle for the cradle ear.
    gap = 12.2
    ear_t = P.HINGE_EAR_T
    for sign in (-1, 1):
        y0 = sign * (gap / 2)
        y1 = sign * (gap / 2 + ear_t)
        if y0 > y1:
            y0, y1 = y1, y0
        v.add_box(back_x - 1, pivot_x + 2, y0, y1, pivot_z - P.HINGE_EAR_R, pivot_z + P.HINGE_EAR_R)
        v.add_cyl_y(pivot_x, pivot_z, P.HINGE_EAR_R, y0, y1)
        v.sub_cyl_y(pivot_x, pivot_z, P.HINGE_HOLE / 2, y0 - 0.2, y1 + 0.2)

    return v


def write_template():
    """1:1 SVG you can print on A4 / Letter at 100% scale and lay on the Plus."""
    page_w, page_h = 210.0, 297.0
    ox, oy = page_w / 2, 70 + P.FACE_H / 2
    outer_w = P.FACE_W + P.PLATE_MARGIN * 2
    outer_h = P.FACE_H + P.PLATE_MARGIN * 2

    def sx(x):
        return ox + x

    def sy(y):
        return oy + y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_w}mm" height="{page_h}mm" viewBox="0 0 {page_w} {page_h}">',
        "<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#111} .dim{font-size:3.2px;fill:#333}</style>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<text x="12" y="14" font-size="5.5" font-weight="700">Stream Deck Plus faceplate — print at 100% scale</text>',
        f'<text x="12" y="21" font-size="3.4">Do not “fit to page”. Cut the outline, lay it on the Plus, and check every opening before you print plastic.</text>',
        f'<text x="12" y="27" class="dim">Face {P.FACE_W:.1f} × {P.FACE_H:.1f} mm  ·  key pitch {P.KEY_PITCH_X:.1f} × {P.KEY_PITCH_Y:.1f}  ·  dial Ø {P.DIAL_D:.1f}  ·  touch {P.TOUCH_W:.0f} × {P.TOUCH_H:.0f}</text>',
        f'<rect x="{sx(-outer_w/2):.3f}" y="{sy(-outer_h/2):.3f}" width="{outer_w:.3f}" height="{outer_h:.3f}" rx="{P.PLATE_R}" fill="none" stroke="#111" stroke-width="0.4"/>',
        f'<rect x="{sx(-P.FACE_W/2):.3f}" y="{sy(-P.FACE_H/2):.3f}" width="{P.FACE_W:.3f}" height="{P.FACE_H:.3f}" rx="{P.BODY_CORNER_R}" fill="none" stroke="#888" stroke-width="0.2" stroke-dasharray="2 1.2"/>',
    ]

    ks = P.KEY_SIZE + P.KEY_CLEAR
    for x in P.key_xs():
        for y in P.key_ys():
            parts.append(
                f'<rect x="{sx(x-ks/2):.3f}" y="{sy(y-ks/2):.3f}" width="{ks:.3f}" height="{ks:.3f}" rx="{P.KEY_CORNER_R}" fill="#e8e8e8" stroke="#111" stroke-width="0.25"/>'
            )

    tw = P.TOUCH_W + P.TOUCH_CLEAR * 2
    th = P.TOUCH_H + P.TOUCH_CLEAR * 2
    ty = P.touch_center_y()
    parts.append(
        f'<rect x="{sx(-tw/2):.3f}" y="{sy(ty-th/2):.3f}" width="{tw:.3f}" height="{th:.3f}" rx="1.2" fill="#d9d9d9" stroke="#111" stroke-width="0.25"/>'
    )

    dial_r = (P.DIAL_D + P.DIAL_CLEAR) / 2
    for x in P.dial_xs():
        parts.append(
            f'<circle cx="{sx(x):.3f}" cy="{sy(P.dial_center_y()):.3f}" r="{dial_r:.3f}" fill="#e8e8e8" stroke="#111" stroke-width="0.25"/>'
        )
        parts.append(
            f'<circle cx="{sx(x):.3f}" cy="{sy(P.dial_center_y()):.3f}" r="{P.DIAL_D/2:.3f}" fill="none" stroke="#888" stroke-width="0.2" stroke-dasharray="1 0.8"/>'
        )

    parts.append(
        f'<text x="{sx(0):.3f}" y="{sy(-P.FACE_H/2 - 4):.3f}" text-anchor="middle" class="dim">logo edge</text>'
    )
    parts.append(
        f'<text x="{sx(0):.3f}" y="{sy(P.FACE_H/2 + 6):.3f}" text-anchor="middle" class="dim">dial edge</text>'
    )
    parts.append("</svg>")
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    path = TEMPLATE_DIR / "faceplate-1to1.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"  wrote {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--part",
        choices=["all", "faceplate", "cradle", "clamp", "gauge", "template"],
        default="all",
    )
    args = parser.parse_args()
    STL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Face {P.FACE_W:.1f} x {P.FACE_H:.1f} mm  (derived from bezel stack)")
    print(f"Key pitch {P.KEY_PITCH_X} x {P.KEY_PITCH_Y}  dial pitch {P.DIAL_PITCH}")

    if args.part in ("all", "template"):
        write_template()
    if args.part in ("all", "gauge"):
        export(build_fit_gauge(), STL_DIR / "fit_gauge.stl", "fit_gauge")
    if args.part in ("all", "faceplate"):
        export(build_faceplate(), STL_DIR / "faceplate.stl", "faceplate")
    if args.part in ("all", "cradle"):
        export(build_cradle(), STL_DIR / "cradle.stl", "cradle")
    if args.part in ("all", "clamp"):
        export(build_clamp(), STL_DIR / "clamp_4040.stl", "clamp_4040")


if __name__ == "__main__":
    main()
