# Stream Deck Plus cockpit faceplate + 6 Sigma mount

A 3D-printed **faceplate** for the [Elgato Stream Deck Plus](https://www.elgato.com/us/en/p/stream-deck-plus) that also **bolts to a 6 Sigma sim cockpit** (any 40-series extrusion: 4040 / 4080 / 40120).

It is four printed parts plus hardware you already have on a 6 Sigma rig: M8 T-nuts and the two original stand screws.

```
  driver
    │
    ▼
 ┌──────────────┐
 │   FACEPLATE  │  covers the bezel, keys / touch / dials stay open
 │  8 keys      │
 │  touch strip │
 │  4 dials     │
 └──────┬───────┘
        │ Stream Deck Plus (stand removed)
 ┌──────┴───────┐
 │    CRADLE    │  tray + original M3 stand screws + zip-tie slots
 └──────┬───────┘
        │ M5 hinge (set the angle, tighten)
 ┌──────┴───────┐
 │  CLAMP 4040  │  U-channel, two M8 into drop-in T-nuts
 └──────┬───────┘
        │
   6 Sigma 40-series rail
```

## What to print

| File | What it is | First print? |
|---|---|---|
| [`stls/fit_gauge.stl`](stls/fit_gauge.stl) | 1.2 mm 1:1 cutout plate | **Yes — print this first** |
| [`templates/faceplate-1to1.svg`](templates/faceplate-1to1.svg) | Paper template, print at **100% scale** | Also yes |
| [`stls/faceplate.stl`](stls/faceplate.stl) | Bezel overlay with a snap skirt | After the gauge fits |
| [`stls/cradle.stl`](stls/cradle.stl) | Tray the Plus drops into | After the gauge fits |
| [`stls/clamp_4040.stl`](stls/clamp_4040.stl) | 40-series U-clamp | Anytime |

If the gauge openings do not line up with your unit, change the millimetre values in [`cad/params.py`](cad/params.py) and run `python3 cad/generate.py`. Key pitch, dial size, and M3 spacing are the usual tweaks.

## Hardware

| Qty | Part | Where it goes |
|---|---|---|
| 2 | **M8 × 16** button-head or socket-cap (M8 × 20 if the wall stacks up thick) | Clamp → T-nut |
| 2 | **M8 drop-in / spring T-nuts**, 40-series 8 mm slot | 6 Sigma extrusion |
| 1 | **M5 × 25** socket + nylock + 2 washers | Hinge pivot |
| 2 | Original **M3 × 8** Phillips from the Stream Deck stand | Optional, cradle floor |
| 1–2 | 4 mm zip ties | Optional extra retention |

6 Sigma ships M8 T-nuts and M8 × 16 screws with the chassis. You should not need a special hardware kit.

## Print settings

PETG is the right material on a cockpit (heat, vibration, UV through a window). PLA will work for a fit check.

| Setting | Faceplate / gauge | Cradle / clamp |
|---|---|---|
| Layer height | 0.16 mm | 0.20 mm |
| Perimeters | 4 | 4 |
| Infill | 25% gyroid | 40% gyroid |
| Supports | None | None if oriented as exported |
| Bed | Face / gauge **flat, visible face down** | Cradle **floor down**. Clamp **back wall down** or on its side so layers run across the M8 bosses |

Mirror `cradle.stl` and `clamp_4040.stl` in the slicer for a left-side mount.

## Assembly

1. Print the SVG at 100% (no “fit to page”) or print `fit_gauge.stl`. Lay it on the Plus. The eight keys, touch strip, and four dials should sit inside the openings with a little air around them.
2. Pull the four **dial caps** straight off (they are meant to come off — Elgato sells replacements).
3. Unscrew the two Phillips screws in the stand and take the stand off. Keep the screws.
4. Drop the faceplate onto the Plus, then press the dial caps back on. The caps retain the plate.
5. Seat the Plus in the cradle, USB-C toward the hinge / cable slot. Optionally run the original M3 screws through the slotted holes in the floor. Add zip ties through the side slots if you want a belt.
6. Slide the clamp onto a **40 mm face** of any 6 Sigma extrusion (upright, shifter arm, or a spare 4040). Drop two M8 T-nuts in the slot, bolt through the clamp.
7. Join cradle and clamp with the M5 bolt. Point the face at your hand, snug the nylock.

### Where it goes on a 6 Sigma

The clamp is a U that hugs a 40 × 40 mm section, so it fits:

- **Shifter / handbrake arm** (the usual button-box spot, right of the wheel)
- **Wheel-deck side upright** (inboard face, so the Plus faces you)
- **Any spare 4040** you bolt on as a dedicated accessory rail
- **4080 / 40120** — clamp onto one 40 mm face, same M8 T-nuts

On a **vertical** bar the hinge swings the deck toward / away from you. On a **horizontal** bar it nods the viewing angle.

## Regenerating STLs

Python 3 with `numpy` (already listed in `requirements.txt`):

```bash
python3 cad/generate.py              # all parts
python3 cad/generate.py --part faceplate
```

Official Elgato numbers used as anchors: overall 140 × 138 × 110 mm (with stand), touch strip **108 × 14 mm**, stand screws **M3 × 8**. Housing depth, key pitch, dial diameter, and M3 spacing are estimated from those plus the XLR Dock envelope, then given clearance. That is why the paper gauge exists.

This is not an Elgato or 6 Sigma product.

## License

STL files and source: [MIT](LICENSE). Stream Deck and 6 Sigma names belong to their owners.
