DRAG THESE ONTO MELD STUDIO
============================

1. Double-click tools\Start-MeldLayout.bat and leave it open.
2. Open Meld Studio. File -> Import Session -> meld\Rise-Above-Meld.json
   That drops all 8 scenes + overlay / chat / Lumia browser layers.

3. Then add your game and cameras in Meld (once):
   Layers + -> Game Capture     name it  Game / Main
   Layers + -> Video Device     Cam / Face, Cam / Room, Cam / Wheel, Cam / Pedals

4. If you skipped Import Session, drag the files in THIS folder onto each scene:
   RACE - Main.html            onto the Main (1920x1080) canvas, scene RACE
   RACE - Portrait.html        onto the Portrait canvas (Multi Canvas), scene RACE
   Same pattern for the other scene names.

Size the overlay to the full canvas. Overlay sits ON TOP of game + cameras.

Social Stream Ninja + Lumia layers are already in the imported session.
Paste your session ID / Lumia URL in overlays\shared\config.js then reload the Browser layers.
