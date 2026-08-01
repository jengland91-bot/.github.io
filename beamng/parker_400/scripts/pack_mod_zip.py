#!/usr/bin/env python3
"""Pack parker_400.zip + Parker400_Download_Both.zip under GitHub 100 MiB."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVEL = ROOT / "levels" / "parker_400"
MOD_ZIP = ROOT / "mods_drop_in" / "parker_400.zip"
BOTH_ZIP = ROOT / "Parker400_Download_Both.zip"

# Omit bulky / unused assets from the shipped mod
EXCLUDE = {
    "import/heightmap_4096.png",  # optional re-import only; .ter is baked
    "import/heightmap_8192.png",  # HD optional (~115 MB) — cannot ship in GitHub zip
    "import/heightmap_meta.json",  # tiny but keep repo; not needed at runtime
    "art/terrains/desert_base_sat512_b.png",  # replaced by HD JPG
    "art/terrains/parker400_base_color.png",  # replaced by JPG
    "art/terrains/desert_base_base_b.png",  # unused — unique sat is the base color
    "preview.png",  # reclaim space for 16k sat
}
EXCLUDE_PREFIXES = (
    "art/terrains/hd4096/",
    "art/terrains/rock_slope_",  # not painted in .ter
)
EXCLUDE_SUFFIXES = (
    # keep 4096 PBR bases; drop unused classic 512 color where 4096 exists is optional
)


def keep(rel: str) -> bool:
    if rel in EXCLUDE:
        return False
    if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
        return False
    if any(rel.endswith(s) for s in EXCLUDE_SUFFIXES):
        return False
    return True


def main() -> None:
    MOD_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(MOD_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(LEVEL.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(LEVEL).as_posix()
            if not keep(rel):
                print("skip", rel)
                continue
            z.write(path, f"levels/parker_400/{rel}")

    extras = [
        "RUN_INSTALL.cmd",
        "INSTALL_UNPACKED.bat",
        "INSTALL_UNPACKED.ps1",
        "MANUAL_INSTALL.txt",
        "BLACK_VOID_FIX.md",
        "FIX_AND_INSTALL.bat",
    ]
    with zipfile.ZipFile(BOTH_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(MOD_ZIP, "parker_400.zip")
        for e in extras:
            p = ROOT / e
            if p.exists():
                z.write(p, p.name)

    for p in (MOD_ZIP, BOTH_ZIP):
        mib = p.stat().st_size / (1024 * 1024)
        print(f"{p.name}: {mib:.2f} MiB")
        if p.stat().st_size >= 100 * 1024 * 1024:
            raise SystemExit(f"FAIL: {p} exceeds GitHub 100 MiB hard limit")

    with zipfile.ZipFile(MOD_ZIP) as z:
        names = z.namelist()
        assert any(n.endswith("theTerrain.ter") for n in names)
        assert any(n.endswith("parker400_base_color.jpg") for n in names)
        assert not any(n.endswith("parker400_base_color.png") for n in names)
        print("files", len(names), "uncompressed_MB", round(sum(i.file_size for i in z.infolist()) / 1e6, 1))


if __name__ == "__main__":
    main()
