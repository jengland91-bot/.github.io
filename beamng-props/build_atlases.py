#!/usr/bin/env python3
"""
Build texture atlases + ORM channel-packed maps for Parker 400 props.

Outputs (under beamng-props/atlases/):
  sign_atlas_2048.png      — mile markers, course arrows, danger, laps, exits, wood/metal
  sign_atlas_layout.json   — UV rects (Blender bottom-left V)
  sign_orm_2048.png        — R=AO G=Roughness B=Metallic
  vegetation_atlas_2048.png — rocks + desert flora tiles (creosote, saguaro, sand, bush)
  vegetation_atlas_layout.json
  vegetation_orm_2048.png

No external deps (pure Python PNG via _shared/pngutil.py).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "_shared"))
from pngutil import blit, load_rgba, resize_box, save_rgba, solid  # noqa: E402

OUT = ROOT / "atlases"
SIZE = 2048


def uv_rect(px: int, py: int, pw: int, ph: int, atlas: int = SIZE):
    """Pixel rect (top-left origin) → Blender UVs (V=0 at bottom)."""
    u0 = px / atlas
    u1 = (px + pw) / atlas
    v1 = 1.0 - (py / atlas)
    v0 = 1.0 - ((py + ph) / atlas)
    return {
        "px": px,
        "py": py,
        "pw": pw,
        "ph": ph,
        "u0": round(u0, 6),
        "v0": round(v0, 6),
        "u1": round(u1, 6),
        "v1": round(v1, 6),
    }


def place(
    atlas,
    layout: dict,
    key: str,
    path: Path,
    px: int,
    py: int,
    cell_w: int,
    cell_h: int,
    orm,
    ao: int,
    rough: int,
    metal: int,
):
    if not path.exists():
        print(f"  skip missing {path}")
        return False
    sw, sh, src = load_rgba(path)
    # Fit into cell preserving aspect (letterbox on dark)
    scale = min(cell_w / sw, cell_h / sh)
    tw, th = max(1, int(sw * scale)), max(1, int(sh * scale))
    resized = resize_box(sw, sh, src, tw, th)
    ox = px + (cell_w - tw) // 2
    oy = py + (cell_h - th) // 2
    blit(SIZE, atlas, tw, th, resized, ox, oy)
    # ORM fill for this cell
    for y in range(cell_h):
        for x in range(cell_w):
            # soft AO vignette toward cell edge
            edge = min(x, y, cell_w - 1 - x, cell_h - 1 - y)
            vig = max(0, 40 - edge * 2) if edge < 20 else 0
            a = max(0, min(255, ao - vig))
            orm[(py + y) * SIZE + (px + x)] = (a, rough, metal, 255)
    layout[key] = uv_rect(px, py, cell_w, cell_h)
    print(f"  + {key} @ {px},{py} {cell_w}x{cell_h}")
    return True


def procedural_tile(w, h, kind: str):
    """Generate desert flora / ground tiles. Leaf kinds use real alpha cutouts."""
    px = []
    for y in range(h):
        for x in range(w):
            n1 = ((x * 13) ^ (y * 7)) % 17
            n2 = ((x * 3 + y * 5) % 23) - 11
            if kind == "creosote_bark":
                v = 70 + n1 + (x % 6) * 2
                r, g, b, a = v + 15, v - 5, v - 20, 255
            elif kind == "creosote_leaf":
                # Opaque leaf clusters only — transparent elsewhere (cuts overdraw)
                r, g, b, a = _foliage_alpha_pixel(x, y, w, h, "creosote", n1, n2)
            elif kind == "saguaro_skin":
                r, g, b, a = 70 + n1, 95 + n1, 55 + n1 // 2, 255
            elif kind == "saguaro_rib":
                stripe = 20 if (x % 32) < 6 else 0
                r, g, b, a = 55 + n1 + stripe, 80 + n1 + stripe, 45 + n1, 255
            elif kind == "dry_bush":
                r, g, b, a = _foliage_alpha_pixel(x, y, w, h, "scrub", n1, n2)
            elif kind == "sand_ground":
                r, g, b, a = 180 + n1 // 2, 150 + n1 // 2, 105 + n2 // 2, 255
            elif kind == "ocotillo_stem":
                r, g, b, a = 90 + n1, 55 + n1 // 2, 35, 255
            else:
                r, g, b, a = 128, 128, 128, 255
            px.append(
                (
                    max(0, min(255, int(r))),
                    max(0, min(255, int(g))),
                    max(0, min(255, int(b))),
                    max(0, min(255, int(a))),
                )
            )
    return px


def _foliage_alpha_pixel(x, y, w, h, style: str, n1: int, n2: int):
    """
    Paint several leaf blobs; everything else alpha=0.
    Keeps opaque coverage tight so silhouette meshes waste less transparent fill.
    """
    nx = (x + 0.5) / w
    ny = (y + 0.5) / h
    # Seeded blob centers (normalized)
    if style == "creosote":
        blobs = [
            (0.50, 0.55, 0.22, 0.28),
            (0.32, 0.40, 0.14, 0.18),
            (0.68, 0.42, 0.13, 0.17),
            (0.45, 0.28, 0.12, 0.14),
            (0.58, 0.70, 0.11, 0.13),
        ]
        base = (55 + n1, 70 + n1 + n2 // 2, 35 + n1 // 2)
    else:  # scrub / dry bush
        blobs = [
            (0.50, 0.50, 0.26, 0.24),
            (0.30, 0.55, 0.12, 0.14),
            (0.70, 0.48, 0.12, 0.13),
            (0.48, 0.32, 0.10, 0.12),
        ]
        base = (95 + n1, 85 + n1 // 2, 45 + n2)

    covered = False
    for cx, cy, rx, ry in blobs:
        dx = (nx - cx) / rx
        dy = (ny - cy) / ry
        # Slightly irregular ellipse
        jag = 0.08 * math.sin((nx + ny) * 40 + n1)
        if dx * dx + dy * dy < 1.0 + jag:
            covered = True
            break
    if not covered:
        return (0, 0, 0, 0)
    r, g, b = base
    # Edge darken within blob for AO-ish read
    return (r, g, b, 255)


def place_generated(
    atlas,
    layout,
    key,
    pixels,
    tw,
    th,
    px,
    py,
    cell_w,
    cell_h,
    orm,
    ao,
    rough,
    metal,
):
    resized = resize_box(tw, th, pixels, cell_w, cell_h) if (tw, th) != (cell_w, cell_h) else pixels
    blit(SIZE, atlas, cell_w, cell_h, resized, px, py)
    for y in range(cell_h):
        for x in range(cell_w):
            edge = min(x, y, cell_w - 1 - x, cell_h - 1 - y)
            vig = max(0, 30 - edge) if edge < 16 else 0
            orm[(py + y) * SIZE + (px + x)] = (max(0, ao - vig), rough, metal, 255)
    layout[key] = uv_rect(px, py, cell_w, cell_h)
    print(f"  + {key} (generated) @ {px},{py}")


def build_sign_atlas():
    print("=== Sign atlas 2048 ===")
    atlas = solid(SIZE, SIZE, (18, 18, 18, 255))
    orm = solid(SIZE, SIZE, (220, 180, 20, 255))  # default mid AO, mid rough, low metal
    layout = {"atlas": "sign_atlas_2048.png", "orm": "sign_orm_2048.png", "size": SIZE, "rects": {}}

    # --- Trim strip: wood + metal (256 cells) ---
    place(
        atlas,
        layout["rects"],
        "post_wood",
        ROOT / "mile-marker/textures/post_wood.png",
        0,
        0,
        256,
        256,
        orm,
        ao=200,
        rough=220,
        metal=15,
    )
    place(
        atlas,
        layout["rects"],
        "sign_metal",
        ROOT / "mile-marker/textures/sign_metal.png",
        256,
        0,
        256,
        256,
        orm,
        ao=210,
        rough=110,
        metal=180,
    )

    # --- Course signs 256×256 starting x=512 ---
    course = [
        ("arrow_straight", "course-signs/textures/arrow_straight.png"),
        ("arrow_slight_left", "course-signs/textures/arrow_slight_left.png"),
        ("arrow_slight_right", "course-signs/textures/arrow_slight_right.png"),
        ("arrow_turn_left", "course-signs/textures/arrow_turn_left.png"),
        ("arrow_turn_right", "course-signs/textures/arrow_turn_right.png"),
        ("arrow_double_left", "course-signs/textures/arrow_double_left.png"),
        ("arrow_double_right", "course-signs/textures/arrow_double_right.png"),
        ("arrow_triple_left", "course-signs/textures/arrow_triple_left.png"),
        ("arrow_triple_right", "course-signs/textures/arrow_triple_right.png"),
        ("wrong_way", "course-signs/textures/sign_wrong_way.png"),
        ("danger_x", "course-signs/textures/sign_danger_x.png"),
        ("arrow_back_wrong_way", "course-signs/textures/arrow_back_wrong_way.png"),
    ]
    # Fill remaining of row0 then row1 (y=0 and y=256) with 256 cells from x=512
    slots = []
    for y in (0, 256):
        for x in range(512, SIZE, 256):
            slots.append((x, y))
    for i, (key, rel) in enumerate(course):
        if i >= len(slots):
            break
        x, y = slots[i]
        place(atlas, layout["rects"], key, ROOT / rel, x, y, 256, 256, orm, 205, 140, 90)

    # --- Miles / laps / exits: 128×128 from y=512 ---
    cell = 128
    keys = []
    for n in range(1, 101):
        keys.append((f"mile_{n:03d}", ROOT / f"mile-marker/textures/mile_{n:03d}.png"))
    for n in range(1, 11):
        keys.append((f"lap_{n:02d}", ROOT / f"lap-signs/textures/lap_{n:02d}.png"))
    for ex in ("exit", "exit_left", "exit_right", "exit_up"):
        keys.append((ex, ROOT / f"pits/textures/{ex}.png"))

    cols = SIZE // cell  # 16
    start_y = 512
    for i, (key, path) in enumerate(keys):
        col = i % cols
        row = i // cols
        px = col * cell
        py = start_y + row * cell
        if py + cell > SIZE:
            print(f"  WARNING: atlas full at {key}")
            break
        # Signs: mid roughness, slight metal
        place(atlas, layout["rects"], key, path, px, py, cell, cell, orm, 215, 150, 40)

    save_rgba(OUT / "sign_atlas_2048.png", SIZE, SIZE, atlas)
    save_rgba(OUT / "sign_orm_2048.png", SIZE, SIZE, orm)
    (OUT / "sign_atlas_layout.json").write_text(json.dumps(layout, indent=2))
    print(f"wrote {OUT / 'sign_atlas_2048.png'} ({len(layout['rects'])} rects)")


def build_vegetation_atlas():
    print("=== Vegetation / rock atlas 2048 ===")
    atlas = solid(SIZE, SIZE, (40, 35, 28, 255))
    orm = solid(SIZE, SIZE, (200, 230, 10, 255))
    layout = {
        "atlas": "vegetation_atlas_2048.png",
        "orm": "vegetation_orm_2048.png",
        "size": SIZE,
        "rects": {},
    }

    # Rocks: 512×512 tiles in top-left 2×2
    rocks = [
        ("rock_tan", "rocks/textures/rock_tan.png", 210, 235, 8),
        ("rock_red", "rocks/textures/rock_red.png", 205, 230, 8),
        ("rock_gray", "rocks/textures/rock_gray.png", 200, 220, 25),
        ("rock_dark", "rocks/textures/rock_dark.png", 190, 240, 15),
    ]
    for i, (key, rel, ao, rough, metal) in enumerate(rocks):
        px = (i % 2) * 512
        py = (i // 2) * 512
        place(atlas, layout["rects"], key, ROOT / rel, px, py, 512, 512, orm, ao, rough, metal)

    # Flora / ground: 512 tiles filling rest of top half + bottom
    flora = [
        ("creosote_bark", 180, 200, 5),
        ("creosote_leaf", 190, 210, 5),
        ("saguaro_skin", 185, 195, 5),
        ("saguaro_rib", 175, 200, 5),
        ("dry_bush", 195, 215, 5),
        ("sand_ground", 220, 240, 5),
        ("ocotillo_stem", 185, 205, 5),
        ("hay_proxy", 200, 230, 5),  # extra slot — reuse hay-ish noise
    ]
    # Positions: right of rocks and below (512-grid)
    positions = [
        (1024, 0),
        (1536, 0),
        (1024, 512),
        (1536, 512),
        (0, 1024),
        (512, 1024),
        (1024, 1024),
        (1536, 1024),
    ]
    for (key, ao, rough, metal), (px, py) in zip(flora, positions):
        kind = "dry_bush" if key == "hay_proxy" else key
        tile = procedural_tile(512, 512, kind)
        place_generated(
            atlas, layout["rects"], key, tile, 512, 512, px, py, 512, 512, orm, ao, rough, metal
        )

    # Bottom row: smaller detail variants 256
    detail = ["creosote_leaf", "saguaro_skin", "sand_ground", "dry_bush"]
    for i, kind in enumerate(detail):
        px = i * 256
        py = 1536
        tile = procedural_tile(256, 256, kind)
        place_generated(
            atlas,
            layout["rects"],
            f"{kind}_detail",
            tile,
            256,
            256,
            px,
            py,
            256,
            256,
            orm,
            190,
            210,
            5,
        )

    save_rgba(OUT / "vegetation_atlas_2048.png", SIZE, SIZE, atlas)
    save_rgba(OUT / "vegetation_orm_2048.png", SIZE, SIZE, orm)
    (OUT / "vegetation_atlas_layout.json").write_text(json.dumps(layout, indent=2))
    print(f"wrote {OUT / 'vegetation_atlas_2048.png'} ({len(layout['rects'])} rects)")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_sign_atlas()
    build_vegetation_atlas()
    print("DONE atlases")


if __name__ == "__main__":
    main()
