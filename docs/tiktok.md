# TikTok LIVE Studio layout

Go live from **TikTok LIVE Studio only**. Do not open OBS.

Studio cannot import a scene file. Open `tiktok-studio/index.html` (via `tools/Start-TikTokLayout.bat`) and build Dual layout from that board.

Turn on **Dual layout**. Add sources on the **phone** canvas first. Landscape only resizes those same sources. One overlay URL per scene — stretch it to 1920×1080 on landscape and the HUD flips.

Studio Dual layout is not the scene named RACE DUAL. Dual layout = two screens. RACE DUAL = a second BeamNG camera angle.

1. Double-click `tools/Start-TikTokLayout.bat` and leave it open while live.
2. Same scene names, including DESK for sit-at-desk other games. Start with RACE.
3. Phone Overlay Link URLs:

- STARTING SOON: `http://127.0.0.1:5500/overlays/vertical/starting-soon.html?m=5`
- GRID: `http://127.0.0.1:5500/overlays/vertical/chatting.html`
- DESK: `http://127.0.0.1:5500/overlays/vertical/desk.html`
- RACE: `http://127.0.0.1:5500/overlays/vertical/live.html`
- RACE DUAL: `http://127.0.0.1:5500/overlays/vertical/race-dual.html`
- REPLAY: `http://127.0.0.1:5500/overlays/vertical/replay.html`
- BRB: `http://127.0.0.1:5500/overlays/vertical/brb.html`
- ENDING: `http://127.0.0.1:5500/overlays/vertical/ending.html`

Phone RACE: game 1080×608 at 0,0. Face 520×220 at 16,624. Room 520×220 at 544,624. Wheel 520×220 at 16,860. Pedals 520×220 at 544,860. Overlay + Lumia 1080×1920.

Landscape RACE (resize the same sources): game 1920×1080 at 0,0. Four cams 320×180 along the bottom at y=876 (x = 48 / 384 / 720 / 1056). Overlay + Lumia 1920×1080.

Audio: BeamNG + mic only, not Discord.
