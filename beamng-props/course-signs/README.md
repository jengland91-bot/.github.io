# Parker 400 — Course Signs Kit

BeamNG-ready course markers. Portrait plates matching desert-race style:

- **"ILLEGAL TO REMOVE !"** header
- **Lime green** hard turn arrows / **yellow** straight & TURN AHEAD
- Bottom championship-style logo row (layout placeholders)

## What’s included

### Arrow markers (WRONG WAY on the back)
| File | Meaning | Plate |
|------|---------|-------|
| `arrow_straight.dae` | Straight ahead | Yellow + up arrow |
| `arrow_slight_left.dae` / `arrow_slight_right.dae` | Mild bend | Lime |
| `arrow_turn_left.dae` / `arrow_turn_right.dae` | Hard 90° turn | Lime |
| `arrow_double_left.dae` / `arrow_double_right.dae` | Double chevron turn | Lime |
| `arrow_triple_left.dae` / `arrow_triple_right.dae` | Triple chevron turn | Lime |

Arrow backs: red/white **WRONG WAY**.

### Standalone warning signs
| File | Meaning |
|------|---------|
| `turn_ahead.dae` | Yellow **TURN AHEAD** |
| `sign_wrong_way.dae` | Dedicated wrong-way sign |
| `sign_danger_x.dae` | Yellow **X / DANGER** |

## Drop into BeamNG

1. Copy:

```text
beamng-props/course-signs/export/dae/
```

into your map, e.g.:

```text
levels/YourParkerMap/art/shapes/props/course_signs/
```

2. World Editor (`F11`) → place as **TSStatic**
3. Face the arrow toward oncoming racers (back shows WRONG WAY the other way)

## Specs

- Meters, Z-up
- Post ≈ **1.65 m**, portrait sign ≈ **0.40 × 0.68 m**
- Origin at ground under the post
- Front faces **-Y**

Also included: rebuild via `../rebuild_with_collision.py` and `generate_textures.py`.
