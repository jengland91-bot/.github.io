#!/usr/bin/env python3
"""Build Rise-Above-Meld.zip with a visible top-level folder name."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Rise-Above-Meld.zip"
PREFIX = "Rise-Above-Meld"

SKIP_DIRS = {".git", "__pycache__", ".cursor"}
SKIP_FILES = {"Rise-Above-Meld.zip"}
SKIP_SUFFIXES = {".pyc"}


def keep(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if path.name in SKIP_FILES:
        return False
    if path.suffix in SKIP_SUFFIXES:
        return False
    return True


def main() -> None:
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and keep(p))
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            arc = f"{PREFIX}/{p.relative_to(ROOT).as_posix()}"
            zf.write(p, arcname=arc)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(files)} files)")


if __name__ == "__main__":
    main()
