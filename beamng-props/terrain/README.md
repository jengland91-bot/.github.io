# Parker 400 — RGB Mask → Heightmap (Blender)

That colorful image is an **RGB terrain feature mask**, not a heightmap yet:

| Channel | Meaning | Height |
|---------|---------|--------|
| **R** red | Ridges / peaks | High |
| **G** green | Slopes / mid | Medium |
| **B** blue | Valleys / basins | Low |

## 1. Drop your image here

Save the attached RGB map as:

```text
beamng-props/terrain/source/rgb_terrain_mask.png
```

(If missing, the script generates a synthetic demo mask.)

## 2. Convert to heightmap

```bash
python3 beamng-props/terrain/rgb_to_heightmap.py
# or with an explicit path:
python3 beamng-props/terrain/rgb_to_heightmap.py /path/to/your_mask.png
```

Writes:

| File | Use |
|------|-----|
| `export/heightmap_8bit.png` | Blender displace / quick preview |
| `export/heightmap_16bit.png` | Better precision for BeamNG Terrain |
| `export/heightmap_preview.png` | Tinted preview |

## 3. Preview / sculpt base in Blender

```bash
/tmp/blender-4.2.9-linux-x64/blender --background --python beamng-props/terrain/apply_heightmap_blender.py
```

Creates `export/parker_terrain.blend` (1024 m grid, ~80 m relief — edit constants in the script).

## 4. BeamNG

Prefer the **heightmap PNG** in a Terrain Block (16-bit), not the DAE mega-mesh.
Props (mile markers, flora, K-rails) go on top as TSStatics.

Tune in `rgb_to_heightmap.py`:

- Softmax sharpness `k`
- Blur radius
- Class heights (red/green/blue targets)
