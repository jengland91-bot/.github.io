#!/usr/bin/env python3
"""Convert 2024 CA300 GPX into Dust Valley Ultra map coordinates.

Reads the Race Ready course + danger markers and writes:
  - ca300_map_course.json   (downsampled long-course polyline in 0..1 UV)
  - ca300_map_dangers.json  (danger / waypoint markers in 0..1 UV)
  - ca300_course_preview.png

The real CA300 footprint (~15.3 × 15.6 km) fits inside the 16.384 km park
at ~0.97× geographic scale (nearly 1:1).
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WORLD_M = 16384.0
MARGIN = 0.04  # keep a little desert padding around the real footprint
HERE = Path(__file__).resolve().parent


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def parse_tracks(gpx: str) -> list[dict]:
    tracks = []
    for trk in re.finditer(r"<trk>(.*?)</trk>", gpx, re.S):
        block = trk.group(1)
        name_m = re.search(r"<name>([^<]*)</name>", block)
        segs = []
        for seg in re.finditer(r"<trkseg>(.*?)</trkseg>", block, re.S):
            pts = []
            for m in re.finditer(r'<trkpt\s+([^>/]+)/?>', seg.group(1)):
                attrs = m.group(1)
                lat = float(re.search(r'lat="([^"]+)"', attrs).group(1))
                lon = float(re.search(r'lon="([^"]+)"', attrs).group(1))
                pts.append((lat, lon))
            if pts:
                segs.append(pts)
        tracks.append({"name": name_m.group(1) if name_m else "unnamed", "segments": segs})
    return tracks


def parse_wpts(gpx: str) -> list[tuple[float, float, str]]:
    out = []
    for m in re.finditer(r"<wpt\s+([^>]+)>", gpx):
        attrs = m.group(1)
        lat = float(re.search(r'lat="([^"]+)"', attrs).group(1))
        lon = float(re.search(r'lon="([^"]+)"', attrs).group(1))
        chunk = gpx[m.end() : m.end() + 400]
        name_m = re.search(r"<name>([^<]*)</name>", chunk)
        out.append((lat, lon, name_m.group(1) if name_m else ""))
    return out


def path_len(pts: list[tuple[float, float]]) -> float:
    return sum(haversine(a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:]))


def downsample(pts: list[tuple[float, float]], max_pts: int = 360) -> list[tuple[float, float]]:
    if len(pts) <= max_pts:
        return pts
    # Keep roughly equal arc-length spacing
    total = path_len(pts)
    step = total / (max_pts - 1)
    keep = [pts[0]]
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        acc += haversine(a[0], a[1], b[0], b[1])
        if acc >= step:
            keep.append(b)
            acc = 0.0
    if keep[-1] != pts[-1]:
        keep.append(pts[-1])
    return keep


def main() -> None:
    course_gpx = (HERE / "2024_CA300_Course_Race_Ready.gpx").read_text(encoding="utf-8")
    danger_gpx = (HERE / "2024_CA300_Dangers.gpx").read_text(encoding="utf-8")

    tracks = parse_tracks(course_gpx)
    main_pts = tracks[0]["segments"][0]
    pit_pts = tracks[1]["segments"][0] if len(tracks) > 1 else []
    dangers = parse_wpts(danger_gpx)
    wpts = parse_wpts(course_gpx)

    all_pts = main_pts + pit_pts
    lats = [p[0] for p in all_pts]
    lons = [p[1] for p in all_pts]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    def to_m(lat: float, lon: float) -> tuple[float, float]:
        x = haversine(lat, min_lon, lat, lon)
        y = haversine(min_lat, lon, lat, lon)
        return x, y

    meters = [to_m(lat, lon) for lat, lon in all_pts]
    minx = min(x for x, _ in meters)
    maxx = max(x for x, _ in meters)
    miny = min(y for _, y in meters)
    maxy = max(y for _, y in meters)
    span = max(maxx - minx, maxy - miny)
    usable = WORLD_M * (1 - 2 * MARGIN)
    scale = usable / span
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2

    def to_uv(lat: float, lon: float) -> tuple[float, float]:
        x, y = to_m(lat, lon)
        X = (x - cx) * scale + WORLD_M / 2
        Y = (y - cy) * scale + WORLD_M / 2
        return (X / WORLD_M, Y / WORLD_M)

    course_uv = [to_uv(lat, lon) for lat, lon in downsample(main_pts, 400)]
    pit_uv = [to_uv(lat, lon) for lat, lon in pit_pts] if pit_pts else []

    danger_payload = []
    for lat, lon, name in dangers:
        u, v = to_uv(lat, lon)
        severity = "extreme" if "Extreme" in name else "danger"
        danger_payload.append(
            {
                "name": name,
                "severity": severity,
                "uv": [round(u, 5), round(v, 5)],
                "lat": lat,
                "lon": lon,
            }
        )

    key_wpts = []
    for lat, lon, name in wpts:
        upper = name.upper()
        if any(k in upper for k in ("START", "FINISH", "PIT", "RM1", "RM74", "STOP CHECK")) or name.startswith("RM") and name[2:].isdigit() and int(name[2:]) % 10 == 0:
            u, v = to_uv(lat, lon)
            key_wpts.append({"name": name, "uv": [round(u, 5), round(v, 5)], "lat": lat, "lon": lon})

    course_json = {
        "source": "2024 CA300 C_T_U Course - Race Ready",
        "worldSizeMeters": WORLD_M,
        "geographicScale": round(scale, 4),
        "courseMiles": round(path_len(main_pts) / 1609.34, 2),
        "pitRowMiles": round(path_len(pit_pts) / 1609.34, 2) if pit_pts else 0,
        "longCourseUv": [[round(u, 5), round(v, 5)] for u, v in course_uv],
        "pitRowUv": [[round(u, 5), round(v, 5)] for u, v in pit_uv],
        "note": "UV is normalized map space (0..1). Y increases north. Use as long-course centerline.",
    }
    (HERE / "ca300_map_course.json").write_text(json.dumps(course_json, indent=2) + "\n", encoding="utf-8")
    (HERE / "ca300_map_dangers.json").write_text(
        json.dumps(
            {
                "source": "2024 CA300 C_T_U Dangers",
                "count": len(danger_payload),
                "types": dict(Counter(d["name"] for d in danger_payload)),
                "markers": danger_payload,
                "keyWaypoints": key_wpts,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Preview
    size = 1400
    img = Image.new("RGB", (size, size + 160), (18, 16, 14))
    draw = ImageDraw.Draw(img)
    for yy in range(size):
        c = int(70 + 25 * ((yy / size) ** 0.5))
        draw.line([(0, yy), (size, yy)], fill=(c + 30, c + 10, max(0, c - 20)))

    def pix(uv: tuple[float, float]) -> tuple[float, float]:
        return uv[0] * (size - 1), (1 - uv[1]) * (size - 1)

    pts = [pix(p) for p in course_uv]
    draw.line(pts, fill=(20, 16, 12), width=5)
    draw.line(pts, fill=(242, 199, 71), width=3)
    if pit_uv:
        draw.line([pix(p) for p in pit_uv], fill=(50, 200, 110), width=4)
    for d in danger_payload:
        px, py = pix(tuple(d["uv"]))
        col = (230, 55, 70) if d["severity"] == "extreme" else (242, 115, 38)
        r = 4 if d["severity"] == "extreme" else 3
        draw.ellipse([px - r, py - r, px + r, py + r], fill=col)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    draw.text((20, size + 18), f"CA300 → Dust Valley Ultra  |  {course_json['courseMiles']} mi long course", fill=(245, 235, 210), font=font)
    draw.text((20, size + 48), f"Nearly 1:1 fit (scale {scale:.2f}) inside 16.4 km park", fill=(220, 210, 195), font=font_sm)
    draw.text((20, size + 72), f"{len(danger_payload)} danger markers  |  gold = race line  |  green = pit row", fill=(220, 210, 195), font=font_sm)
    draw.text((20, size + 96), "Ideas for layout: g-outs, rocks, washouts, poles — not a copy of real land ownership", fill=(220, 210, 195), font=font_sm)
    img.save(HERE / "course_preview.png")
    img.save("/opt/cursor/artifacts/ca300_course_preview.png")

    print(json.dumps({
        "courseMiles": course_json["courseMiles"],
        "pointsOut": len(course_uv),
        "dangers": len(danger_payload),
        "scale": round(scale, 3),
        "wrote": ["ca300_map_course.json", "ca300_map_dangers.json", "course_preview.png"],
    }, indent=2))


if __name__ == "__main__":
    main()
