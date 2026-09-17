# Parker 400 — Stakes, Ribbon & Snow Fence

Barrier props for blocking off course sections. **No Blender work needed.**

## What’s included (`export/dae/`)

### Stakes
| File | Use |
|------|-----|
| `stake_wood.dae` | Single wood stake |
| `stake_metal.dae` | Single metal stake |

### Ribbon only (place between stakes — stretches along **+X**)
| Lengths | Styles |
|---------|--------|
| 2m / 3m / 5m | `ribbon_caution_*`, `ribbon_orange_*`, `ribbon_yellow_*` |

Examples: `ribbon_caution_3m.dae`, `ribbon_orange_5m.dae`

### Ready-made stake + ribbon + stake
| File | Use |
|------|-----|
| `stake_ribbon_caution_2m.dae` | Instant 2m caution barrier |
| `stake_ribbon_caution_3m.dae` | Instant 3m caution barrier |
| `stake_ribbon_orange_2m.dae` | Instant 2m orange barrier |
| `stake_ribbon_orange_3m.dae` | Instant 3m orange barrier |

### Snow fence (modular panels)
| File | Use |
|------|-----|
| `snowfence_orange_2m.dae` | Orange plastic-style panel |
| `snowfence_wood_2m.dae` | Wood-slat panel |
| `snowfence_wood_1m.dae` | Short wood panel for tight spots |

Line panels end-to-end along **+X** to fence a long stretch.

## Drop into BeamNG

Copy `export/dae/` into:

```text
levels/YourParkerMap/art/shapes/props/barriers/
```

Place as **TSStatic**.

**Tips**
- Easiest blocker: drop `stake_ribbon_caution_3m` and duplicate along the edge
- Long fence: duplicate `snowfence_orange_2m` in a row
- Custom gaps: place `stake_wood` pairs and span with a ribbon piece

## Specs

- Meters, Z-up, origin at ground (left stake / left end)
- Stakes ≈ 1.15 m tall
- Ribbon height ≈ 0.85 m
- Snow fence ≈ 1.05 m tall panels
