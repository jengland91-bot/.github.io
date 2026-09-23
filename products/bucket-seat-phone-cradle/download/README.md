# EVO Phone Cradle — SOLID printable kit (v5)

These STLs are **solid / watertight enough to slice and print**. Earlier faceted versions were open shells and would not work in Bambu Studio.

## First print (must-do)

1. Open `01_cradle_evo.stl` in **Bambu Studio**
2. Slice with PETG or PLA+, 0.20 mm, 4 walls, 25% infill
3. Print on your P2S
4. Drop an iPhone (with case) in the pocket — charge cable through the bottom notch
5. Screw on a back plate with **4× M3 × 10–12 mm** screws

## What’s in the download

| File | What it does |
|------|----------------|
| `01_cradle_evo.stl` | Seat + phone pocket (92×18 mm) + charge hole + M3 boss |
| `02_back_rail_vertical.stl` | Twist into **vertical** 4040-style rail |
| `03_back_rail_horizontal.stl` | Twist into **horizontal** rail |
| `04_back_leg_plate.stl` | Desk tripod plate |
| `05_desk_leg.stl` | Print **×3**, bolt into leg plate |
| `06_back_kickout_m3.stl` | Kick-out with M3 hole |
| `07_clamp_desk_m3.stl` | Desk-edge clamp → kick-out |
| `08_clamp_tube40_m3.stl` | 40 mm tube half-clamp (print **×2**) → kick-out |
| `09_back_blank_diy.stl` | Flat plate + extra M3 holes |

## Hardware

- Back attach: 4× M3 × 10–12 mm  
- Desk legs: 3× M3 × 16–20 mm  
- Kick-out: 1× M3 × 16–20 + locknut  
- Tube clamp: 2× M5 × 30 + locknuts  
- Desk clamp: 1× M5 thumb screw  

## Regenerate

```bash
python3 products/bucket-seat-phone-cradle/scripts/generate_stl_v5_solid.py
```

## Notes

- Original EVO-*style* geometry (not a Sparco / MakerWorld remix). Don’t brand as Sparco.  
- Pocket sized for **iPhone 18 Pro Max + thick case**.  
- If a rail is tight/loose, scale the **back STL only** ±2% in XY.
