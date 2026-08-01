# Parker 400 — Inflatable Drive-Through Arch

Start / finish / checkpoint gate cars can drive under. Center panel is **blank for logos**.

## Ready to place (`export/dae/`)

| File | Look |
|------|------|
| `arch_yellow_blank.dae` | Yellow tubes + black logo panel (like your photo) |
| `arch_orange_blank.dae` | Desert orange tubes + black logo panel |
| `arch_white_blank.dae` | White tubes + navy logo panel |
| `arch_yellow_logo_white.dae` | Yellow tubes + white logo panel |

**Clearance:** ~7 m wide × ~4.6 m tall under the arch (fits BeamNG cars / Ultra4-size rigs).

## Add a logo

1. Open `logo_templates/logo_template_black.png` (or white/navy) in Photoshop / GIMP
2. Paste your logo inside the dashed box
3. Export PNG (**1024×512**)
4. Overwrite the matching texture next to the DAE, e.g.:

```text
export/dae/arch_logo_blank_black.png
```

Keep the **same filename** so the arch still finds it.  
Duplicate the whole DAE + texture set if you want several branded arches (start, finish, checkpoint).

## Drop into BeamNG

Copy `export/dae/` into:

```text
levels/YourParkerMap/art/shapes/props/arch/
```

Place as **TSStatic**. Drive direction is along **Y** through the opening (rotate in World Editor as needed).

## Specs

- Meters, Z-up, origin at ground center
- Inflatable-style round tubes + beveled center block
- Logo plates on **front and back** of the center block
