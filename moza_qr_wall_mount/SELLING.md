# Selling this mount

You can sell this. It is an original hanger that **fits** MOZA (and other D1-spec) wheels — it is not a copy of those Etsy listings and not a MOZA-branded product.

Two ways to sell:

| What you sell | Why people buy it | Watch-out |
| --- | --- | --- |
| **Physical print** (best fit for a Bambu) | They want it on the wall this week, in a colour | You own QC, shipping, returns |
| **Digital STL** | Impulse buy, they already have a printer | Competes with free files on Printables; once sold, it gets shared |

If this folder is on a **public** GitHub Pages repo, anyone can download the STLs for free. Do not merge the `stl/` files onto the public site if you want to charge for them. Keep this branch private, or sell prints only.

---

## What to call it

Do **not** put “MOZA” in the product name as if you make MOZA gear. Do **not** print their logo on the part.

**Product name (yours):** `D1 QR Steering Wheel Wall Mount`  
**Subtitle:** Compatible with MOZA R3 / R5 / R9 / R12 / R16 / R21 and stock MOZA wheels (ES, RS, CS, GS, FSR)

That “compatible with” wording is the normal, allowed way to say what it fits.

Every listing and the packing slip should include:

> Not affiliated with, endorsed by, or sponsored by MOZA Racing.

Do not use MOZA’s product photos, box art, or another seller’s photos. Shoot **your** print: black PETG, wheel clipped on, then a second shot of the empty mount on a wall or 8020 extrusion.

---

## Etsy listing (paste and edit)

**Title (keep under ~140 characters):**

```
Steering Wheel Wall Mount compatible with MOZA R3 R5 R9 R12 | QR Hanger for Sim Racing Wheel Storage
```

**Tags:** sim racing, steering wheel mount, wheel hanger, wall mount, QR mount, 8020, garage storage, racing wheel, sim rig, PETG

**Description:**

```
Hang your sim-racing wheel on the wall (or your rig) instead of leaving it on a chair.

This is a 3D-printed quick-release hanger. Line up the wheel the same way you do on the base and press on — six ball seats stop it spinning if you bump it. Pull the QR collar to take it off.

Fits:
• MOZA Racing wheels with the stock ball-lock QR (ES, RS, CS, GS, FSR, and others)
• MOZA bases R3, R5, R9, R12, R16, R21 — this hangs the WHEEL, not the base
• Other D1-spec / 50 mm ball-lock QRs (including many Simagic wheels)

You get:
• 1× wall mount, printed in PETG
• Countersunk holes for #8 / 4.5 mm screws (screws not included unless you add the hardware option)
• Optional: 8020/4040 rig version (choose at checkout)

Print: PETG, 6 walls, 40% infill, made on a Bambu Lab printer.

Install into a wall stud or use rated anchors. Do not hang a wheel on a single drywall screw.

Not affiliated with, endorsed by, or sponsored by MOZA Racing.
```

**Variations to offer**

1. Wall mount — black PETG  
2. Wall mount — colour of the month (red / white)  
3. 8020 rig mount — black PETG  
4. Add-on: 4× screws + drywall anchors in a small bag  

**What to charge (US, 2026 ballpark)**

- Printed wall mount: **$18–28** + shipping (those Etsy listings sit in this band)  
- Rig mount: same  
- Hardware add-on: **+$4–6**  
- Digital STL only: **$8–12** if you go that route  

Filament for one wall mount is a few dollars of PETG and well under two hours on a Bambu. The margin is in finishing, photos, and not having failed parts.

---

## Print every customer unit the same way

Reject a part rather than ship a weak one. A dropped carbon wheel costs more than a reprint.

| Setting | Ship this |
| --- | --- |
| Material | PETG (Bambu PETG Basic or equivalent). Not PLA for sale units. |
| Colour | Black as the default SKU |
| Layer | 0.20 mm |
| Walls | 6 |
| Top/bottom | 5 |
| Infill | 40% gyroid |
| Supports | None |
| Brim | 5 mm, then knife it off clean |
| Orientation | Plate on the bed, stub up |

**QC before it goes in the box**

1. No layer splits on the stub. Flex it — it should not creak.  
2. Groove is clean (no stringing in the channel).  
3. Screw holes are open; countersinks are round.  
4. Snap **your** wheel (or a QR dummy) on. It must click and not slide off when you hold the plate vertical and give it a firm tug.  
5. Collar still releases. If it welds on, that unit is scrap.  
6. Wipe, bag, include the care card.

If a customer’s wheel is unusually tight, reprint that order on the **loose** fit (`python3 generate.py --fit loose`) rather than arguing.

---

## Care card (print on a 4×6 or slip in the bag)

```
D1 QR WHEEL MOUNT

1. Screw the plate to a stud or use rated anchors. Four screws. Stub points into the room.
2. Press the wheel on until it clicks. No need to line up the balls.
3. To remove: pull the QR collar with both hands and take the wheel off.

PETG printed part. Do not yank the rim. Do not hang on a single drywall screw.
Questions? (your email / Etsy messages)

Not affiliated with MOZA Racing.
```

---

## Photos that sell

1. Hero: wheel hanging on a dark wall, slightly off-centre, paddles visible.  
2. Detail: QR collar seated on the stub, groove visible.  
3. Install: back of the plate and the four screw holes.  
4. Scale: in a hand, next to a tape or a screw.  
5. Rig shot if you sell the 8020 version.

Buyers of the Etsy listings you sent are shopping “MOZA wheel storage.” Your photos should answer: it clicks on, it looks clean, it will not drop the wheel.

---

## Files for each SKU

| Sell this | File |
| --- | --- |
| Wall mount | `stl/moza_qr_wall_mount.stl` |
| Rig / 8020 | `stl/moza_qr_8020_mount.stl` |
| Digital download zip | both STLs + this care card + “compatible with MOZA…” one-pager |

Do not include `generate.py` in a cheap digital listing unless you want people cloning your shop.
