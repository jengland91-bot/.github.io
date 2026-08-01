# Course Builder HUD (BeamNG.drive)

A freeroam **UI App** for laying out course props **without opening World Editor (F11)**.

Look with the camera → pick a prop on the HUD → **Place**. Undo, rotate yaw, clear, and save/load layouts.

## Is this possible?

Yes. BeamNG UI Apps can call Lua via `bngApi.engineLua`, and Lua can spawn props with `core_vehicles.spawnNewVehicle` at a camera raycast hit. That is enough for quick course mocking in freeroam.

| Approach | Good for | Limitation |
| --- | --- | --- |
| **This HUD** (spawned props) | Fast cones / barriers / tire walls while driving around | Session objects; not a permanent map edit unless you save layout or convert in World Editor |
| **World Editor + Prefabs** | Permanent level content | Slower; full editor UI |
| **Scene Manager** (community) | Broader scene staging | Separate mod |

## Install

1. Copy the folder `beamng-course-builder-hud` into your BeamNG mods unpacked folder, **or** zip its **contents** (not the outer folder name alone — the zip root must contain `scripts/`, `lua/`, `ui/`):

   ```
   Documents/BeamNG.drive/<version>/mods/unpacked/courseBuilderHud/
     scripts/courseBuilderHud/modScript.lua
     lua/ge/extensions/courseBuilderHud.lua
     ui/modules/apps/CourseBuilderHud/...
   ```

2. Enable the mod in the in-game Repository / Mods menu (unpacked mods usually auto-load).

3. Load a freeroam map.

4. Press **Esc → UI Apps → Add App → Course Builder**.

5. Resize / dock the app like any other HUD widget.

## How to use

1. Free-look or drive so the camera aims at the ground where you want the prop.
2. Select a prop in the list (cone, barrier, tire wall, etc.).
3. Set yaw with ⟲ / ⟳ (snap 5° / 15° / 45° / 90°).
4. Click **Place**.
5. **Undo** removes the last prop. **Clear** removes all props tracked by this app.
6. **Save** writes `settings/courseBuilderHud/<name>.json` in your user folder. **Load** respawns that layout.

## Prop catalog

Default list uses stock spawnable models (`cones`, `barrels`, `cardboard_box`, `barrier`, `tirewall`, …). Exact names vary by game version — if something fails to spawn, you will get a toast and a log line under `courseBuilderHud`.

Edit the `PROP_CATALOG` table in:

`lua/ge/extensions/courseBuilderHud.lua`

Add entries with the same model name you would pick from the vehicle/prop spawner.

## Saving permanently into a map

This HUD is for **fast layout**, not replacing World Editor:

1. Build the course with the HUD (or Load a saved JSON).
2. Open **F11**, select the spawned objects in the Scene Tree (`Spawned Vehicles` / clones).
3. **Make selection a Prefab** and save under your level’s `art/prefabs`.
4. Or keep using **Save/Load** in this app for temporary / replayable freeroam courses.

## Files

```
beamng-course-builder-hud/
  scripts/courseBuilderHud/modScript.lua
  lua/ge/extensions/courseBuilderHud.lua
  ui/modules/apps/CourseBuilderHud/
    app.json
    app.js
    app.html
    app.png
```

## Notes

- Works best in **freeroam**.
- Placed props are physics objects (same family as Esc → Vehicles props), so cars can hit them.
- If a model name is wrong for your BeamNG version, remove or fix that catalog entry.
- Collision / multiplayer sync is not handled; this is a single-player layout tool.
