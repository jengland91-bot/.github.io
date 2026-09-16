# Open-Shoulder Bucket Phone Cradle

Original 3D-printable phone holder shaped like an **open-shoulder racing bucket seat**.

Designed to sell as your own product (Etsy / Shopify / MakerWorld paid, etc.) — **not** a remix of the MakerWorld sim-rig seat holder, and **not** branded as Sparco or Recaro.

## Why this design (vs the MakerWorld link)

| | MakerWorld #1669652 | This product |
|---|---|---|
| Look | Racing-seat phone cradle | Original open-shoulder bucket (EVO III *silhouette cue*: no tall head wings) |
| Mount | Twist-fit into aluminum T-slot | **40 mm tube clamp** for Evolve-style steel frames + optional **4040 adapter** + desk base |
| Rights | Someone else's model | **Your original geometry** (generated here) |

Your Sparco **Evolve 3.0** uses **40 mm steel tubing**, so aluminum-profile clips from most free models will not fit cleanly. The clamp is the product advantage.

## Files

```
products/bucket-seat-phone-cradle/
  stl/
    seat_cradle.stl          # main phone cradle
    clamp_40mm_front.stl     # tube clamp half (dovetail receiver)
    clamp_40mm_rear.stl      # tube clamp half (nut side)
    adapter_4040.stl         # optional — M8 plate for 4040/4080 aluminum
    desk_stand_base.stl      # optional — desk / shelf stand
  scad/                      # parametric OpenSCAD sources (edit & re-export)
  scripts/generate_stl_v2.py # regenerates STLs (numpy only)
  docs/                      # print guide + Etsy listing draft
```

## Hardware (tube clamp kit)

- 2× M5 × 30 mm socket-cap screws  
- 2× M5 nylon-insert locknuts (or heat-set inserts in the rear half)  
- Optional: thin rubber strip inside the bore so it does not mark powder coat  

## Trademark / selling notes

- **Do use:** “open-shoulder bucket seat phone holder”, “fits 40 mm tubular sim cockpits”, “compatible with Evolve-style 40 mm frames”.
- **Do not use in titles/branding:** Sparco logos, Recaro name, or “official” claims.
- Compatibility language (“fits 40 mm tube / Evolve-style chassis”) is normally fine; copying another STL is not.
- Re-measure your phone (with case) and tube OD before listing “fits all phones”.

## Regenerate meshes

```bash
python3 products/bucket-seat-phone-cradle/scripts/generate_stl_v2.py
```

For cleaner CAD edits later, install OpenSCAD locally and open the files in `scad/`.
