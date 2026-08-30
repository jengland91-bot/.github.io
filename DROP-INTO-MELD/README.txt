DRAG THESE ONTO MELD STUDIO
============================

Easiest: go up one folder and double-click 1-OPEN-IN-MELD.bat
That writes STARTING SOON / GRID / RACE / BRB into Meld for you.

If the bat did nothing:
  Go up one folder and double-click 00-DOUBLE-CLICK-ME.html
  Then run 1-OPEN-IN-MELD.bat (Unblock it if Windows blocked it).

Then add your game and cameras in Meld (once):
   Layers + -> Game Capture     name it  Game / Main
   Layers + -> Video Device     Cam / Face, Cam / Room, Cam / Wheel, Cam / Pedals

If a scene is missing its HUD, drag the files in THIS folder onto that scene:
   RACE - Main.html            onto the Main (1920x1080) canvas, scene RACE
   RACE - Portrait.html        onto the Portrait canvas (Multi Canvas), scene RACE
   Same pattern for the other scene names.

You never put code into Meld. The bat loads the session. These HTML files
are only a backup if a Browser layer is missing.

Social Stream Ninja + Lumia layers are already in the session.
Paste your session ID / Lumia URL in overlays\shared\config.js then reload the Browser layers.
