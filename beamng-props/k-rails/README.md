# Parker 400 — K-Rails (Jersey Barriers)

Concrete barrier sections for pits, road edges, and course blocking.

## Blank / recolorable

Main blank sections use `krail.png` — overwrite that PNG to change color.

| File | Length |
|------|--------|
| `krail_blank_2m.dae` | 2 m |
| `krail_blank_3m.dae` | 3 m |
| `krail_blank_6m.dae` | 6 m |

## Ready looks

| Style | Lengths |
|-------|---------|
| Concrete | 2 m, 3 m |
| Orange/white stripe | 2 m, 3 m |
| Orange | 2 m, 3 m |
| White | 2 m |
| Dark | 2 m, 3 m |

## Place in BeamNG

Copy `export/dae/` into:

```text
levels/YourParkerMap/art/shapes/props/krails/
```

Place as **TSStatic**. Stack along **+Y** end-to-end to make long walls.

**Collision:** Each DAE includes a dedicated bevel-free `Colmesh_*-1` box (not the visual mesh). In World Editor set **collisionType** = `Collision Mesh`. See `../COLLISION.md`.

## Specs

- Jersey/K-rail profile ~0.81 m tall, ~0.61 m wide at base
- Meters, Z-up, origin at ground at the start end of the section
- Collider: single axis-aligned box (no bevels / no vertex seams for bumper snagging)
