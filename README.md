# Rise Above — BeamNG OBS + Lumia

Race-broadcast overlay kit for **BeamNG.drive** with **multi-cam** (game + face + wheel) and **Lumia Stream** for chat, alerts, lights, and camera switching. Casterlabs is not used.

Open [START-HERE.txt](START-HERE.txt). On Windows: extract the zip, open OBS, double-click `tools/Install-OBS.bat`.

That creates two scene collections:

- **Rise Above BeamNG** — 1920×1080 for Twitch / YouTube
- **Rise Above BeamNG Vertical** — 1080×1920 for TikTok / Shorts / Reels

Same scene names in both. Switch them with the dropdown at the top of OBS. Pick BeamNG on `Game / Main` in both collections.

## Scenes

| OBS scene | Wide overlay | Vertical overlay | Job |
| --- | --- | --- | --- |
| `STARTING SOON` | `overlays/starting-soon.html` | `overlays/vertical/starting-soon.html` | Countdown, staging lights |
| `GRID` | `overlays/chatting.html` | `overlays/vertical/chatting.html` | Big face + wheel, talking |
| `RACE` | `overlays/live.html` | `overlays/vertical/live.html` | BeamNG + face + wheel + chat |
| `RACE DUAL` | `overlays/race-dual.html` | `overlays/vertical/race-dual.html` | Main view + second angle |
| `REPLAY` | `overlays/replay.html` | `overlays/vertical/replay.html` | Clean game, no cams |
| `BRB` | `overlays/brb.html` | `overlays/vertical/brb.html` | Pit stop |
| `ENDING` | `overlays/ending.html` | `overlays/vertical/ending.html` | Checkered / thanks |

In-game BeamNG cameras (C / Shift+C) stay on one source: `Game / Main`. Physical cameras are `Cam / Face` and `Cam / Wheel`. A second BeamNG view (other monitor, bumper window) is `Game / Angle 2` on `RACE DUAL` only.

`?setup=1` on an overlay prints wells so you can park Lumia layers. Turn it off before going live.

## Who does what

- **OBS** — BeamNG capture, face/wheel cams, layout, audio
- **Lumia** — chatbox, alerts, goals, lights, scene/cam commands

## Customize

Edit `overlays/shared/config.js`, then in OBS right-click the overlay source → **Refresh**.

## Docs

- [OBS + BeamNG + multi-cam](docs/obs.html)
- [Lumia overlay, lights, cam director](docs/lumia.html)
- [Source map](obs/source-map.md)
