#!/usr/bin/env python3
"""
Original Open-Shoulder Bucket Phone Cradle — mesh generator
===========================================================
Creates print-ready binary STLs without OpenSCAD.

Design intent
-------------
- Open-shoulder racing-bucket silhouette (EVO III *style cue*: no tall
  head wings), original geometry — not a remix of MakerWorld / Thingiverse /
  Recaro / Sparco models.
- Phone pocket + charge notch.
- Dovetail mount on the back.
- Separate 40 mm tube clamp (Evolve-style tubular frames).
- Optional 4040 adapter plate.

Trademark note: do not sell under Sparco / Recaro brand names.
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent / "stl"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Mesh utilities
# ---------------------------------------------------------------------------

class Mesh:
    def __init__(self):
        self.tris: list[np.ndarray] = []

    def add_tri(self, a, b, c):
        self.tris.append(np.array([a, b, c], dtype=np.float64))

    def add_quad(self, a, b, c, d):
        self.add_tri(a, b, c)
        self.add_tri(a, c, d)

    def extend(self, other: "Mesh"):
        self.tris.extend(other.tris)

    def transform(self, matrix_3x3=None, translate=(0, 0, 0)):
        t = np.asarray(translate, dtype=np.float64)
        m = np.asarray(matrix_3x3, dtype=np.float64) if matrix_3x3 is not None else None
        out = Mesh()
        for tri in self.tris:
            pts = tri.copy()
            if m is not None:
                pts = pts @ m.T
            pts += t
            out.tris.append(pts)
        return out

    def translate(self, x, y, z):
        return self.transform(translate=(x, y, z))

    def rotate_x(self, deg):
        r = math.radians(deg)
        c, s = math.cos(r), math.sin(r)
        m = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        return self.transform(m)

    def rotate_z(self, deg):
        r = math.radians(deg)
        c, s = math.cos(r), math.sin(r)
        m = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        return self.transform(m)

    def write_stl(self, path: Path, name: str = "part"):
        path = Path(path)
        # Weld near-duplicates for cleaner normals
        verts = []
        faces = []
        key_map = {}

        def key(p):
            return (round(float(p[0]), 4), round(float(p[1]), 4), round(float(p[2]), 4))

        for tri in self.tris:
            ids = []
            for p in tri:
                k = key(p)
                if k not in key_map:
                    key_map[k] = len(verts)
                    verts.append(np.array(k, dtype=np.float64))
                ids.append(key_map[k])
            # skip degenerate
            a, b, c = verts[ids[0]], verts[ids[1]], verts[ids[2]]
            if np.linalg.norm(np.cross(b - a, c - a)) < 1e-8:
                continue
            faces.append(ids)

        with open(path, "wb") as f:
            header = name.encode("ascii", "ignore")[:80].ljust(80, b"\0")
            f.write(header)
            f.write(struct.pack("<I", len(faces)))
            for i0, i1, i2 in faces:
                a, b, c = verts[i0], verts[i1], verts[i2]
                n = np.cross(b - a, c - a)
                ln = np.linalg.norm(n)
                if ln > 0:
                    n = n / ln
                else:
                    n = np.array([0.0, 0.0, 1.0])
                f.write(struct.pack("<3f", *n))
                f.write(struct.pack("<3f", *a))
                f.write(struct.pack("<3f", *b))
                f.write(struct.pack("<3f", *c))
                f.write(struct.pack("<H", 0))
        print(f"Wrote {path} ({len(faces)} triangles)")


def box(sx, sy, sz, center=False) -> Mesh:
    m = Mesh()
    x0, y0, z0 = (0, 0, 0)
    if center:
        x0, y0, z0 = -sx / 2, -sy / 2, -sz / 2
    x1, y1, z1 = x0 + sx, y0 + sy, z0 + sz
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    faces = [
        (0, 1, 2, 3),  # bottom
        (4, 7, 6, 5),  # top
        (0, 4, 5, 1),  # front
        (1, 5, 6, 2),  # right
        (2, 6, 7, 3),  # back
        (3, 7, 4, 0),  # left
    ]
    for a, b, c, d in faces:
        m.add_quad(v[a], v[b], v[c], v[d])
    return m


def cylinder(r, h, segments=48, center=False) -> Mesh:
    m = Mesh()
    z0 = -h / 2 if center else 0
    z1 = z0 + h
    bottom = []
    top = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        x, y = r * math.cos(a), r * math.sin(a)
        bottom.append((x, y, z0))
        top.append((x, y, z1))
    c_bot = (0, 0, z0)
    c_top = (0, 0, z1)
    for i in range(segments):
        j = (i + 1) % segments
        m.add_tri(c_bot, bottom[j], bottom[i])
        m.add_tri(c_top, top[i], top[j])
        m.add_quad(bottom[i], bottom[j], top[j], top[i])
    return m


def hex_prism(af, h, center=False) -> Mesh:
    """af = across-flats."""
    r = af / math.sqrt(3)
    return cylinder(r, h, segments=6, center=center)


def loft_rings(rings: list[list[tuple]], close_caps=True) -> Mesh:
    """Loft stacked rings (each ring same vertex count) into a solid."""
    m = Mesh()
    n = len(rings[0])
    for ri in range(len(rings) - 1):
        a = rings[ri]
        b = rings[ri + 1]
        for i in range(n):
            j = (i + 1) % n
            m.add_quad(a[i], a[j], b[j], b[i])
    if close_caps and len(rings) >= 2:
        # bottom fan
        c0 = np.mean(np.array(rings[0]), axis=0)
        for i in range(n):
            j = (i + 1) % n
            m.add_tri(c0, rings[0][j], rings[0][i])
        # top fan
        c1 = np.mean(np.array(rings[-1]), axis=0)
        for i in range(n):
            j = (i + 1) % n
            m.add_tri(c1, rings[-1][i], rings[-1][j])
    return m


def ellipse_ring(cx, cy, cz, rx, ry, n=32, z_tilt=0.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = cx + rx * math.cos(a)
        y = cy + ry * math.sin(a)
        z = cz + z_tilt * math.sin(a)  # unused usually
        pts.append((x, y, z))
    return pts


# ---------------------------------------------------------------------------
# Seat cradle — open-shoulder bucket
# ---------------------------------------------------------------------------

def make_seat_cradle(
    phone_w=88.0,
    phone_t=16.0,
    recline_deg=12.0,
) -> Mesh:
    """
    Build a hollowable solid by lofting outer shell, then carving the phone
    pocket as an open trough (constructed, not boolean-subtracted).
    """
    n = 28
    # Cross-section profile heights along seat "spine" (mm)
    # EVO-III cue: shoulders stay open — upper width does NOT flare into head wings
    sections = [
        # z, half_width, depth_front, depth_back, y_center
        (0.0, 34.0, 36.0, 8.0, 28.0),    # pan front
        (8.0, 36.0, 30.0, 14.0, 24.0),   # pan mid
        (18.0, 35.0, 10.0, 22.0, 14.0),  # bolster transition
        (40.0, 32.0, 4.0, 20.0, 8.0),    # lower back
        (70.0, 28.0, 2.0, 16.0, 4.0),    # mid back (open shoulder)
        (95.0, 22.0, 1.0, 12.0, 1.0),    # upper back
        (112.0, 16.0, 0.5, 9.0, -1.0),   # crown — low, no wings
    ]

    outer_rings = []
    for z, hw, df, db, yc in sections:
        # Rounded rectangle-ish ring: front arc + back arc
        ring = []
        # Parametric oval centered at (0, yc)
        rx = hw
        ry = (df + db) / 2
        # shift so front/back depths match
        y_off = yc + (db - df) / 2
        for i in range(n):
            a = 2 * math.pi * i / n
            # flatten sides slightly for bolsters (faceted premium look)
            squash = 0.92 + 0.08 * abs(math.cos(a))
            x = rx * math.cos(a) * squash
            y = y_off + ry * math.sin(a)
            ring.append((x, y, z))
        outer_rings.append(ring)

    shell = loft_rings(outer_rings, close_caps=True)

    # Apply recline around X through seat base
    shell = shell.rotate_x(-recline_deg)

    # --- Phone trough walls (built as solid rails + floor, open top) ---
    # Pocket sits in the backrest region
    pocket = Mesh()
    pw, pt, ph = phone_w, phone_t, 58.0
    wall = 3.0
    # Floor under phone
    floor = box(pw + 2 * wall, pt + wall, 3.0, center=True)
    floor = floor.translate(0, 18, 22)
    # Left / right rails
    rail_l = box(wall, pt + wall, ph, center=True).translate(-(pw / 2 + wall / 2), 18, 22 + ph / 2)
    rail_r = box(wall, pt + wall, ph, center=True).translate(+(pw / 2 + wall / 2), 18, 22 + ph / 2)
    # Back plate
    back = box(pw + 2 * wall, wall, ph, center=True).translate(0, 18 - (pt / 2 + wall / 2), 22 + ph / 2)
    # Front lip (retains phone)
    lip = box(pw + 2 * wall, wall, 9.0, center=True).translate(0, 18 + (pt / 2 + wall / 2), 22 + 4.5)
    # Charge notch cut = simply leave a gap in the lip center via two lip halves
    lip_l = box((pw / 2 - 5), wall, 9.0, center=True).translate(-(pw / 4 + 2.5), 18 + (pt / 2 + wall / 2), 22 + 4.5)
    lip_r = box((pw / 2 - 5), wall, 9.0, center=True).translate(+(pw / 4 + 2.5), 18 + (pt / 2 + wall / 2), 22 + 4.5)

    for part in (floor, rail_l, rail_r, back, lip_l, lip_r):
        pocket.extend(part.rotate_x(-recline_deg))

    # Decorative harness slot frames (raised bezels — original detail)
    slots = Mesh()
    for sx in (-16, 16):
        bezel = box(8, 2.5, 14, center=True).translate(sx, 2, 78)
        slots.extend(bezel.rotate_x(-recline_deg))
    for sx in (-18, 18):
        bezel = box(10, 8, 2.5, center=True).translate(sx, 22, 12)
        slots.extend(bezel)
    crotch = box(8, 10, 2.5, center=True).translate(0, 30, 8)
    slots.extend(crotch)

    # Dovetail male on back
    dovetail = make_dovetail_male(22, 10, 28).translate(0, -6, 48)

    out = Mesh()
    out.extend(shell)
    out.extend(pocket)
    out.extend(slots)
    out.extend(dovetail)

    # Sit flat on print bed: shift so min Z = 0, center XY
    all_pts = np.vstack(out.tris)
    mn = all_pts.min(axis=0)
    mx = all_pts.max(axis=0)
    mid = (mn + mx) / 2
    out = out.translate(-mid[0], -mid[1], -mn[2])
    return out


def make_dovetail_male(w, h, length) -> Mesh:
    """Trapezoid prism along Y."""
    m = Mesh()
    # Cross section: bottom narrow, top wide (or reverse for dovetail)
    # Male: wide at tip so it locks into female
    half_len = length / 2
    # profile at z=0 (narrow) and z=h (wide)
    # Extrude along Y
    # Bottom face (narrow) y from -hl to +hl
    n0, n1 = 2.0, w - 2.0  # narrow inset
    w0, w1 = 0.0, w
    # 8 corners of trapezoidal prism
    # y=-hl and y=+hl
    def ring(y):
        return [
            (-n0 + w / 2 - w / 2, y, 0),  # simplify below
        ]

    # Explicit corners:
    # z=0 (insert face, narrower): x from 2 to w-2
    # z=h (base, full width): x from 0 to w
    corners_neg = [
        (2, -half_len, 0),
        (w - 2, -half_len, 0),
        (w, -half_len, h),
        (0, -half_len, h),
    ]
    corners_pos = [
        (2, half_len, 0),
        (w - 2, half_len, 0),
        (w, half_len, h),
        (0, half_len, h),
    ]
    # center on X
    shift = -w / 2
    corners_neg = [(x + shift, y, z) for x, y, z in corners_neg]
    corners_pos = [(x + shift, y, z) for x, y, z in corners_pos]

    # end caps
    m.add_quad(corners_neg[0], corners_neg[1], corners_neg[2], corners_neg[3])
    m.add_quad(corners_pos[0], corners_pos[3], corners_pos[2], corners_pos[1])
    # sides
    for i in range(4):
        j = (i + 1) % 4
        m.add_quad(corners_neg[i], corners_pos[i], corners_pos[j], corners_neg[j])
    return m


def make_dovetail_female_block(w=22.4, h=10.4, length=28.4, shell=4.0) -> Mesh:
    """Solid block with trapezoid tunnel — approximate by outer box minus
    leaving a channel as open U (print-friendly slide-in from +Z)."""
    m = Mesh()
    bw, bh, bl = w + 2 * shell, h + shell + 2, length + 2
    # Outer
    outer = box(bw, bh, bl, center=True)
    # We can't boolean easily; build as walls
    walls = Mesh()
    # floor
    walls.extend(box(bw, 2, bl, center=True).translate(0, -bh / 2 + 1, 0))
    # left wall
    walls.extend(box(shell, bh, bl, center=True).translate(-bw / 2 + shell / 2, 0, 0))
    # right wall
    walls.extend(box(shell, bh, bl, center=True).translate(+bw / 2 - shell / 2, 0, 0))
    # back stop (partial)
    walls.extend(box(bw, bh, 2, center=True).translate(0, 0, -bl / 2 + 1))
    # angled rails approximated with stepped ledges
    ledge = box(w * 0.15, 2, bl - 2, center=True)
    walls.extend(ledge.translate(-w / 2 + 2, -bh / 2 + 3, 0))
    walls.extend(ledge.translate(+w / 2 - 2, -bh / 2 + 3, 0))
    return walls


# ---------------------------------------------------------------------------
# 40 mm tube clamp
# ---------------------------------------------------------------------------

def make_clamp_half(front=True, tube_od=40.4, width=28.0, wall=4.5) -> Mesh:
    m = Mesh()
    r_outer = tube_od / 2 + wall
    r_inner = tube_od / 2
    segments = 48
    ear = r_outer + 12

    # Build as annular sector (180 deg) with bolt ears
    # Outer half-cylinder shell
    z0, z1 = 0.0, width
    # Half ring points for outer and inner
    def arc(r, a0, a1, n):
        pts = []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            pts.append((r * math.cos(a), r * math.sin(a)))
        return pts

    # Front half: +Y (0 to 180 deg in math coords where 0=+X)
    # Use a0=-10deg to a1=190deg with flats at split for clamping gap
    if front:
        a0, a1 = math.radians(-5), math.radians(185)
    else:
        a0, a1 = math.radians(175), math.radians(365)

    n = 32
    outer = arc(r_outer, a0, a1, n)
    inner = arc(r_inner, a0, a1, n)

    # Side walls of half-pipe
    for i in range(n):
        o0, o1 = outer[i], outer[i + 1]
        i0, i1 = inner[i], inner[i + 1]
        # outer wall
        m.add_quad((o0[0], o0[1], z0), (o1[0], o1[1], z0), (o1[0], o1[1], z1), (o0[0], o0[1], z1))
        # inner wall (reversed winding)
        m.add_quad((i0[0], i0[1], z0), (i0[0], i0[1], z1), (i1[0], i1[1], z1), (i1[0], i1[1], z0))
        # bottom rim
        m.add_quad((o0[0], o0[1], z0), (i0[0], i0[1], z0), (i1[0], i1[1], z0), (o1[0], o1[1], z0))
        # top rim
        m.add_quad((o0[0], o0[1], z1), (o1[0], o1[1], z1), (i1[0], i1[1], z1), (i0[0], i0[1], z1))

    # Close split faces
    for end in (0, -1):
        o = outer[end]
        i = inner[end]
        m.add_quad((o[0], o[1], z0), (o[0], o[1], z1), (i[0], i[1], z1), (i[0], i[1], z0))

    # Bolt ears
    for side in (-1, 1):
        ex = side * ear
        ear_box = box(14, wall + 2, width, center=True).translate(ex, 0 if front else 0, width / 2)
        # shift ear to sit on split plane
        if front:
            ear_box = box(14, wall + 1, width, center=True).translate(ex, wall / 2, width / 2)
        else:
            ear_box = box(14, wall + 1, width, center=True).translate(ex, -wall / 2, width / 2)
        m.extend(ear_box)
        # Bolt hole as empty — approximate by not filling; add thin cylinder cutout
        # For printable prototype without boolean: leave a small through-marker cylinder
        # Better: add hole by ring of triangles (tube through ear)
        hole = cylinder(2.65, wall + 4, segments=24, center=True)
        # We can't subtract; instead leave note for drilling OR build ear as C-shape
        # Build ear with hole using annular construction
        pass

    # Rebuild ears with proper holes
    m2 = Mesh()
    # copy pipe part only — rebuild ears properly
    # Actually reconstruct ears:
    ears = Mesh()
    for side in (-1, 1):
        ex = side * (r_outer + 7)
        ey = (wall / 2 + 0.5) if front else -(wall / 2 + 0.5)
        # Annular ear (plate with hole)
        ear_mesh = plate_with_hole(14, width, wall + 1, hole_r=2.65, segments=24)
        # plate_with_hole is in XY; rotate to XZ and place
        ear_mesh = ear_mesh.rotate_x(90).translate(ex, ey, width / 2)
        ears.extend(ear_mesh)
        if not front:
            # nut trap hex recess on outer face
            trap = hex_prism(8.2, 2.2, center=True).translate(ex, ey - (wall / 2 + 0.2), width / 2)
            # Can't subtract — add a note in docs to drill; for now skip trap mesh
            _ = trap

    m.extend(ears)

    if front:
        # Dovetail receiver block on +Y
        recv = make_dovetail_female_block()
        recv = recv.translate(0, r_outer + 8, width / 2)
        m.extend(recv)

    # Orient flat for printing: lay split face on bed
    if front:
        m = m.rotate_x(90)  # split toward bed roughly
    else:
        m = m.rotate_x(-90)

    all_pts = np.vstack(m.tris)
    mn = all_pts.min(axis=0)
    mid = (all_pts.min(axis=0) + all_pts.max(axis=0)) / 2
    m = m.translate(-mid[0], -mid[1], -mn[2])
    return m


def plate_with_hole(sx, sy, sz, hole_r, segments=32) -> Mesh:
    """Rectangular plate centered at origin with cylindrical hole along Z."""
    m = Mesh()
    # Outer rectangle corners
    hx, hy = sx / 2, sy / 2
    # Use triangle fan from hole to outer for top/bottom + walls
    # Outer path
    outer = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    # For simplicity: solid box then... without boolean, build as
    # 4 corner blocks around hole if hole is centered and smaller
    # Better approach: extrude polygon with hole via triangles

    z0, z1 = -sz / 2, sz / 2
    # Top face: ring from hole to a surrounding octagon-rect hybrid
    # Map each outer edge to hole arcs
    # Create outer boundary as denser points along rectangle
    def rect_boundary(n_per_side=8):
        pts = []
        # bottom edge
        for i in range(n_per_side):
            t = i / n_per_side
            pts.append((-hx + sx * t, -hy))
        for i in range(n_per_side):
            t = i / n_per_side
            pts.append((hx, -hy + sy * t))
        for i in range(n_per_side):
            t = i / n_per_side
            pts.append((hx - sx * t, hy))
        for i in range(n_per_side):
            t = i / n_per_side
            pts.append((-hx, hy - sy * t))
        return pts

    outer_pts = rect_boundary(10)
    n = len(outer_pts)
    inner_pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        # match winding
        a = 2 * math.pi * i / n
        inner_pts.append((hole_r * math.cos(a), hole_r * math.sin(a)))

    # Re-parameterize inner by angle of outer for better quads
    inner_pts = []
    for x, y in outer_pts:
        a = math.atan2(y, x)
        inner_pts.append((hole_r * math.cos(a), hole_r * math.sin(a)))

    for i in range(n):
        j = (i + 1) % n
        o0, o1 = outer_pts[i], outer_pts[j]
        i0, i1 = inner_pts[i], inner_pts[j]
        # top
        m.add_quad((o0[0], o0[1], z1), (o1[0], o1[1], z1), (i1[0], i1[1], z1), (i0[0], i0[1], z1))
        # bottom
        m.add_quad((o0[0], o0[1], z0), (i0[0], i0[1], z0), (i1[0], i1[1], z0), (o1[0], o1[1], z0))
        # outer wall
        m.add_quad((o0[0], o0[1], z0), (o1[0], o1[1], z0), (o1[0], o1[1], z1), (o0[0], o0[1], z1))
        # hole wall
        m.add_quad((i0[0], i0[1], z0), (i0[0], i0[1], z1), (i1[0], i1[1], z1), (i1[0], i1[1], z0))
    return m


def make_adapter_4040() -> Mesh:
    m = Mesh()
    plate = plate_with_hole(40, 40, 6, hole_r=4.15, segments=36)
    # Stand plate in XZ with face on Y=0
    plate = plate.rotate_x(90).translate(0, 3, 20)
    recv = make_dovetail_female_block()
    recv = recv.translate(0, 12, 20)
    m.extend(plate)
    m.extend(recv)
    all_pts = np.vstack(m.tris)
    mn = all_pts.min(axis=0)
    mid = (all_pts.min(axis=0) + all_pts.max(axis=0)) / 2
    return m.translate(-mid[0], -mid[1], -mn[2])


def make_desk_stand_base() -> Mesh:
    """Optional weighted-look desk base with dovetail — sell as desk variant."""
    m = Mesh()
    base = box(90, 70, 8, center=True).translate(0, 0, 4)
    # subtle foot pads
    for x, y in [(-35, -25), (35, -25), (-35, 25), (35, 25)]:
        pad = cylinder(6, 2, segments=24).translate(x, y, 0)
        m.extend(pad)
    m.extend(base)
    # upright post
    post = box(18, 10, 50, center=True).translate(0, -20, 8 + 25)
    m.extend(post)
    recv = make_dovetail_female_block()
    recv = recv.rotate_x(12).translate(0, -14, 55)
    m.extend(recv)
    all_pts = np.vstack(m.tris)
    mn = all_pts.min(axis=0)
    mid = (all_pts.min(axis=0) + all_pts.max(axis=0)) / 2
    return m.translate(-mid[0], -mid[1], -mn[2])


def main():
    seat = make_seat_cradle()
    seat.write_stl(OUT / "seat_cradle.stl", "seat_cradle")

    clamp_f = make_clamp_half(front=True)
    clamp_f.write_stl(OUT / "clamp_40mm_front.stl", "clamp_40mm_front")

    clamp_r = make_clamp_half(front=False)
    clamp_r.write_stl(OUT / "clamp_40mm_rear.stl", "clamp_40mm_rear")

    adapter = make_adapter_4040()
    adapter.write_stl(OUT / "adapter_4040.stl", "adapter_4040")

    desk = make_desk_stand_base()
    desk.write_stl(OUT / "desk_stand_base.stl", "desk_stand_base")

    # Manifest sizes
    for p in sorted(OUT.glob("*.stl")):
        print(f"  {p.name}: {p.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
