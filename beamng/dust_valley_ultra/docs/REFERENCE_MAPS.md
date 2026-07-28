# Reference maps — ideas only (no asset rip)

Inspiration sources named by Josh:

| Folder / map | Role for Dust Valley Ultra |
| --- | --- |
| `lacrmx` | Short-course rhythm in the middle (LiDAR MX / off-road short track feel) |
| `bdr_high_desert` | High-desert openness, silt / wash texture, big hills |
| `echovalley` | Technical valley walls, rock reading, tighter desert lines |
| `cf_baja1k` | Long Baja-style race flow, surface variety, prerunner pace |

**Rule:** study layout language, rock silhouette, material contrast, and course pacing. Do **not** copy meshes, textures, heightmaps, or whole scenes into this mod.

---

## What to borrow as ideas

### From `lacrmx` (short course)
- Tight, readable short loop with clear rhythm: turn → jump/whoop → settle → next hit
- Man-made “prepped” short-course feel in the **middle** of an otherwise natural desert
- Elevation changes that are intentional, not random noise
- Use for: cyan **short course** shaping and jump/berm language

### From `bdr_high_desert` (high desert / silt)
- Broad sightlines and soft silt flats between harder features
- Hills that roll, then suddenly get mean
- Sparse vegetation; terrain does the storytelling
- Use for: overall biome, silt washes beside the long course, hill scale

### From `echovalley` (valley + rocks)
- Rock clusters that look stacked/natural, not evenly sprinkled
- Valley walls that funnel speed without feeling like a pipe
- Mixed rock sizes: big anchors + mid clutter + small break-up
- Use for: east/NW rock trails and valley cut walls

### From `cf_baja1k` (long Baja course)
- Surface variety along one long loop: smooth wide → narrow rough → silt → rock edge
- Long straights that earn the next technical section
- Course stays findable without painting the whole desert as “road”
- Use for: gold **~20 mi long course** pacing and whoops/jump placement

---

## Dust Valley Ultra translation

| Our zone | Steal the *feeling* of | Avoid |
| --- | --- | --- |
| Short course (middle) | `lacrmx` rhythm / prepped track | Copying their exact layout |
| Long course | `cf_baja1k` flow + surface changes | One flat sand ribbon the whole way |
| Silt / washes | `bdr_high_desert` softness | Muddy or over-green look |
| Rock trails | `echovalley` rock reading | Uniform rock spam |
| Hills / valleys | high desert + echo valley | Sharp video-game spikes |

---

## Texture direction (original materials later)

Aim for contrast you can read at Ultra 4 speed:

1. **Packed tan dirt** — main race corridors  
2. **Soft silt / light sand** — washes, whoops shoulders  
3. **Darker gravel berms** — edges so the line pops on minimap + eye  
4. **Broken rock / grey-brown** — side trails only  
5. **Sparse scrub** — never clog the fast line  

When real reference folders are available, note from each map:
- terrain material names + groundmodels
- rock mesh scale mix
- how wide the race ribbon is vs freeroam desert

---

## How to send map files so they can actually be studied

The last upload arrived empty. On desktop, do one of these:

1. **Zip each level folder** (or the whole mod) and attach/upload the `.zip`  
   Example paths often look like:
   - `Documents/BeamNG.drive/mods/unpacked/lacrmx/...`
   - or `.../levels/lacrmx/`
2. Or drop **screenshots** of rocks, silt, valley, and track ribbon from each map
3. Or paste a short note: “from echovalley I like X rocks / from baja I like Y whoops”

What to include if zipping (for analysis only):
- `info.json`
- `main.materials.json` / terrain materials
- a few rock `.dae` paths + material names (we still won’t ship their assets)
- screenshots / minimap if present

---

## Next build passes (when files or notes arrive)

1. Short-course profile inspired by LACR rhythm  
2. Long-course surface “chapters” inspired by Baja 1K pacing  
3. Rock-trail clustering rules inspired by Echo Valley  
4. Silt + hill macro shapes inspired by High Desert  
