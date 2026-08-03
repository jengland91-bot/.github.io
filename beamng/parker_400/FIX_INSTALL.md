# Why Parker 400 does not show in Freeroam (BeamNG 0.39.1)

## The real cause (after the 0.39 update)

Copying a folder into:

```
...\BeamNG.drive\current\levels\parker_400\
```

often **does nothing** in Freeroam on **0.39 / 0.39.1**.

BeamNG expects custom maps as a **mod**:

```
...\BeamNG.drive\current\mods\parker_400.zip
```

Inside that zip the layout must be:

```
levels/parker_400/info.json
levels/parker_400/main/MissionGroup/...
...
```

---

## Fix (2 minutes)

### Option A — one zip (best)

1. Download:  
   [parker_400.zip](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip)
2. BeamNG launcher → **Manage User Folder** → **Open**
3. Open the **`mods`** folder
4. Put **`parker_400.zip`** there (**do not unzip**)
5. Delete any old `levels\parker_400` folder if you made one earlier
6. Quit BeamNG completely → start again
7. Enable the mod if needed → **Freeroam** → search **parker**

Full guide: [INSTALL_FOR_039.md](INSTALL_FOR_039.md)

### Option B — run the bat

1. Download [Parker_400_Install.zip](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/Parker_400_Install.zip) and extract
2. Double-click **`FIX_AND_INSTALL.bat`**
3. It copies the mod zip into `mods\` and removes the old loose `levels\parker_400`

---

## How to find the correct user folder

| Wrong (old advice) | Right for 0.39 |
|--------------------|----------------|
| `Documents\BeamNG.drive` | Launcher → Manage User Folder → Open |
| Usually | `%LOCALAPPDATA%\BeamNG\BeamNG.drive\current\` |

You must see a **`mods`** folder inside what you opened.

---

## Still missing?

1. Zip is named `parker_400.zip` under `mods\`
2. Opening the zip shows `levels\parker_400\info.json` at the top
3. Mod is enabled
4. Full restart after install
5. Search Freeroam for `parker` (not only scrolling)
6. Check `logs\` for load errors mentioning `parker_400`

## Map loads but is black

Old packages were missing **`theTerrain.ter`**. Re-download the latest:

[parker_400.zip](https://github.com/jengland91-bot/.github.io/raw/cursor/parker-400-beamng-a8ad/beamng/parker_400/mods_drop_in/parker_400.zip)

Inside the zip you must see `levels/parker_400/theTerrain.ter` (~48 MB).
