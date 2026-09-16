# Bambu Lab P2S — print guide (modular kit)

## Material

PETG preferred for clamps and cradle (cockpit heat). PLA+ OK for desk-only kits.

## Profile (start here)

| Setting | Cradle | Backs / legs | Clamps |
|---------|--------|--------------|--------|
| Layer | 0.20 mm | 0.20 mm | 0.20 mm |
| Walls | 4 | 4 | 5 |
| Infill | 25% gyroid | 30% | 40% gyroid |
| Supports | Tree on dovetail/pocket if upright | Usually none | Tree on C-clamp throat if needed |
| Brim | 5 mm if needed | No | No |

## Orientation

- **Cradle:** upright (boss toward back) or on its back for strongest rails  
- **Rail backs:** plate flat on bed, twist key pointing up  
- **Legs:** foot on bed  
- **Tube clamp half:** split face on bed  
- **Desk clamp:** spine on bed  

## Fit notes

1. Rail twist keys are sized for **4040-class ~8 mm T-slots**. If your profile is tighter/looser, scale XY ±2% on the back only.  
2. Vertical vs horizontal are **different STLs** — use the matching one.  
3. Phone pocket: 92 × 18 mm. If a case is wider, regenerate with `PHONE_W` / `PHONE_T` in `generate_stl_v3.py`.  
4. Tube clamp: nominal **40.4 mm** bore for Evolve-style 40 mm tube + paint.

## First prototype order

1. `01_cradle_evo` + `02` or `03` (your rig type)  
2. Then desk or tube accessories once the seat shape looks right on the P2S  
