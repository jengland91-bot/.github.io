#!/usr/bin/env python3
"""Convert 2026 Parker 400 C/T/UTV GPX into BeamNG map course JSON (1:1 meters).

Outputs under source/reference/p400/:
  - p400_map_course.json   (course UV + local meters + meta)
  - p400_map_waypoints.json (pits, VCPs, dangers, mile markers, speed zones)
  - course_preview.svg     (quick layout preview)

World: 65536 m square @ 8192 heightmap → squareSize 8 m (covers full race bbox 1:1).
"""

from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P400 = ROOT / "source" / "reference" / "p400"
GPX = P400 / "2026_Parker_400_CTUTV_Final_Racer_File.gpx"

WORLD_M = 65536.0
SIZE = 8192
MARGIN = 0.04  # keep course inside usable map
COURSE_DECIMATE_M = 45.0  # DecalRoad node spacing target


def local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def parse_gpx(path: Path) -> tuple[list[tuple[float, float, float | None]], list[dict]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    track: list[tuple[float, float, float | None]] = []
    wpts: list[dict] = []
    for el in root.iter():
        name = local(el.tag)
        if name == "trkpt":
            lat = float(el.attrib["lat"])
            lon = float(el.attrib["lon"])
            ele = None
            for c in el:
                if local(c.tag) == "ele" and c.text:
                    ele = float(c.text)
            track.append((lat, lon, ele))
        elif name == "wpt":
            lat = float(el.attrib["lat"])
            lon = float(el.attrib["lon"])
            ele = None
            nm = None
            sym = None
            desc = None
            for c in el:
                cn = local(c.tag)
                if cn == "ele" and c.text:
                    ele = float(c.text)
                elif cn == "name" and c.text:
                    nm = c.text.strip()
                elif cn == "sym" and c.text:
                    sym = c.text
                elif cn == "desc" and c.text:
                    desc = c.text
            wpts.append({"lat": lat, "lon": lon, "ele": ele, "name": nm, "sym": sym, "desc": desc})
    return track, wpts


def classify_waypoint(name: str | None) -> str:
    n = name or ""
    if n in ("Start Line", "Finish Line"):
        return "gates"
    if "Pit" in n:
        return "pits"
    if n.startswith("VCP"):
        return "vcps"
    if any(k in n for k in ("Stop Check", "SZ", "Speed Zone", "Stop Ahead", "25 MPH")):
        return "speedzones"
    if any(k in n for k in ("Danger", "Wash", "Hole", "Rock", "Drop")):
        return "hazards"
    if n.isdigit():
        return "mile_markers"
    return "other"


def build_geo_frame(track: list[tuple[float, float, float | None]]) -> dict:
    lats = [p[0] for p in track]
    lons = [p[1] for p in track]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    lat0 = (min_lat + max_lat) / 2.0

    def to_m(lat: float, lon: float) -> tuple[float, float]:
        # Local ENU-ish meters from SW corner of course bbox
        x = haversine(lat, min_lon, lat, lon) * (1 if lon >= min_lon else -1)
        y = haversine(min_lat, lon, lat, lon) * (1 if lat >= min_lat else -1)
        return x, y

    meters = [to_m(lat, lon) for lat, lon, _ in track]
    minx = min(x for x, _ in meters)
    maxx = max(x for x, _ in meters)
    miny = min(y for _, y in meters)
    maxy = max(y for _, y in meters)
    span_x = maxx - minx
    span_y = maxy - miny
    span = max(span_x, span_y)
    usable = WORLD_M * (1.0 - 2.0 * MARGIN)
    # True 1:1 — only shrink if the course somehow exceeds usable world
    scale = 1.0 if span <= usable else usable / span
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    return {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon,
        "lat0": lat0,
        "minx": minx,
        "maxx": maxx,
        "miny": miny,
        "maxy": maxy,
        "span_x": span_x,
        "span_y": span_y,
        "span": span,
        "cx": cx,
        "cy": cy,
        "scale": scale,
        "to_m": to_m,
    }


def meters_to_uv(xm: float, ym: float, frame: dict) -> tuple[float, float]:
    # Center course in world, apply scale (usually 1.0)
    X = WORLD_M / 2.0 + (xm - frame["cx"]) * frame["scale"]
    Y = WORLD_M / 2.0 + (ym - frame["cy"]) * frame["scale"]
    u = X / WORLD_M
    v = Y / WORLD_M
    return u, v


def decimate(points: list[tuple[float, float, float, float]], max_step_m: float) -> list[list[float]]:
    """Decimate [lat,lon,u,v] by map-meter spacing along polyline."""
    if not points:
        return []
    out = [[round(points[0][2], 6), round(points[0][3], 6)]]
    last_u, last_v = points[0][2], points[0][3]
    for _, _, u, v in points[1:]:
        dist = math.hypot(u - last_u, v - last_v) * WORLD_M
        if dist >= max_step_m:
            out.append([round(u, 6), round(v, 6)])
            last_u, last_v = u, v
    # always keep last
    lu, lv = points[-1][2], points[-1][3]
    if out[-1][0] != round(lu, 6) or out[-1][1] != round(lv, 6):
        out.append([round(lu, 6), round(lv, 6)])
    return out


def track_length_m(track: list[tuple[float, float, float | None]]) -> float:
    total = 0.0
    for i in range(1, len(track)):
        total += haversine(track[i - 1][0], track[i - 1][1], track[i][0], track[i][1])
    return total


def write_preview_svg(course_uv: list[list[float]], waypoints: dict, path: Path) -> None:
    w = h = 1024
    pad = 24

    def xy(u: float, v: float) -> tuple[float, float]:
        # SVG Y grows down; map V is north-up → flip
        x = pad + u * (w - 2 * pad)
        y = pad + (1.0 - v) * (h - 2 * pad)
        return x, y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#1a1410"/>',
        '<text x="32" y="40" fill="#e8c56a" font-family="Georgia, serif" font-size="28">Parker 400 — 2026 C/T/UTV</text>',
        '<text x="32" y="68" fill="#a89880" font-family="sans-serif" font-size="14">1:1 desert race corridor · CTUTV final racer file</text>',
    ]
    if len(course_uv) >= 2:
        d = "M " + " L ".join(f"{xy(u, v)[0]:.1f},{xy(u, v)[1]:.1f}" for u, v in course_uv)
        parts.append(f'<path d="{d}" fill="none" stroke="#f2c747" stroke-width="2.2" stroke-linejoin="round"/>')

    colors = {
        "gates": "#5ad4ff",
        "pits": "#50c86e",
        "hazards": "#ff5a3a",
        "vcps": "#c48cff",
        "mile_markers": "#d8c8a8",
        "speedzones": "#ffb040",
    }
    for cat, color in colors.items():
        for m in waypoints.get(cat, []):
            u, v = m["uv"]
            x, y = xy(u, v)
            r = 5 if cat in ("gates", "pits") else 3
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>')

    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    track, wpts = parse_gpx(GPX)
    frame = build_geo_frame(track)
    length_m = track_length_m(track)

    course_pts: list[tuple[float, float, float, float]] = []
    for lat, lon, _ele in track:
        xm, ym = frame["to_m"](lat, lon)
        u, v = meters_to_uv(xm, ym, frame)
        course_pts.append((lat, lon, u, v))

    course_uv = decimate(course_pts, COURSE_DECIMATE_M)

    by_cat: dict[str, list] = defaultdict(list)
    for w in wpts:
        cat = classify_waypoint(w["name"])
        xm, ym = frame["to_m"](w["lat"], w["lon"])
        u, v = meters_to_uv(xm, ym, frame)
        item = {
            "name": w["name"],
            "lat": round(w["lat"], 6),
            "lon": round(w["lon"], 6),
            "ele": w["ele"],
            "uv": [round(u, 6), round(v, 6)],
            "sym": w.get("sym"),
        }
        by_cat[cat].append(item)

    # Pit centers for a simple pit pad ribbon (Main Pit + numbered pits)
    pit_named = [
        w
        for w in by_cat.get("pits", [])
        if w["name"] and "Ahead" not in w["name"]
    ]

    course = {
        "source": "2026 Parker 400 CTUTV - Final Racer File",
        "trackName": "P400 Car/Truck/UTV",
        "worldSizeMeters": WORLD_M,
        "heightmapResolution": SIZE,
        "squareSize": WORLD_M / SIZE,
        "geographicScale": round(frame["scale"], 6),
        "courseMiles": round(length_m / 1609.344, 3),
        "courseKm": round(length_m / 1000.0, 3),
        "rawTrackPoints": len(track),
        "decalRoadNodes": len(course_uv),
        "bbox": {
            "minLat": round(frame["min_lat"], 6),
            "maxLat": round(frame["max_lat"], 6),
            "minLon": round(frame["min_lon"], 6),
            "maxLon": round(frame["max_lon"], 6),
            "spanMetersEW": round(frame["span_x"], 1),
            "spanMetersNS": round(frame["span_y"], 1),
        },
        "transform": {
            "cx": frame["cx"],
            "cy": frame["cy"],
            "minLat": frame["min_lat"],
            "minLon": frame["min_lon"],
            "scale": frame["scale"],
            "margin": MARGIN,
        },
        "longCourseUv": course_uv,
        "pitCenters": pit_named,
    }

    waypoints = {
        "source": course["source"],
        "counts": {k: len(v) for k, v in sorted(by_cat.items())},
        **by_cat,
    }

    P400.mkdir(parents=True, exist_ok=True)
    (P400 / "p400_map_course.json").write_text(json.dumps(course, indent=2) + "\n", encoding="utf-8")
    (P400 / "p400_map_waypoints.json").write_text(json.dumps(waypoints, indent=2) + "\n", encoding="utf-8")
    write_preview_svg(course_uv, waypoints, P400 / "course_preview.svg")

    print(
        json.dumps(
            {
                "courseMiles": course["courseMiles"],
                "nodes": course["decalRoadNodes"],
                "scale": course["geographicScale"],
                "squareSize": course["squareSize"],
                "bboxKm": [round(frame["span_x"] / 1000, 2), round(frame["span_y"] / 1000, 2)],
                "waypointCounts": waypoints["counts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
