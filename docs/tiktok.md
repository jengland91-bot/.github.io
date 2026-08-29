# TikTok LIVE Studio — Rise Above

TikTok LIVE Studio cannot run the OBS WebSocket installer. Use the same vertical overlays over a local HTTP server.

1. Double-click `tools/Start-OverlayServer.bat` and leave it open while live.
2. Canvas **1080 × 1920**. Scenes: STARTING SOON, GRID, RACE, RACE DUAL, REPLAY, BRB, ENDING.
3. Add a **Link** source per scene. URLs:

- STARTING SOON: `http://127.0.0.1:5500/overlays/vertical/starting-soon.html?m=5`
- GRID: `http://127.0.0.1:5500/overlays/vertical/chatting.html`
- RACE: `http://127.0.0.1:5500/overlays/vertical/live.html`
- RACE DUAL: `http://127.0.0.1:5500/overlays/vertical/race-dual.html`
- REPLAY: `http://127.0.0.1:5500/overlays/vertical/replay.html`
- BRB: `http://127.0.0.1:5500/overlays/vertical/brb.html`
- ENDING: `http://127.0.0.1:5500/overlays/vertical/ending.html`

RACE sizes (same as OBS Vertical):

| Source | X | Y | W | H |
| --- | --- | --- | --- | --- |
| Game / Main | 0 | 0 | 1080 | 608 |
| Cam / Face | 16 | 624 | 520 | 220 |
| Cam / Room | 544 | 624 | 520 | 220 |
| Cam / Wheel | 16 | 860 | 520 | 220 |
| Cam / Pedals | 544 | 860 | 520 | 220 |
| Overlay Link | 0 | 0 | 1080 | 1920 |
| Lumia Link | 0 | 0 | 1080 | 1920 |

GRID has no game. Face 1048×420 at 16,88; Room 1048×280 at 16,524; Wheel 516×200 at 16,820; Pedals 516×200 at 548,820.

RACE DUAL: Game / Main still top strip. Angle 2 is 1048×200 at 16,624. Skip Dual until you have a second BeamNG view.

REPLAY: game 1080×608 at 0,360. No cams.

Audio is BeamNG + mic only, not Discord.

Edit names in `overlays/shared/config.js`, then refresh the Link source.

Portrait + landscape Dual in Studio: portrait uses the vertical URLs above. Landscape uses the wide files (`overlays/live.html`, no `vertical/`).

If you already go live from OBS collection **Rise Above BeamNG Vertical**, you can skip Studio.
