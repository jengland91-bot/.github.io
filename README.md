# Stream Deck Plus ring + 6 Sigma back plate

Two printed parts. The **front ring** is only a frame around the outside of the [Stream Deck Plus](https://www.elgato.com/us/en/p/stream-deck-plus) — keys, touch strip, and dials stay open. Four M3 screws hold that ring to a **back plate**. The Plus sits in the pocket between them. The back plate bolts to a 6 Sigma (or any 40-series) rail with two M8 T-nuts.

```
        keys / dials open
     ┌─────────────────┐
     │ ███████████████ │  front ring (picture frame)
     │ █             █ │
     │ █  Stream     █ │
     │ █  Deck Plus  █ │
     │ █             █ │
     │ ███████████████ │
     └────────┬────────┘
              │ 4× M3
     ┌────────┴────────┐
     │    back plate   │
     │    2× M8 slots  │
     └────────┬────────┘
              │ T-nuts
         6 Sigma 4040
```

## Print these

| File | What it is |
|---|---|
| [`stls/front_ring.stl`](stls/front_ring.stl) | Outer frame. Rim on the bed, walls up. |
| [`stls/back_plate.stl`](stls/back_plate.stl) | Plate + M8 pad. Pad on the bed. |
| [`templates/ring-1to1.svg`](templates/ring-1to1.svg) | Paper check. Print at **100% scale**, lay it on the Plus. The grey band is the frame; nothing in the white window should cover a key or dial. |

If the ring is tight or the window clips a key, edit `LIP`, `FACE_H`, or `CLEAR` in [`cad/params.py`](cad/params.py) and run `python3 cad/generate.py`.

## Hardware

| Qty | Part |
|---|---|
| 4 | M3 × 20 socket cap (from the back into the ring posts) |
| 2 | M8 × 16 + M8 drop-in T-nuts, 8 mm slot (6 Sigma already has these) |
| 2 | Optional: original M3 × 8 stand screws into the slotted holes |

## Print

PETG on the rig. 0.20 mm layers, 4 walls, 30–40% gyroid. No supports.

- Ring: visible face (the frame) on the bed
- Back plate: M8 pad on the bed

## Assembly

1. Print the SVG at 100% and confirm the window clears the controls.
2. Take the stand off the Plus (two Phillips screws). Keep them if you want the optional M3 slots.
3. Sit the Plus on the back plate, USB-C toward the notch (logo end).
4. Drop the ring over the face. It only wraps the outside.
5. Four M3 × 20 from the back plate into the ring corners.
6. Two M8 through the pad into T-nuts on a 40 mm face of the chassis — shifter arm, wheel-deck upright, or a spare 4040.

Not an Elgato or 6 Sigma product. MIT licensed.
