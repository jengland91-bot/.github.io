# Course Builder HUD (BeamNG.drive)

Clean freeroam **UI App** for laying out courses with props, rocks, and clutter — **without opening World Editor**.

Aim the camera → pick from the library → **Place**. Select placed items to rotate, scale, nudge, duplicate, or delete. Save layouts and reload them later.

## Features

- Categories: **Favs**, Course, Rocks, Nature, Clutter, Static, Found
- Physics props + rock scan + static meshes
- Edit: yaw snap, scale, nudge, move-to-aim, duplicate, delete
- **Hotkeys** for place / undo / rotate / delete / paint / grid / ghost
- **Paint mode** — drop props along your aim path with spacing
- **Grid snap** — align placements to 0.5 / 1 / 2 / 5 m
- **Favorites** — star props; open the Favs tab
- **Ghost preview** — sphere + facing arrow at the aim point
- **Random yaw / scale** — natural rock fields
- Save / Load JSON + Prefab guide for F11 permanence

## Install

1. Put the mod in your BeamNG unpacked mods folder so it looks like:

   ```
   Documents/BeamNG.drive/<version>/mods/unpacked/courseBuilderHud/
     scripts/courseBuilderHud/modScript.lua
     lua/ge/extensions/courseBuilderHud.lua
     lua/ge/extensions/core/input/actions/courseBuilderHud.json
     settings/inputmaps/keyboard_courseBuilderHud.json
     ui/modules/apps/CourseBuilderHud/...
   ```

   Or run `./pack-mod.sh` and drop the zip into `mods/`.

2. Enable the mod, load **freeroam**.
3. **Esc → UI Apps → Add App → Course Builder**.
4. If hotkeys don’t show up, check **Options → Controls** for “Course Builder” actions (zipped mods bind more reliably than unpacked on some versions).

## Hotkeys (defaults)

| Key | Action |
| --- | --- |
| **U** | Place |
| **I** (hold) | Paint along aim |
| **Alt+I** | Toggle paint mode |
| **[** / **]** | Rotate left / right |
| **Alt+Z** | Undo |
| **Alt+Backspace** | Delete selected |
| **Alt+G** | Toggle grid snap |
| **Alt+H** | Toggle ghost preview |

Rebind anytime in Controls.

## Paint + grid

1. Pick a prop (cones work great).
2. Set **Spacing** (e.g. 3 m).
3. Turn on **Paint** or hold **I**, then look/drive along the line you want.
4. Optional: turn on **Grid** for straight barrier rows.

## Rocks

1. Open **Rocks** and try **Rocks & Boulders**.
2. If nothing spawns, click **Scan for rocks / props** → use **Found**.
3. Star favorites with ★ for quick access.

## Permanent map content

Build / Load a layout → **Save + Prefab guide** → **F11** → select objects → Make Prefab → save under the level’s `art/prefabs`.

Terrain, full roads, and lighting still need World Editor.

## Customize

Edit `lua/ge/extensions/courseBuilderHud.lua` → `BASE_CATALOG`.

- `kind = "vehicle"` + `model = "folder_name"`
- `kind = "static"` + `shape = "path/to/mesh.dae"`
