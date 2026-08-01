# Parker 400 — Blank Inflatable Arch (recolor + logo)

Drive-through start/finish/checkpoint gate. **Everything is blank / swappable** so you can change tube color, block color, and logo.

## Main file

```text
export/dae/arch_blank.dae
```

Uses these three textures (edit any of them):

| Texture | Controls |
|---------|----------|
| `arch_tube.png` | Legs, arms, feet color |
| `arch_block.png` | Center block color |
| `arch_logo.png` | Front & back logo panel |

**Clearance:** ~7 m wide × ~4.6 m tall.

**Collision:** Split into three convex boxes (left leg, right leg, header) so vehicles can drive through. Never one concave hull. Set **collisionType** = `Collision Mesh`. See `../COLLISION.md`.

**LODs:** `_a800` / `_a200` / `_a50` billboard + cull. Base pivot at ground. See `../GEOMETRY_LODS.md`.

## How to customize

### Change colors
1. Open `arch_tube.png` or `arch_block.png` in Photoshop / GIMP  
   (or copy a preset over them — see below)
2. Fill with your color / save
3. Keep the **same filename**

### Add a logo
1. Open `logo_templates/paint_logo.png`
2. Paste your logo in the dashed box
3. Export as PNG **1024×512**
4. Overwrite `export/dae/arch_logo.png`

### Quick color presets (copy over the three masters)
In `export/dae/` you’ll find ready solids:

- Tubes: `arch_tube_yellow.png`, `arch_tube_orange.png`, `arch_tube_white.png`, `arch_tube_black.png`, `arch_tube_red.png`, `arch_tube_blue.png`
- Block: `arch_block_white.png`, `arch_block_black.png`, `arch_block_gray.png`
- Logo base: `arch_logo_white.png`, `arch_logo_black.png`, `arch_logo_gray.png`

Example — yellow tubes + black block + black logo face (like your photo):

```text
copy arch_tube_yellow.png  →  arch_tube.png
copy arch_block_black.png  →  arch_block.png
copy arch_logo_black.png   →  arch_logo.png
```

Then paint your brand onto `arch_logo.png`.

## Optional presets (already assembled)
If you want a starting look without copying files:

- `arch_preset_yellow_black.dae`
- `arch_preset_orange_black.dae`
- `arch_preset_white_navyish.dae`

These still use swappable PNGs next to them — same idea, different starting filenames.

## Drop into BeamNG

Copy `export/dae/` into:

```text
levels/YourParkerMap/art/shapes/props/arch/
```

Place `arch_blank.dae` as a **TSStatic**. Duplicate the folder for start/finish/checkpoint if each needs different logos.
