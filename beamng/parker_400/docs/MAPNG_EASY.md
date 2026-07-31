# Easy path: full Parker 400 looking good (no MapNG clicking required)

## Good news

You do **not** have to use MapNG yourself for the full course.

I already pulled the **exact Parker 400 map square** (same corners as our 1:1 GPX frame) from **Esri World Imagery** — the same satellite family MapNG uses — and baked it into the level:

- `levels/parker_400/art/terrains/parker400_base_color.png`
- Preview with race line: `import/parker400_base_color_preview.png`

So the full ~126‑mile loop already has matching satellite color + our SRTM hills + official DecalRoad.

---

## Why I can’t “log into MapNG” for you

[mapng.com](https://mapng.com/) runs in **your desktop browser** (Cloudflare + WebGL). I can’t click around inside that UI from here.

What I *can* do (and did): hit the **same data sources** MapNG uses, locked to our exact GPS frame so the race line lines up.

---

## What you do now (easiest)

1. Get the latest `Parker_400_Install.zip` / pull this branch  
2. Run `INSTALL_PARKER_400.bat`  
3. BeamNG → Freeroam → **Parker 400**  
4. F11 → Import Terrain → `import/p400_gpx_scale.preset.json`  
   - **16** m/px · **1500** max height · pos **-32768, -32768**  
5. Terrain Painter → paint **`desert_base`** over the map (satellite is wired as its base)  
6. Soft-paint `course_pack` on the race ribbon if you want  
7. Ctrl+S

---

## If you still want MapNG yourself

MapNG is still useful for **ultra-local** detail (Main Pit ~8×8 km tiles) or USGS 1 m patches.

| Goal | Use |
|---|---|
| Full 126‑mile course looking good | **This package** (already done) |
| Insane detail at Main Pit only | MapNG 8192 tile on start/finish |
| MapNG batch of the whole box | Zip tiles → send to me to stitch |

MapNG single-tile limit reminder: **8192 px ≈ 8 km**, not the whole race.

### Optional MapNG drop (local HD only)

```
%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400\import\mapng_heightmap.png
%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels\parker_400\art\terrains\parker400_base_color.png
```

Or run `scripts\OPEN_MAPNG_DROP_FOLDERS.bat`.

---

## Cheat sheet

1. Install latest Parker 400 ZIP  
2. Import heightmap preset  
3. Paint `desert_base`  
4. Drive  

Satellite for the **exact** course is already in.
