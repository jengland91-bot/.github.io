#!/usr/bin/env python3
"""Assemble beamng-props/READY_TO_COPY from each kit's export/dae folder."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "READY_TO_COPY" / "art" / "shapes" / "props"

KITS = {
    "mile-marker": "milemarkers",
    "course-signs": "course_signs",
    "lap-signs": "lapsigns",
    "arch-gate": "arch",
    "barriers": "barriers",
    "chainlink": "chainlink",
    "desert-flora": "flora",
    "feather-flags": "featherflags",
    "hay-bales": "haybales",
    "k-rails": "krails",
    "light-towers": "lighttowers",
    "pits": "pits",
    "porta-potties": "portapotties",
    "rocks": "rocks",
    "safety-netting": "safetynetting",
    "tents": "tents",
    "tire-stacks": "tirestacks",
}


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST.parent.parent)  # wipe READY_TO_COPY
    DEST.mkdir(parents=True)
    readme_src = ROOT / "READY_TO_COPY_README.md"
    out_root = ROOT / "READY_TO_COPY"
    out_root.mkdir(parents=True, exist_ok=True)
    if readme_src.exists():
        shutil.copy2(readme_src, out_root / "README.md")
    for src_name, dst_name in KITS.items():
        src = ROOT / src_name / "export" / "dae"
        dst = DEST / dst_name
        if not src.is_dir():
            print(f"skip missing {src}")
            continue
        shutil.copytree(src, dst)
        n = sum(1 for _ in dst.rglob("*") if _.is_file())
        print(f"{src_name} -> {dst_name} ({n} files)")
    print(f"DONE {out_root}")


if __name__ == "__main__":
    main()
