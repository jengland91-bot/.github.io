# Google Earth / satellite paint — Parker 400

The heightmap is already **real elevation**. Satellite color is the next visual jump.

## What to export from Google Earth Pro

1. Open the KML: `source/reference/p400/2026_Parker_400_CTUTV_Final_Racer_File.kml`
2. Fit the view to the full CTUTV loop (include a little desert margin)
3. Note the exact corner lat/lon of your export box — must match the BeamNG world frame:
   - World: **65536 m** square, course centered, scale **1.0**
   - See `p400_map_course.json` → `bbox` + `transform`
4. Save a high-res JPEG/PNG of the ground (turn off labels/roads overlays)

## Better open alternative (recommended)

Esri World Imagery / USGS NAIP tiles — same footprint, cleaner licensing for mods.

Target size for BeamNG base colormap: **2048² or 4096²** matching the terrain.

## Where it goes in BeamNG

1. Convert export to a seamless desert base texture set (albedo / normal / roughness)
2. Place under `levels/parker_400/art/terrains/`
3. Wire into `main.materials.json` as the terrain **base** layer
4. Paint `desert_base` across the map, `course_pack` along the DecalRoad ribbon, `rock_slope` on steep DEM slopes

## Optional high-detail DEM later

If you can pull **USGS NED 10 m** or **1 m lidar** for the Parker box, drop GeoTIFFs into `source/reference/elevation/` and we can re-bake the heightmap for sharper washes and whoops. SRTM is the correct first pass for a 55 km footprint.
