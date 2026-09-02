# D1 QR steering-wheel wall mount

3D-printable hanger for **MOZA** wheels (ES, RS, CS, GS, FSR — anything with the stock ball-lock QR) and other **D1-spec / Simagic-style** 50 mm ball QRs.

Snap the wheel onto the stub the same way you clip it onto the base. A **continuous locking groove** means you do not have to line up the six balls.

This is an original product design, not a MOZA part and not a copy of a commercial listing.

**Want to sell prints?** Read [`SELLING.md`](SELLING.md) (Etsy title, compatible-with wording, PETG QC, photos).

![Top and side view](preview.svg)

## Print these files

| File | What it is |
| --- | --- |
| [`stl/fit_test_nominal.stl`](stl/fit_test_nominal.stl) | **Print this first.** Tiny coupon, ~15 minutes. |
| [`stl/fit_test_tight.stl`](stl/fit_test_tight.stl) / [`stl/fit_test_loose.stl`](stl/fit_test_loose.stl) | Same coupon, ±0.4 mm on the shaft if nominal is off. |
| [`stl/moza_qr_wall_mount.stl`](stl/moza_qr_wall_mount.stl) | Round wall plate, 4× countersunk #8 / 4.5 mm holes on a plus pattern. |
| [`stl/moza_qr_8020_mount.stl`](stl/moza_qr_8020_mount.stl) | Tab mount for 4040 / 2020 extrusion, 2× M8 at 40 mm spacing. |

Regenerate STLs after editing dimensions:

```bash
python3 generate.py            # default: nominal fit
python3 generate.py --fit loose
```

Or open `moza_qr_wall_mount.scad` in OpenSCAD and export.

## Bambu Lab print settings

Print **plate on the bed, stub pointing up**. No supports. The groove walls are 45° so a P1S / X1C / A1 will handle them.

| Setting | Value |
| --- | --- |
| Material | **PETG** (best). PLA or PLA-CF is fine for a light ES/RS wheel if the room stays cool. |
| Nozzle | 0.4 mm |
| Layer height | 0.20 mm (0.16 mm if you want a cleaner groove) |
| Walls | **6** (or 2.4 mm wall thickness) |
| Top / bottom | 5 |
| Infill | 40% gyroid |
| Supports | None |
| Brim | 5 mm, or a textured PEI plate with glue stick |
| Outer wall speed | ~40–60 mm/s so the shaft stays round |

A CS/GS wheel is ~1–1.5 kg hanging on a plastic stub. PETG + 6 walls is the conservative choice. After the first print, snap the wheel on **without** hanging it on the wall and tug it — it should click and not slide off under its own weight.

## Fit check

1. Print `fit_test_nominal.stl`.
2. Pull the gold/black QR collar and push the wheel on. It should snap. Pull the collar to release.
3. If it will not go on → print `fit_test_loose.stl` (or in `generate.py` drop `shaft_d` / `groove_d` by 0.4).
4. If it goes on but will not lock → print `fit_test_tight.stl`, or make sure you are pushing until the balls drop into the groove.
5. When the coupon feels right, print the matching full mount (`generate.py --fit …` if you changed it).

Nominal numbers (plastic, a little under the ~50 mm metal male QR):

- Shaft Ø **49.4 mm**
- Groove Ø **45.4 mm**, 45° walls, ~8.8 mm from the tip

## Hardware

**Wall mount**

- 4× **#8 × 1¼″** wood screws (4.5 mm shank) with countersunk heads, **or** M4 / M5 CSK.
- The holes are on a **plus** (+): north / south / east / west at 36 mm from centre. Put the north–south pair into a **stud** if you can; use rated drywall anchors for the other two.
- Optional: **M5 × 50 mm** through the centre of the stub into a stud. The head sits in a countersink on the tip and is hidden by the wheel.

**8020 / sim rig**

- 2× **M8 × 16–20 mm** socket-cap screws + T-nuts, 40 mm apart on the tab below the stub.

Do not hang this on a single drywall anchor. A wheel plus a yank while unclipping is a real load.

## Use

1. Screw the plate to the wall (or T-nut it to the rig). Stub points into the room.
2. Offer the wheel up and press on. You do **not** need to clock the six balls.
3. To remove: pull the QR collar with both hands and take the wheel off, same as on the base.

Paddle clearance: the plate is 98 mm across. That clears ES / RS / CS / GS paddles on a typical hang. If a deep formula wheel’s paddles kiss the plate, print the 8020 variant and use it as a standoff on a short piece of 2020, or increase `SHAFT_LEN` in `generate.py`.

## Tuning (`generate.py`)

| Constant | Default | What it does |
| --- | --- | --- |
| `FITS["nominal"].shaft_d` | 49.4 | Outer Ø the QR slides over |
| `FITS["nominal"].groove_d` | 45.4 | Groove floor Ø (balls lock here) |
| `SHAFT_LEN` | 26 | How far the stub sticks out |
| `PLATE_D` / `PLATE_T` | 98 / 8 | Wall plate size |
| `SCREW_R` | 36 | Screw circle |

## License

All rights reserved — see `LICENSE`. You may sell physical prints and digital files of this design. Do not publish the STLs on a public site if you are charging for them. Not affiliated with MOZA Racing.
