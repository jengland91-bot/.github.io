Drop Google Earth Pro / MapNG satellite tiles here for sharper close-up patches.

1) Copy tiles.json.example → tiles.json
2) Add your .jpg / .png files
3) Fill in center lat, lon, and ground width/height in meters
4) From beamng/parker_400 run:
     python3 scripts/stitch_sat_tiles.py
     python3 scripts/pack_mod_zip.py

Full guide: docs/CLOSEUP_MULTI_TILE.md
