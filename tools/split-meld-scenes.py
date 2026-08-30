#!/usr/bin/env python3
"""Split meld/Rise-Above-Meld.json into one session file per scene."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "meld" / "Rise-Above-Meld.json"
OUT = ROOT / "LOAD-THESE-SCENES"

SCENE_FILES = [
    ("1 STARTING SOON.json", "STARTING SOON"),
    ("2 GRID.json", "GRID"),
    ("3 DESK.json", "DESK"),
    ("4 RACE.json", "RACE"),
    ("5 RACE DUAL.json", "RACE DUAL"),
    ("6 REPLAY.json", "REPLAY"),
    ("7 BRB.json", "BRB"),
    ("8 ENDING.json", "ENDING"),
]


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    session = json.loads(SRC.read_text(encoding="utf-8"))
    items = session["items"]
    OUT.mkdir(exist_ok=True)

    for obj in items.values():
        if obj.get("type") == "scene":
            obj["current"] = obj.get("name") == "STARTING SOON"
    dump(OUT / "0 ALL SCENES.json", session)
    text = json.dumps(session, indent=2) + "\n"
    (ROOT / "IMPORT-THIS-IN-MELD.json").write_text(text, encoding="utf-8")
    (ROOT / "Rise-Above.json").write_text(text, encoding="utf-8")

    tracks = {iid: obj for iid, obj in items.items() if obj.get("type") == "track"}
    scenes = {iid: obj for iid, obj in items.items() if obj.get("type") == "scene"}
    name_to_id = {obj["name"]: iid for iid, obj in scenes.items()}

    for filename, name in SCENE_FILES:
        sid = name_to_id[name]
        subset = dict(tracks)
        scene = dict(scenes[sid])
        scene["index"] = 0
        scene["current"] = True
        scene["staged"] = False
        subset[sid] = scene
        for iid, obj in items.items():
            if obj.get("type") == "layer" and obj.get("parent") == sid:
                subset[iid] = obj
        dump(OUT / filename, {"items": subset})

    print(f"wrote {OUT} ({1 + len(SCENE_FILES)} session files)")


if __name__ == "__main__":
    main()
