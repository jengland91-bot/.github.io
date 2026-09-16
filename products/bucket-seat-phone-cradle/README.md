# EVO-Style Bucket Phone Cradle (modular)

Original product family for Etsy / physical sales. Shaped after an **open-shoulder EVO III–class bucket** (the seat style used in many race trucks) — **not** a remix of MakerWorld / Recaro free STLs.

## Phone fit

Sized for **iPhone 18 Pro Max** (78.0 × 8.75 mm) **plus a thick case**:

| Pocket | Spec |
|--------|------|
| Width | 92 mm |
| Thickness | 18 mm |
| Charge | Bottom notch + cable drop |

Smaller phones sit fine; Pro Max + chunky case is the design target.

## How the modular system works

One cradle. Swap the **back plate** with 4× M3 screws (30 mm square pattern):

| STL | What it does |
|-----|----------------|
| `01_cradle_evo.stl` | Main seat + phone pocket + charge hole + M3 boss |
| `02_back_rail_vertical.stl` | Twist-lock for **vertical** aluminum profile (4040-class) |
| `03_back_rail_horizontal.stl` | Twist-lock for **horizontal** aluminum rail |
| `04_back_leg_plate.stl` | Tripod bosses for desk legs |
| `05_desk_leg.stl` | Print **×3** — bolts into leg plate |
| `06_back_kickout_m3.stl` | Kick-out tab with **M3** (also works with M2 + sleeve) |
| `07_clamp_desk_m3.stl` | Desk-edge C-clamp → bolts to kick-out |
| `08_clamp_tube40_m3.stl` | Half-clamp for **40 mm** tube (print ×2) → kick-out |
| `09_back_blank_diy.stl` | Flat plate with extra M3 holes — add your own legs |

### Kits to sell

1. **Rail Vertical** — cradle + `02`  
2. **Rail Horizontal** — cradle + `03`  
3. **Desk Tripod** — cradle + `04` + 3× `05`  
4. **Desk Clamp** — cradle + `06` + `07`  
5. **Tube Clamp (Evolve-style)** — cradle + `06` + 2× `08`  
6. **DIY / blank** — cradle + `09`  
7. **Ultimate bundle** — cradle + all backs + legs + both clamps  

## Hardware

- **Back attach:** 4× M3 × 10–12 mm screws (+ heat-set inserts in cradle optional)  
- **Desk legs:** 3× M3 × 16–20 mm  
- **Kick-out pivot:** 1× M3 × 16–20 mm + locknut  
- **Tube clamp ears:** 2× M5 × 30 mm + locknuts  
- **Desk clamp screw:** 1× M5 thumb screw (or printed knob later)

## Regenerate

```bash
python3 products/bucket-seat-phone-cradle/scripts/generate_evo_cradle.py
```

Reference photos used for proportions: `docs/reference/`

## Trademark

Sell as original “EVO-style / open-shoulder bucket” phone cradle.  
Do **not** brand as Sparco or Recaro. Compatibility language for 40 mm tubular / 4040 rails is fine.

## Docs

- `docs/PRINT_GUIDE_P2S.md` — Bambu P2S settings  
- `docs/ETSY_LISTING_DRAFT.md` — listing copy for multi-variant SKUs  
- `docs/NEXT_STEPS.md` — prototype → photo → list  
