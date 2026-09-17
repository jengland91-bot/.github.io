#!/usr/bin/env python3
"""Write a low-poly desert mile-marker OBJ + MTL (no Blender required)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "export"


def write_obj() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Units: meters. Origin at ground center under post.
    # Post: 0.10 x 0.10 x 1.45, bottom at z=0
    # Sign: 0.42 x 0.03 x 0.28, face near top
    # Cap: small pyramid-ish bevel on post top (box is fine)

    verts: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    faces: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int], str]] = []

    def add_box(x0, y0, z0, x1, y1, z1, mat: str, uv_mode: str = "box") -> None:
        """Axis-aligned box. Face winding outward for +Z up."""
        base = len(verts)
        corners = [
            (x0, y0, z0),
            (x1, y0, z0),
            (x1, y1, z0),
            (x0, y1, z0),
            (x0, y0, z1),
            (x1, y0, z1),
            (x1, y1, z1),
            (x0, y1, z1),
        ]
        verts.extend(corners)

        # UV helpers
        def uv(u, v):
            uvs.append((u, v))
            return len(uvs)

        # each face: 4 verts indices (1-based later), with uvs
        face_defs = [
            # bottom -z
            ([0, 3, 2, 1], [(0, 0), (1, 0), (1, 1), (0, 1)]),
            # top +z
            ([4, 5, 6, 7], [(0, 0), (1, 0), (1, 1), (0, 1)]),
            # -y front (sign faces -Y mostly)
            ([0, 1, 5, 4], [(0, 0), (1, 0), (1, 1), (0, 1)]),
            # +y back
            ([2, 3, 7, 6], [(0, 0), (1, 0), (1, 1), (0, 1)]),
            # +x
            ([1, 2, 6, 5], [(0, 0), (1, 0), (1, 1), (0, 1)]),
            # -x
            ([3, 0, 4, 7], [(0, 0), (1, 0), (1, 1), (0, 1)]),
        ]

        # For the sign front face, stretch UV across full texture
        for fi, (idxs, uv_coords) in enumerate(face_defs):
            if mat == "sign" and fi == 2:
                # front face full plate UV
                uv_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
            elif mat == "wood" and fi in (2, 3, 4, 5):
                # vertical grain
                uv_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

            uv_ids = [uv(u, v) for u, v in uv_coords]
            faces.append(
                (
                    (base + idxs[0] + 1, uv_ids[0]),
                    (base + idxs[1] + 1, uv_ids[1]),
                    (base + idxs[2] + 1, uv_ids[2]),
                    (base + idxs[3] + 1, uv_ids[3]),
                    mat,
                )
            )

    # Post
    pw = 0.05  # half-width 5cm -> 10cm post
    post_h = 1.45
    add_box(-pw, -pw, 0.0, pw, pw, post_h, "wood")

    # Slight metal band under sign
    add_box(-0.055, -0.055, 1.05, 0.055, 0.055, 1.09, "metal")

    # Sign plate (facing -Y, slightly in front)
    sx0, sx1 = -0.21, 0.21
    sy0, sy1 = -0.085, -0.055  # thickness ~3cm, in front of post
    sz0, sz1 = 1.10, 1.38
    add_box(sx0, sy0, sz0, sx1, sy1, sz1, "sign")

    # Thin backer plate
    add_box(-0.20, -0.055, 1.11, 0.20, -0.045, 1.37, "metal")

    mtl_path = OUT / "milemarker_01.mtl"
    mtl_path.write_text(
        "\n".join(
            [
                "newmtl wood",
                "Ka 1.000 1.000 1.000",
                "Kd 0.45 0.30 0.18",
                "Ks 0.05 0.05 0.05",
                "Ns 8.0",
                "map_Kd ../textures/post_wood.png",
                "",
                "newmtl metal",
                "Ka 1.000 1.000 1.000",
                "Kd 0.55 0.57 0.60",
                "Ks 0.25 0.25 0.25",
                "Ns 40.0",
                "map_Kd ../textures/sign_metal.png",
                "",
                "newmtl sign",
                "Ka 1.000 1.000 1.000",
                "Kd 0.95 0.93 0.88",
                "Ks 0.15 0.15 0.15",
                "Ns 25.0",
                "map_Kd ../textures/mile_01.png",
                "",
            ]
        ),
        encoding="utf-8",
    )

    lines = [
        "# Parker 400 style mile marker",
        "# Units: meters, Z-up, origin at ground",
        "mtllib milemarker_01.mtl",
        "o milemarker_01",
    ]
    for v in verts:
        lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
    for uv in uvs:
        lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")

    current = None
    for f in faces:
        mat = f[4]
        if mat != current:
            lines.append(f"usemtl {mat}")
            current = mat
        a, b, c, d = f[0], f[1], f[2], f[3]
        lines.append(
            f"f {a[0]}/{a[1]} {b[0]}/{b[1]} {c[0]}/{c[1]} {d[0]}/{d[1]}"
        )

    obj_path = OUT / "milemarker_01.obj"
    obj_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {obj_path}")
    print(f"wrote {mtl_path}")


if __name__ == "__main__":
    write_obj()
