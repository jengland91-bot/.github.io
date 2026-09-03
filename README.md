# Stream Deck Plus ring + hinged 6 Sigma mount

Measured on the Plus (stand off): **139.6 × 135.0 × 29.9 mm**.

Three printed parts, kept light. The **front ring** is four screw corners plus thin straps — keys and dials stay open. The logo end is a **cable gate** so the USB-C plug drops in. The **back plate** is a + rib with four pockets cut out. It **hinges** on a **4040 clamp** so you can tilt the deck, then lock it with an M5 nylock.

```
   [ front ring ]     picture frame around the outside
          │ 4× M3
   [ back plate ]     Plus sits here
          │ M5 hinge — set the angle, tighten
   [ 4040 clamp ]     short clip, 34 mm along the bar
          │ 1× M8 T-nut
     vertical 6 Sigma upright
```

Yes, the hinge needs its own part. That’s what lets it move.

## Print these

| File | What it is |
|---|---|
| [`stls/front_ring.stl`](stls/front_ring.stl) | Outer frame. Rim on the bed. |
| [`stls/back_plate.stl`](stls/back_plate.stl) | Plate + one hinge ear. Plus-face on the bed. |
| [`stls/clamp_4040.stl`](stls/clamp_4040.stl) | Short clip for a **vertical** 4040 + two hinge ears. |
| [`templates/ring-1to1.svg`](templates/ring-1to1.svg) | Paper check at **100% scale**. |

## Hardware

| Qty | Part |
|---|---|
| 4 | M3 × 20 — back plate into the ring posts |
| 1 | M5 × 25 + nylock + 2 washers — hinge. Snug to lock the angle |
| 1 | M8 × 16 + M8 drop-in T-nut (8 mm slot) — front/far face of the upright |

## Print

PETG, 0.20 mm, 4 walls, 40% gyroid, no supports.

- Ring: frame on the bed
- Back plate: Plus-facing side on the bed (hinge sticks up)
- Clamp: back wall on the bed, or on its side

## Assembly

1. Print the SVG at 100%. The white window must miss every key and dial.
2. Take the stand off the Plus.
3. Sit the Plus on the back plate. Drop the USB-C cable through the open gate on the logo end (no threading).
4. Drop the ring over the outside — same gate lines up. Four M3s from the back.
5. Clip the short U onto the **vertical** 4040 upright. One M8 into a T-nut on the far face.
6. One M5 through the three hinge ears. Point the face where you want it, tighten the nylock.

On a vertical bar the hinge nods the face up and down. Loosen, tilt, retighten.

Not an Elgato or 6 Sigma product. MIT licensed.
