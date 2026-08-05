#!/usr/bin/env python3
"""Generate original desert terrain materials for California 300."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "levels" / "california_300" / "art" / "terrains"
LEVEL = ROOT / "levels" / "california_300"

BASE_PX = 512
MACRO_PX = 1024
DETAIL_PX = 1024


def fbm(size: int, seed: int, octaves: int = 5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.zeros((size, size), dtype=np.float32)
    amp = 1.0
    for o in range(octaves):
        step = max(2, size // (4 * (2 ** o)))
        grid = rng.random((size // step + 2, size // step + 2), dtype=np.float32)
        yy = np.linspace(0, grid.shape[0] - 2, size, dtype=np.float32)
        xx = np.linspace(0, grid.shape[1] - 2, size, dtype=np.float32)
        y0 = np.floor(yy).astype(np.int32)
        x0 = np.floor(xx).astype(np.int32)
        fy = yy - y0
        fx = xx - x0
        # bilinear
        g00 = grid[y0][:, x0]
        g10 = grid[y0][:, x0 + 1]
        g01 = grid[y0 + 1][:, x0]
        g11 = grid[y0 + 1][:, x0 + 1]
        # fix shapes: use mesh
        Y, X = np.meshgrid(y0, x0, indexing="ij")
        FY, FX = np.meshgrid(fy, fx, indexing="ij")
        v00 = grid[Y, X]
        v10 = grid[Y, X + 1]
        v01 = grid[Y + 1, X]
        v11 = grid[Y + 1, X + 1]
        v0 = v00 * (1 - FX) + v10 * FX
        v1 = v01 * (1 - FX) + v11 * FX
        out += (v0 * (1 - FY) + v1 * FY) * amp
        amp *= 0.5
    out -= out.min()
    out /= (out.max() + 1e-6)
    return out


def save_rgb(path: Path, arr: np.ndarray) -> None:
    Image.fromarray(arr.astype(np.uint8), "RGB").save(path, "PNG")


def save_gray(path: Path, arr: np.ndarray) -> None:
    Image.fromarray(arr.astype(np.uint8), "L").save(path, "PNG")


def save_normal(path: Path, height: np.ndarray, strength: float = 4.0) -> None:
    hL = np.roll(height, 1, axis=1)
    hR = np.roll(height, -1, axis=1)
    hD = np.roll(height, 1, axis=0)
    hU = np.roll(height, -1, axis=0)
    dx = (hL - hR) * strength
    dy = (hD - hU) * strength
    dz = np.ones_like(height)
    inv = 1.0 / np.sqrt(dx * dx + dy * dy + dz * dz)
    n = np.stack([(dx * inv) * 0.5 + 0.5, (dy * inv) * 0.5 + 0.5, (dz * inv) * 0.5 + 0.5], axis=-1)
    save_rgb(path, n * 255.0)


def colorize(n: np.ndarray, dark, light) -> np.ndarray:
    t = n[..., None]
    dark = np.array(dark, dtype=np.float32)
    light = np.array(light, dtype=np.float32)
    return dark * (1 - t) + light * t


def make_material(prefix: str, dark, light, seed: int, ground: str = "DIRT", annotation: str = "DIRT") -> dict:
    paths = {}
    for kind, size, s_off, nstr in (
        ("base", BASE_PX, 0, 3.5),
        ("macro", MACRO_PX, 11, 3.5),
        ("detail", DETAIL_PX, 29, 6.0),
    ):
        n = fbm(size, seed + s_off, octaves=6 if kind == "detail" else 5)
        b = ART / f"{prefix}_{kind}_b.png"
        r = ART / f"{prefix}_{kind}_r.png"
        ao = ART / f"{prefix}_{kind}_ao.png"
        h = ART / f"{prefix}_{kind}_h.png"
        nm = ART / f"{prefix}_{kind}_nm.png"
        save_rgb(b, colorize(n, dark, light))
        save_gray(r, 140 + n * 80)
        save_gray(ao, 180 + n * 60)
        save_gray(h, n * 255)
        save_normal(nm, n, strength=nstr)
        paths[kind] = {k: f"/levels/california_300/art/terrains/{prefix}_{kind}_{k}.png" for k in ("b", "nm", "r", "ao", "h")}

    return {
        "class": "TerrainMaterial",
        "internalName": prefix,
        "annotation": annotation,
        "groundmodelName": ground,
        "baseColorBaseTex": paths["base"]["b"],
        "baseColorBaseTexSize": 512,
        "baseColorMacroTex": paths["macro"]["b"],
        "baseColorMacroTexSize": 64,
        "baseColorMacroStrength": [0.15, 0.35],
        "baseColorDetailTex": paths["detail"]["b"],
        "baseColorDetailTexSize": 4,
        "baseColorDetailStrength": [0.35, 0.1],
        "normalBaseTex": paths["base"]["nm"],
        "normalBaseTexSize": 512,
        "normalMacroTex": paths["macro"]["nm"],
        "normalMacroTexSize": 64,
        "normalMacroStrength": [0.2, 0.4],
        "normalDetailTex": paths["detail"]["nm"],
        "normalDetailTexSize": 4,
        "normalDetailStrength": [0.6, 0.2],
        "roughnessBaseTex": paths["base"]["r"],
        "roughnessBaseTexSize": 512,
        "roughnessMacroTex": paths["macro"]["r"],
        "roughnessMacroTexSize": 64,
        "roughnessMacroStrength": [0.2, 0.7],
        "roughnessDetailTex": paths["detail"]["r"],
        "roughnessDetailTexSize": 4,
        "roughnessDetailStrength": [0.3, 0.3],
        "aoBaseTex": paths["base"]["ao"],
        "aoBaseTexSize": 512,
        "aoMacroTex": paths["macro"]["ao"],
        "aoMacroTexSize": 64,
        "aoDetailTex": paths["detail"]["ao"],
        "aoDetailTexSize": 4,
        "heightBaseTex": paths["base"]["h"],
        "heightBaseTexSize": 512,
        "heightMacroTex": paths["macro"]["h"],
        "heightMacroTexSize": 64,
        "heightDetailTex": paths["detail"]["h"],
        "heightDetailTexSize": 4,
        "macroDistances": [0, 10, 100, 3000],
        "detailDistances": [0, 0, 30, 60],
        "macroDistAtten": [1, 1],
        "detailDistAtten": [1, 1],
    }


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    desert = make_material("desert_base", (138, 102, 62), (186, 148, 96), 3001)
    course = make_material("course_pack", (150, 130, 100), (205, 190, 155), 3002)
    rock = make_material("rock_slope", (90, 78, 68), (145, 128, 112), 3003, ground="ROCK", annotation="ROCK")

    tex_set = "california_300TerrainMaterialTextureSet"
    materials = {
        tex_set: {
            "class": "TerrainMaterialTextureSet",
            "name": tex_set,
            "baseTexSize": [BASE_PX, BASE_PX],
            "macroTexSize": [MACRO_PX, MACRO_PX],
            "detailTexSize": [DETAIL_PX, DETAIL_PX],
        },
        "desert_base": desert,
        "course_pack": course,
        "rock_slope": rock,
    }
    (ART / "main.materials.json").write_text(json.dumps(materials, indent=2) + "\n", encoding="utf-8")

    items = LEVEL / "main" / "items.level.json"
    if items.exists():
        lines = []
        for line in items.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("class") == "TerrainBlock":
                obj["materialTextureSet"] = tex_set
            lines.append(json.dumps(obj, separators=(",", ":")))
        items.write_text("\n".join(lines) + "\n", encoding="utf-8")

    (ART / "README.txt").write_text(
        "Original California 300 desert materials.\n"
        "In Terrain Painter open Terrain Material Library and use desert_base.\n",
        encoding="utf-8",
    )
    print("pngs", len(list(ART.glob("*.png"))))
    print("wrote", ART / "main.materials.json")


if __name__ == "__main__":
    main()
