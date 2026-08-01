# Parker 400 — Tire Stacks

| File | Description |
|------|-------------|
| `tire_single.dae` | One tire |
| `tire_stack_2` … `tire_stack_6` | Stacks 2–6 high |
| `tire_row_3.dae` | Three tires in a row (low barrier) |

Copy `export/dae/` into your map props folder. Place as **TSStatic**.

**Collision:** Each stack uses one 8-sided `Colmesh_*-1` cylinder (not the torus visual). Rows use one cylinder per tire. Set **collisionType** = `Collision Mesh`. See `../COLLISION.md`.

**LODs:** `_a800` / `_a200` / `_a50` billboard. See `../GEOMETRY_LODS.md`.
