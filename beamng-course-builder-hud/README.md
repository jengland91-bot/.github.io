# Course Builder HUD (BeamNG.drive)

Clean freeroam **UI App** for laying out courses with props, rocks, and clutter — **without opening World Editor**.

Aim the camera → pick from the library → **Place**. Select placed items to rotate, scale, nudge, duplicate, or delete. Save layouts and reload them later.

## Features

- Categories: **Course**, **Rocks**, **Nature**, **Clutter**, **Static**, **Found**
- Physics props (cones, barriers, tire walls, barrels, …)
- Rocks via stock / installed rock packs + **Scan for rocks / props**
- Static mesh rocks (TSStatic) when mesh paths exist on the map
- Edit tools: yaw snap, scale, nudge pad, move-to-aim, duplicate, delete
- Save / Load JSON layouts
- **Save + Prefab guide** for turning a layout into permanent map content in F11

## Install

1. Put the mod in your BeamNG unpacked mods folder so it looks like:

   ```
   Documents/BeamNG.drive/<version>/mods/unpacked/courseBuilderHud/
     scripts/courseBuilderHud/modScript.lua
     lua/ge/extensions/courseBuilderHud.lua
     ui/modules/apps/CourseBuilderHud/...
   ```

   Or run `./pack-mod.sh` and drop the zip into `mods/`.

2. Enable the mod, load **freeroam**.
3. **Esc → UI Apps → Add App → Course Builder**.

## Rocks

Rocks work best as **spawnable props** (same family as Esc → Vehicles → Props → Rocks & Boulders).

1. Open the **Rocks** tab and try **Rocks & Boulders**.
2. If nothing spawns, click **Scan for rocks / props** — it searches installed models and fills the **Found** tab.
3. **Static** tab tries map mesh rocks (West Coast paths). Those only work if that mesh exists on the loaded level; use Scan / physics rocks when static fails.

## Editing

| Control | What it does |
| --- | --- |
| Place | Spawns selected library item at camera aim |
| Placed list | Click to select for editing |
| ⟲ ⟳ | Rotate (uses snap) |
| Scale − / + | Scale selected (best on statics) |
| Nudge pad | Move selected relative to facing |
| Move to aim | Teleport selected to where you look |
| Duplicate / Delete | Copy or remove selected |
| Save / Load | JSON in `settings/courseBuilderHud/` |

## Permanent map content

This tool is for **fast freeroam layouts**. To bake into a level:

1. Build / Load the layout.
2. Click **Save + Prefab guide** (writes layout + a short checklist).
3. **F11** → select objects → **Make selection a Prefab** → save under the level’s `art/prefabs`.

Terrain sculpt, road painting, and full lighting still need World Editor.

## Customize catalog

Edit `lua/ge/extensions/courseBuilderHud.lua` → `BASE_CATALOG`.

- `kind = "vehicle"` + `model = "folder_name"` for props
- `kind = "static"` + `shape = "path/to/mesh.dae"` for static meshes
