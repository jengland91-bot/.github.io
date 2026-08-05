# Google Earth paint guide (from Josh’s course walk)

Reference from Google Earth screenshots along the CA300 line (Sorrel Trail / Lucerne-area desert).  
Use for **look + materials** — height already comes from SRTM.

## What the photos show

| Look | Where you see it | BeamNG paint / feel |
| --- | --- | --- |
| Light gray / pale packed dirt ribbon | Named trails like **Sorrel Trail**, main race line | Main course DecalRoad / terrain: packed **DIRT** or light gravel |
| Tan–orange open desert | Most freeroam ground | Base terrain: warm desert dirt / sand |
| Lighter branching veins | Dry washes / drainage | Slightly softer **SAND** / silt, maybe a bit lower |
| Darker rocky hills / ridges | Steeper slopes, shadowed mountains | **ROCK** / gravel terrain + rock props |
| Dense dark speckles | Creosote / scrub across flats | Sparse Forest scrub — never on the race ribbon |
| Braided light scratch trails | Heavy OHV areas beside the course | Optional faint side tracks; don’t clutter the race line |
| Quarries / cut banks (light pits) | Local excavated spots | Steep rock/sand walls; keep off main line unless marked |

## Course ribbon rules (from the photos)

1. **Main line = lighter, more defined** than surrounding desert (like Sorrel Trail).
2. Width feels like a **real dirt road / prerunner trail**, not a highway and not a single-track hike path.
3. The line often **follows washes and valley floors**, then climbs onto shelves — SRTM should already carry that.
4. Lots of **side braids** exist in real life; for v1, only build the **official CA300 line** + pit row.
5. Scrub is **everywhere except** on worn trails — paint/forest density high off-road, zero on ribbon.

## Suggested terrain layers (v1)

1. `desert_base` — tan/orange packed dirt (majority)  
2. `course_pack` — lighter gray-tan dirt on CA300 corridor  
3. `wash_silt` — lighter soft sand in wash veins  
4. `rock_slope` — darker rock on steep hills  
5. optional `berm_gravel` — slightly darker edge beside the ribbon  

Match BeamNG **groundmodels** so:
- course_pack → dirt (fast, controllable)
- wash_silt → sand (looser)
- rock_slope → rock/gravel (harsh)

## Prop / Forest notes

- Small desert bushes: even sprinkle on flats  
- Keep **clear** ~ road-width + shoulder on the race line  
- Rock clusters: on hillsides and where danger GPX says rocks/boulders  
- Avoid dumping rocks on the packed ribbon

## Next screenshots that help most

Keep walking the course and grab:
1. Start / finish + pits  
2. A big g-out / drop  
3. A rocky shelf section  
4. A silt wash straight  
5. A ridge/valley speed section  

Name them if you can (`rm12_wash`, `danger_gout`, etc.).

## Do not

- Paste Google Earth imagery as in-game textures  
- Paint the whole desert as one sand type  
- Make the race road asphalt-dark; photos show **light worn dirt**
