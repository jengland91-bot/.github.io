# Parker 400 — Mile Marker Prop Kit

Ready-made desert-race **mile marker** for BeamNG.drive. Built for beginners: either run the Blender script, or import the OBJ.

## What’s included

| File | Purpose |
|------|---------|
| `build_mile_marker.py` | Run inside Blender 4.x to spawn a nicer marker (bevels, bolts, frame, textures) |
| `generate_textures.py` | Makes sign + wood PNGs (`mile_00` … `mile_50`) |
| `generate_obj.py` | Writes a simple importable `export/milemarker_01.obj` |
| `textures/` | Wood grain, metal, and `MILE N` sign faces |
| `export/milemarker_01.obj` | Mesh you can import if you don’t want to run the script yet |

## Easiest path (recommended)

### 1. Generate textures (already done in this folder)

If you need to regenerate:

```bash
python3 generate_textures.py
python3 generate_obj.py
```

### 2. Build it in Blender

1. Open **Blender**
2. Switch to the **Scripting** workspace (top bar)
3. **Open** `build_mile_marker.py`
4. Near the top, set the mile you want:

```python
MILE_NUMBER = 1
```

5. Click **Run Script**
6. You should see a post + sign with bolts at the world origin

### 3. Export for BeamNG

1. Make sure the **post** is selected (children come with it when parented)
2. **File → Export → Collada (.dae)**
3. Enable **Selection Only**
4. Save into your map, for example:

```text
levels/YourParkerMap/art/shapes/props/milemarker_01.dae
```

5. In BeamNG World Editor (`F11`), place a **TSStatic** pointing at that `.dae`

### 4. Make Mile 2, 3, 5, …

1. Change `MILE_NUMBER = 5` (etc.)
2. Run the script again
3. Export as `milemarker_05.dae`

Textures already exist for miles **0–20** and every **5** up to **50**.

---

## Alternate: import the OBJ (no script)

1. Blender → **File → Import → Wavefront (.obj)**
2. Pick `export/milemarker_01.obj`
3. If textures look missing, open the Material tab and point Base Color at `textures/mile_01.png` / `post_wood.png`
4. Export Collada the same way as above

---

## Scale notes

- Units are **meters**
- Post ≈ **1.45 m** tall, **10 cm** square
- Origin is at the **ground** under the post
- Sign faces **-Y** (rotate in World Editor if your course needs another facing)

## Next props in this series

After this works in-game: **course arrows → flags → stakes + ribbon → snow fence → rocks**.
