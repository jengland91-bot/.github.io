# Parker 400 — Blank Feather Flags

Teardrop / feather flags like trackside sponsor banners. **Blank faces** so you can add your own logos.

## Ready to place

`export/dae/`

| File | Color |
|------|-------|
| `featherflag_blank_orange.dae` | Orange |
| `featherflag_blank_black.dae` | Black |
| `featherflag_blank_white.dae` | White |
| `featherflag_blank_navy.dae` | Navy |

~3.6 m tall cloth + black pole + ground spike. Origin at ground.

## Put a logo on them

1. Open a template from `logo_templates/` in Photoshop / GIMP / Paint.NET  
   (dashed box = safe logo area)
2. Paste your logo (vertical logos work best, like the Maxxis / TKM ones)
3. Hide/delete the guide lines
4. Export as PNG, **512×2048** (or same aspect)
5. Replace the matching texture next to the `.dae`, e.g.:

```text
export/dae/flag_blank_orange.png  ← overwrite with your logo version
```

6. Keep the **same filename** so the DAE still finds it

Or duplicate a DAE + PNG pair and rename both if you want multiple logo versions.

## Drop into BeamNG

Copy `export/dae/` into:

```text
levels/YourParkerMap/art/shapes/props/featherflags/
```

Place as **TSStatic**. Duplicate around start/finish, pits, spectator areas.

## Specs

- Meters, Z-up
- UV mapped for a tall logo banner
- Cloth thickness is thin (visual prop; usually no need for heavy collision)
