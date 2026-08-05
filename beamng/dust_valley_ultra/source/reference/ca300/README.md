# CA300 course reference

Source files from the **2024 California 300** C/T/U Race Ready course (LeadNav / race GPS export).

## What we use them for
- **Course GPX/KML** → long-course centerline shape for Dust Valley Ultra
- **Dangers GPX/KML** → places to sculpt g-outs, rocks, washouts, ledges, poles

This is for **layout inspiration / path geometry**, not a claim on the real race org’s branding or land. Rebuild the desert as an original BeamNG park that *drives* like CA300.

## Numbers
| Item | Value |
| --- | --- |
| Main course length | ~74.2 miles |
| Pit row | ~0.5 miles |
| Real footprint | ~15.3 × 15.6 km |
| Fit in 16.384 km park | Yes, at ~0.97× geographic scale |
| Danger markers | 68 |

## Files
| File | Role |
| --- | --- |
| `2024_CA300_Course_Race_Ready.gpx` | Master course + race miles / VCPs |
| `2024_CA300_Course_Race_Ready.kml` | Same course for Google Earth |
| `2024_CA300_Dangers.gpx` / `.kml` | Danger callouts |
| `convert_ca300_to_map.py` | GPX → map UV JSON |
| `ca300_map_course.json` | Downsampled long-course polyline |
| `ca300_map_dangers.json` | Danger markers in map space |
| `course_preview.png` | Quick look |

## Regenerate map data
```bash
python3 source/reference/ca300/convert_ca300_to_map.py
python3 source/generate_heightmap.py
```
