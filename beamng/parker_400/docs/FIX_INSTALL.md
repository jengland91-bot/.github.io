# FIX: Install Parker 400 when the .bat fails

## Fastest fix (manual — usually works)

### A) Find your extracted map
You already had this:
```
D:\Parker_400_Install\levels\parker_400
```
Open that `parker_400` folder and confirm you see `info.json` inside.

### B) Find BeamNG’s levels folder
1. Press `Win + R`
2. Paste **one** of these and press Enter (try top first):

```
%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\levels
```

```
%USERPROFILE%\Documents\BeamNG.drive\levels
```

3. If Windows says it can’t find the path:
   - Win + R → `%LOCALAPPDATA%\BeamNG`
   - Look for `BeamNG.drive` → `current` → `levels`
   - If `levels` doesn’t exist, create a new folder named exactly `levels`

### C) Copy the map in
1. Copy the whole `parker_400` folder from:
   ```
   D:\Parker_400_Install\levels\parker_400
   ```
2. Paste it into the BeamNG `levels` folder so you get:
   ```
   ...\levels\parker_400\info.json
   ```
3. Path must end with `\levels\parker_400` — **not** `\levels\levels\parker_400`

### D) Check in game
1. Fully quit BeamNG, then reopen
2. Freeroam → look for **Parker 400**
3. If it’s missing: you pasted into the wrong `levels` folder — try the Documents path above

### E) After it loads
1. F11 → Import Terrain → load  
   `import\p400_gpx_scale.preset.json`
2. **16** m/px, **1500** max height  
3. Import → Ctrl+S  
4. Paint `desert_base` → Ctrl+S  

---

## Easier: run FIX_AND_INSTALL.bat

1. Download latest `Parker_400_Install.zip` again  
2. Extract it  
3. Put / run **`FIX_AND_INSTALL.bat`** from inside the extracted folder  
4. It searches common BeamNG folders and copies the map for you  
5. It opens the destination folder when done  

---

## Still stuck? Check these

| Check | Should be |
|---|---|
| `info.json` exists | inside `parker_400` |
| Folder name | exactly `parker_400` (lowercase, underscore) |
| Parent folder | exactly `levels` |
| BeamNG closed | while copying |
| Game restarted | after copy |

If Freeroam still has no Parker 400, tell me:
1. The full path where you pasted `parker_400`  
2. Whether `%LOCALAPPDATA%\BeamNG` opens anything  
and we’ll pinpoint the right folder.
