# Rise Above — BeamNG OBS + Lumia

Race-broadcast overlay kit for **BeamNG.drive** with **multi-cam** (game + face + wheel) and **Lumia Stream** for chat, alerts, lights, and camera switching. Casterlabs is not used.

Open [the preview](index.html), the [setup checklist](setup.html), or the **[OBS + Lumia installer](tools/install.html)** (run it on the streaming PC).

## Scenes

| OBS scene | Overlay | Job |
| --- | --- | --- |
| `STARTING SOON` | `overlays/starting-soon.html` | Countdown, staging lights |
| `GRID` | `overlays/chatting.html` | Big face + wheel, talking |
| `RACE` | `overlays/live.html` | Full BeamNG, face + wheel PiPs |
| `RACE DUAL` | `overlays/race-dual.html` | Main view + second angle |
| `REPLAY` | `overlays/replay.html` | Clean game, no cams |
| `BRB` | `overlays/brb.html` | Pit stop |
| `ENDING` | `overlays/ending.html` | Checkered / thanks |

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
