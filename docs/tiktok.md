# TikTok LIVE Studio — vertical + horizontal

Turn on **Dual layout** in TikTok LIVE Studio. That streams phone **1080 × 1920** and landscape **1920 × 1080** at the same time.

Studio Dual layout is not the OBS scene named RACE DUAL. Dual layout = two screens. RACE DUAL = a second BeamNG camera angle.

1. Double-click `tools/Start-OverlayServer.bat` and leave it open while live.
2. Same seven scene names on both canvases: STARTING SOON, GRID, RACE, RACE DUAL, REPLAY, BRB, ENDING.
3. Add a **Link** source per scene on each canvas.

## Vertical URLs (1080 × 1920)

- STARTING SOON: `http://127.0.0.1:5500/overlays/vertical/starting-soon.html?m=5`
- GRID: `http://127.0.0.1:5500/overlays/vertical/chatting.html`
- RACE: `http://127.0.0.1:5500/overlays/vertical/live.html`
- RACE DUAL: `http://127.0.0.1:5500/overlays/vertical/race-dual.html`
- REPLAY: `http://127.0.0.1:5500/overlays/vertical/replay.html`
- BRB: `http://127.0.0.1:5500/overlays/vertical/brb.html`
- ENDING: `http://127.0.0.1:5500/overlays/vertical/ending.html`

Vertical RACE: game 1080×608 at 0,0. Face 520×220 at 16,624. Room 520×220 at 544,624. Wheel 520×220 at 16,860. Pedals 520×220 at 544,860. Overlay + Lumia 1080×1920.

## Horizontal URLs (1920 × 1080)

- STARTING SOON: `http://127.0.0.1:5500/overlays/starting-soon.html?m=5`
- GRID: `http://127.0.0.1:5500/overlays/chatting.html`
- RACE: `http://127.0.0.1:5500/overlays/live.html`
- RACE DUAL: `http://127.0.0.1:5500/overlays/race-dual.html`
- REPLAY: `http://127.0.0.1:5500/overlays/replay.html`
- BRB: `http://127.0.0.1:5500/overlays/brb.html`
- ENDING: `http://127.0.0.1:5500/overlays/ending.html`

Horizontal RACE: game 1920×1080 at 0,0. Four cams 320×180 along the bottom at y=876 (x = 48 / 384 / 720 / 1056). Overlay + Lumia 1920×1080.

Audio: BeamNG + mic only, not Discord.

Edit `overlays/shared/config.js`, then refresh Link sources on both canvases.
