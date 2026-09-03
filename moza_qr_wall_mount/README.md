# D1 QR steering-wheel wall mount

3D-printable hanger for **MOZA** wheels (ES, RS, CS, GS, FSR — anything with the stock ball-lock QR) and other **D1-spec / Simagic-style** 50 mm ball QRs.

Snap the wheel onto the stub the same way you clip it onto the base. A shallow ring takes **all ten balls**, and **ten deeper seats** lock rotation so the wheel should not spin when bumped. Pull the QR collar, line up a ball with a seat (one seat is at 12 o'clock), then press on.

A ring-groove version with no pockets is also in `stl/` if you ever want free rotation.

This is an original product design, not a MOZA part and not a copy of a commercial listing.

**Want to sell prints?** Read [`SELLING.md`](SELLING.md) (Etsy title, compatible-with wording, PETG QC, photos).

## Download

**[sim-rig-kit.zip](sim-rig-kit.zip)** — wheel mount, fit tests, phone, cup, hook, clip, mouse tray.

| File | Download |
| --- | --- |
| Fit test (print first) | [fit_test_nominal.stl](stl/fit_test_nominal.stl) |
| Wheel mount | [moza_qr_universal_mount.stl](stl/moza_qr_universal_mount.stl) |
| Phone holder | [8020_phone_holder.stl](stl/8020_phone_holder.stl) |
| Cup holder | [8020_cup_holder.stl](stl/8020_cup_holder.stl) |
| Headphone hook | [8020_headphone_hook.stl](stl/8020_headphone_hook.stl) |
| Cable clip | [8020_cable_clip.stl](stl/8020_cable_clip.stl) |
| Mouse tray | [8020_mouse_tray.stl](stl/8020_mouse_tray.stl) |

Drag the STL into **Bambu Studio**. If GitHub shows a file page instead of downloading, click **Download raw file**.

![Top and side view](preview.svg)

## Print these files

| File | What it is |
| --- | --- |
| [`stl/fit_test_nominal.stl`](stl/fit_test_nominal.stl) | **Print this first.** Stub **22.5 mm** into the wheel, ball groove at **12.3 mm**, open tip stops ~6 mm short of the pogo pins. **M8 × 20 mm** sits in the pad. U-bites + **4× #8**. **3 walls / 15%**. |
| [`stl/moza_qr_universal_mount.stl`](stl/moza_qr_universal_mount.stl) | **The one print.** Round plate. **M8 × 20 mm** in the plate (drop it through the open stub) + 4× #8 around the rim. Ring + 10 ball seats. |
| [`stl/fit_test_tight.stl`](stl/fit_test_tight.stl) / [`stl/fit_test_loose.stl`](stl/fit_test_loose.stl) | Same coupon, ±0.4 mm on the shaft if nominal is off. |
| [`stl/moza_qr_wall_mount_free.stl`](stl/moza_qr_wall_mount_free.stl) | Same universal plate, ring groove, wheel can rotate. |

`moza_qr_wall_mount.stl` and `moza_qr_8020_mount.stl` are copies of the universal file so old links still work.

### 8020 sim-rig kit (same M8 hardware)

![Kit outlines](accessories.svg)

All of these use **M8 × 16–20 mm** bolts and T-nuts — same as the wheel mount now. Print in PETG, no supports.

| File | What it is | On the bed |
| --- | --- | --- |
| [`stl/8020_phone_holder.stl`](stl/8020_phone_holder.stl) | Landscape tray for a phone + case up to **174 × 88 × 16 mm**. Open top (cable out the top). 4× M8 in a plus — vertical pair on an upright, horizontal pair on a dash bar. | Flat back down, walls up |
| [`stl/8020_cup_holder.stl`](stl/8020_cup_holder.stl) | 86 mm ID cup / tumbler, 52 mm deep, drain hole. **Bolt to the top of a 4040 / 2020 beam** so the cup sits upright. | Floor down, opening up |
| [`stl/8020_headphone_hook.stl`](stl/8020_headphone_hook.stl) | J-hook for a headset. 2× M8, 20 mm thick. Side upright, hook into the room. | Flat |
| [`stl/8020_cable_clip.stl`](stl/8020_cable_clip.stl) | One M8, two snap slots for USB / power leads. | Flat |
| [`stl/8020_mouse_tray.stl`](stl/8020_mouse_tray.stl) | Right-side **5 × 5 in** mouse tray. Bolts to the **right face** of a 4040 upright; pad sticks out to your right. Solid deck (no cutouts), no side bumpers, 6 mm bolt plate, triangle gusset. Stick a cloth pad on the deck. **3 walls / 15% infill.** Mirror in the slicer for the left side. | Deck on the bed, bolt plate up |

Phone too tight / too loose: edit `PHONE_INNER_W` / `PHONE_INNER_H` / `PHONE_DEPTH` in `accessories.py`. Cup too snug: raise `CUP_ID`.

Regenerate STLs after editing dimensions:

```bash
python3 generate.py            # wheel mount + accessories, nominal QR fit
python3 generate.py --fit loose
python3 accessories.py         # accessories only
```

Or open `moza_qr_wall_mount.scad` in OpenSCAD and export the wheel mount.

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

The 8020 accessories are lighter. **4 walls / 25% gyroid** is enough for the phone tray, cup, and cable clip. Use **6 walls / 40%** on the headphone hook (it is a cantilever). The mouse tray is a solid 3.2 mm deck on a 6 mm plate: **3 walls / 15% gyroid**. The **fit test** is also **3 walls / 15%** — do not use the wheel-mount 6-wall profile on it or it will take ~50 minutes.

## Fit check

1. Print `fit_test_nominal.stl` with **3 walls / 15% infill**, stub pointing up.
2. Hang it on the rig: drop an **M8 × 20 mm** socket-cap in through the **open stub**. The head sits in a **14 mm pocket in the pad** (3 mm of plastic under the head), then the shaft goes into a 4040 T-nut. Optional **4× #8** at the corners. Back of the pad against the extrusion, stub into the room.
3. Press on (pull the collar if it fights you). It should click **and stay** — if it pops the collar then shoots back off, the lip is not holding. Line one ball with a flap (12 o'clock).
4. If it will not go on at all → print `fit_test_loose.stl` (or in `generate.py` drop `shaft_d` / `groove_d` by 0.4).
5. If it goes on but will not lock → you are not lining the balls up with the seats, or print `fit_test_tight.stl`.
6. When the coupon feels right, print the matching full mount (`generate.py --fit …` if you changed it).

Nominal numbers (sized to the user's wheel: sleeve ID **40.9 mm**, centre well **22.4 mm**, ball ring **12.3 mm** in, pogo-pin plate **28.8 mm** deep):

- Shaft Ø **39.8 mm** (~1.1 mm under the sleeve so PETG can slide in)
- Stub sticks into the wheel **22.5 mm** — long enough to lock on the balls, **~6 mm short of the pin plate** so it cannot mash the gold contacts
- Ball groove centred **12.3 mm** from the pad face (where the ten balls sit), then a **10.2 mm** full-diameter lip to the tip so it clicks and stays
- Tip is **open** (26 mm bore, larger than the 22.4 mm pin well). **M8 × 20 mm** sits in a 14 mm pocket in the pad / plate
- Fit-test pad has U-bites at top / sides / bottom

## Hardware

One print. Pick how you hang it:

**On a wall**

- 1× **M8 × 40–50 mm** socket-cap through the **pad** (drop it in through the open stub) into a **stud**.
- 4× **#8 × 1¼″** wood screws around the rim (anchors if they miss a stud).

**On a sim rig (4040 / 2020)**

- 1× **M8 × 20 mm** socket-cap + T-nut (same as the phone / cup / hook).
- Drop it in through the open stub. The head sits in a **14 mm pocket in the plate** and is hidden once the wheel is on.
- Leave the four #8 holes empty. Snug the M8 so the plate cannot rotate on the bolt.

Why 20 mm: the pad is 8 mm with a 5 mm pocket, so you only need ~3 mm through the plastic plus ~8–10 mm in the T-nut. The phone / cup / hook / clip take the same **M8 × 16–20 mm** bolts.

Do not hang this on a single drywall anchor.

## Use

1. Wall: one **M8 × 40–50 mm** through the pad into a stud, plus four #8 around the rim. Rig: one **M8 × 20 mm** through the pad into a 4040 T-nut. Stub points into the room.
2. Pull the QR collar. Line up one ball with a 12 o'clock seat (a flap on the fit test). Press on until all ten balls drop in and it clicks.
3. To remove: pull the QR collar with both hands and take the wheel off, same as on the base.

If the wheel sits a little rotated, try the next click (there are ten). To shift the seats, change `POCKET_OFFSET_DEG` in `generate.py` and regenerate.

Paddle clearance: the plate is 98 mm across. If paddles kiss the plate, increase `SHAFT_LEN` in `generate.py`.

## Tuning (`generate.py`)

| Constant | Default | What it does |
| --- | --- | --- |
| `FITS["nominal"].shaft_d` | 39.8 | Outer Ø the QR slides over (wheel sleeve measured 40.9) |
| `FITS["nominal"].groove_d` | 33.8 | Deep seat floor Ø (ten ball pockets) |
| `LAND_RECESS` | 2.4 | Ring between the ten seats so all balls catch |
| `GROOVE_FLAT` | 3.8 | How wide the ball floor is (stops the wheel shooting back off) |
| `SHAFT_LEN` | 22.5 | Stub length — balls at 12.3 mm plus a 10.2 mm lip (stops short of the pins) |
| `BALL_RING_FROM_FACE` | 12.3 | Pad face to the ball groove (ring in the wheel) |
| `GROOVE_FROM_TIP` | 10.2 | Lip past the balls |
| `PIN_PLATE_DEPTH` | 28.8 | Electronics plate — stub must stay shorter than this |
| `PLATE_D` / `PLATE_T` | 98 / 8 | Wall plate size |
| `STUB_BORE_D` | 26 | Open bore through the stub (tip is open) |
| `CENTER_HOLE_D` | 8.4 | M8 through the pad / plate |
| `CENTER_CSK_D` | 14 | Pocket in the pad for an M8 socket-cap |
| `PAD_BOLT_WEB` | 3 | Plastic under the bolt head |
| `FIT_SCALLOP_NS_R` / `EW_R` | 11 / 10 | Fit-test U-bites at top-bottom / left-right |
| `POCKET_COUNT` | 10 | Seats matching the ten balls in the wheel QR |
| `POCKET_OFFSET_DEG` | 90 | Rotate the seats (90 = one at 12 o'clock) |

Accessories (`accessories.py`): `PHONE_INNER_W` / `PHONE_INNER_H` / `PHONE_DEPTH`, `CUP_ID`, `HOOK_INNER`.

## License

All rights reserved — see `LICENSE`. You may sell physical prints and digital files of this design. Do not publish the STLs on a public site if you are charging for them. Not affiliated with MOZA Racing.
