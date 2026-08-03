# How to load the Parker course in Google Earth, MapNG, and other apps

## File you need

```
beamng/parker_400/source/reference/p400/parker400_mapng_frame.kml
```

Also useful:
```
beamng/parker_400/source/reference/p400/2026_Parker_400_CTUTV_Final_Racer_File.gpx
beamng/parker_400/source/reference/p400/2026_Parker_400_CTUTV_Final_Racer_File.kml
```

Where to get them on your PC:
- From the GitHub repo / PR download, or
- Inside `Parker_400_Install.zip` → look under `levels\parker_400\` won’t have the KML — use the repo folder:
  `beamng\parker_400\source\reference\p400\`

---

## Google Earth Pro (desktop) — easiest KML load

1. Install / open **Google Earth Pro**
2. **File → Open**
3. Browse to `parker400_mapng_frame.kml` → Open
4. In the left Places panel, check the file so it’s visible
5. Double‑click the item name to zoom to it

You should see:
- a box (our BeamNG map square)
- the race line
- corner pins

**To save a satellite photo of that box:**  
look straight down → **File → Save → Save Image**

---

## Google Earth (web) — earth.google.com

1. Go to [earth.google.com](https://earth.google.com/web/)
2. Sign in (needed for projects)
3. Left menu → **Projects** → **New project** → **Import KML file from computer**
4. Pick `parker400_mapng_frame.kml`
5. Click the project / placemark to fly there

If import is missing on your account UI: open the full racer file the same way  
(`2026_Parker_400_CTUTV_Final_Racer_File.kml`) — same course.

---

## MapNG — mapng.com (usually NO KML import)

MapNG is mainly **search + draw area**. It often **cannot open your KML**. That’s OK.

### Do this instead

1. Open [mapng.com](https://mapng.com/) on a **PC** browser  
2. In the search box paste:

```
34.086139, -113.897239
```

3. Switch map layer to **Satellite** if available  
4. Zoom out until you cover roughly from the Colorado River (west) across the desert loop (east)  
5. Use these corners as a checklist — your MapNG box should include all of them:

| Corner | Copy this |
|---|---|
| SW | `33.791781, -114.252473` |
| SE | `33.791781, -113.544084` |
| NW | `34.380498, -114.252851` |
| NE | `34.380498, -113.539519` |

6. Optional double‑check: keep Google Earth open with the KML beside MapNG and match the same desert / farm fields / river

### Reminder
One MapNG tile maxes around **8×8 km**. For the **full** Parker loop, use our installed BeamNG map (already matched). Use MapNG for HD pits or batch tiles.

---

## Other programs that help (including onX)

These are great for **viewing / checking** the GPX. Only some help BeamNG terrain.

| App | Load GPX/KML? | Best for | Helps BeamNG? |
|---|---|---|---|
| **onX Offroad** | Yes (import GPX/track) | Seeing the course on sat/topo like you ride | Great for **checking** the line; not a BeamNG heightmap exporter |
| **Google Earth / Earth Pro** | Yes | Satellite screenshots, verify area | **Color/skin** yes; hills no |
| **MapNG** | Search/coords (not KML) | Heightmap + satellite for BeamNG | **Yes** — main terrain tool |
| **QGIS** (free) | Yes | Exact exports, Esri/NAIP | **Yes** — advanced |
| **USGS National Map** | Draw box | Official US aerial / DEM downloads | **Yes** |
| **Gaia GPS** | Yes | Phone/tablet track review | Check only |
| **Garmin BaseCamp / Explore** | Yes | GPX editing, waypoints | Check / edit GPX |
| **CalTopo** | Yes | Planning overlays, print/export | Check + some export |
| **SAS.Planet** | Overlays | Bulk satellite tile download | Satellite yes |
| **ExpertGPS** | Yes | You already used this (GPX creator) | Check / edit |
| **Lowrance / chart plotter** | USR/GPX | In-rig race files | Source files only |

### onX Offroad — how to use it here
1. Open onX Offroad (app or web if available on your plan)
2. Import track / GPX: use  
   `2026_Parker_400_CTUTV_Final_Racer_File.gpx`
3. Confirm it looks like the Parker loop you raced
4. Use sat + topo layers to study washes, pits, dangers
5. **Don’t expect onX to export a BeamNG map** — it’s for navigation/reference  
6. If onX can export a screenshot or GPX again, that’s enough to verify you’re in the right desert

### Good combo
- **onX / Google Earth** → confirm course + take screenshots  
- **MapNG / our package** → real BeamNG hills + full-loop level  
- **GPX DecalRoad** → official race line in-game  

---

## Quick “am I in the right place?” checklist

You’re good if you can see all of these together:
- Colorado River / Parker area on the **west**
- Big desert loop **east** of town
- Farm pivots / green fields toward the **southeast** of the box
- Race line matching your racer GPX

That’s the same frame we already baked into BeamNG.
