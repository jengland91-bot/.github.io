# Install Parker 400 on BeamNG.drive **0.39 / 0.39.1**

After the 0.39 update, maps often **do not show in Freeroam** if you only copy folders into `levels\`.  
Use a **mod zip** in the `mods` folder instead. That is the reliable method.

---

## 1. Download the mod zip

Get this file only:

**[parker_400.zip](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip)** (~70 MB)

Do **not** unzip it yet.

---

## 2. Open your BeamNG user folder

1. Open the **BeamNG.drive** launcher (or start the game).
2. Click **Manage User Folder**.
3. Click **Open**.

You should land in something like:

`C:\Users\YOURNAME\AppData\Local\BeamNG\BeamNG.drive\current\`

(That is correct for 0.39. Older docs that said `Documents\BeamNG.drive` are outdated.)

---

## 3. Put the zip in `mods`

Inside that folder you should see **`mods`**.

1. Open **`mods`**.
2. Copy **`parker_400.zip`** into `mods` — leave it as a **.zip** (do not extract).

Correct:

```
...\BeamNG.drive\current\mods\parker_400.zip
```

Wrong (common mistake — Freeroam will stay empty):

```
...\BeamNG.drive\current\levels\parker_400\   ← loose copy often ignored in 0.39
```

---

## 4. Enable the mod + restart

1. In the launcher or in-game: **Mods** / Repository.
2. Find **Parker 400** / `parker_400` and make sure it is **enabled**.
3. Fully quit BeamNG and start again.

---

## 5. Find it in Freeroam

1. **Play** → **Freeroam**.
2. Look for **Parker 400**.
3. If the list is long, use the search box and type `parker`.

If it still does not appear:

1. Confirm the zip path is exactly `mods\parker_400.zip` under `current\`.
2. Open the zip — the first folder inside must be **`levels`**, then `parker_400`, then `info.json`.
3. Delete any old loose copy at `levels\parker_400` (can confuse things).
4. Check `settings\cloud\mods.json` or the in-game mod list that it is not disabled.
5. Look in `logs\` for a line mentioning `parker_400` after launch.

---

## Optional: unpacked mod (same result)

If you prefer a folder instead of a zip:

```
...\current\mods\unpacked\parker_400\levels\parker_400\info.json
```

Copy the **contents** of the install package so `levels\parker_400` sits under `mods\unpacked\parker_400\`.

---

## After it loads once

1. Press **F11** → World Editor.
2. **File → Import** → `levels/parker_400/import/p400_gpx_scale.preset.json`
   - Heightmap: **4096**, meters/px: **16**, max height: **1500**
3. Paint material **`desert_base`** (satellite texture) over the terrain.
4. **Ctrl+S**.

Then race the DecalRoad course (orange line in the editor).

---

## Quick checklist

| Step | Done? |
|------|--------|
| Downloaded `parker_400.zip` | ☐ |
| Opened user folder via launcher → `current\` | ☐ |
| Zip is in `mods\` (not extracted into `levels\`) | ☐ |
| Mod enabled | ☐ |
| Fully restarted | ☐ |
| Freeroam → search “parker” | ☐ |
