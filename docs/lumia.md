# Lumia Stream — overlay, lights, cam director

Lumia is the only overlay app in this kit. It does chat, alerts, goals, lights, and OBS camera/scene switches.

Connect guide: [Lumia + OBS](https://lumiastream.com/blogs/how-to-integrate-obs-streaming-software-with-lumia-stream)

## Connect OBS

1. OBS 28+ → Tools → WebSocket Server Settings
2. Enable, port **4455**, authentication on, copy password
3. Lumia → Connections → Add → OBS → `localhost` / 4455 / password
4. Same page: Twitch (and any other platform) + lights

## One overlay, not five browser sources

In Lumia’s overlay editor, build **one** overlay named something like `Rise Above Race`:

| Layer | Put it here (RACE) |
| --- | --- |
| Chatbox | 384×500 at **1488, 520** |
| Alerts | 860×200 at **530, 24** |
| Event list / labels | 420×70 at **48, 96** |
| Now Playing | 400×64 at **48, 800** |
| Goal | optional; skip on RACE if it covers the cams |

Colors: text `#EDE4D4`, accent `#C65A12`, backgrounds transparent or a light dark glass.

Copy the overlay URL once. OBS source `Lumia / Overlay`, 1920×1080 on the wide collection, 1080×1920 on the vertical collection, **above** the Rise Above HUD.

Vertical RACE chatbox: **1048×800 at 16, 1096**. Alerts: **1048×160 at 16, 16**. Duplicate the Lumia overlay for 9:16 if chat looks stretched; or keep one URL and park layers on the vertical wells.

GRID and RACE DUAL use different wells — either duplicate the overlay in Lumia with those positions, or keep one overlay and accept that chat sits in the RACE pocket on every scene (still readable). Two Lumia overlays (Race / Grid) is cleaner if the editor allows switching with the scene.

## Scene lights (Alerts → OBS)

| Scene | Light |
| --- | --- |
| `STARTING SOON` | Warm amber, slow breathe |
| `GRID` | Soft ice / white, face-friendly |
| `RACE` | Ember `#C65A12` |
| `RACE DUAL` | Ember + a bit of ice on a second zone if you have one |
| `REPLAY` | Dim gold |
| `BRB` | Dim cool blue, 30–40% |
| `ENDING` | Gold pulse, then house white on stream stop |

Follow/sub in Lumia: **on-screen alert + a 2s light flash**. Do not add a second alerts app.

## Camera director (OBS actions)

Use **Set source visibility** on the scene `RACE` (and copy the same rows for `GRID` / `RACE DUAL`).

| Command | Action |
| --- | --- |
| `!face` | Face on; Room, Wheel, Pedals off |
| `!room` | Room on; Face, Wheel, Pedals off |
| `!rig` | Face, Room, Wheel, Pedals all on |
| `!wheel` | Wheel on; Face, Room, Pedals off |
| `!pedals` | Pedals on; Face, Room, Wheel off |
| `!game` | All four cams off (game only) |
| `!race` | Set scene `RACE` |
| `!dual` | Set scene `RACE DUAL` |
| `!replay` | Set scene `REPLAY` |
| `!grid` | Set scene `GRID` |
| `!brb` | Set scene `BRB` |

Mods-only for scene switches if random viewers should not yank you into BRB. `!face` / `!room` / `!rig` / `!wheel` / `!pedals` can be everyone with a 15–30s cooldown.

Hype clip redeem: show `Media / Hype Clip`, delay = length, hide. Restart when active, close file when inactive.

## Troubleshooting

- Lumia cannot see scenes: WebSocket off, wrong password, OBS closed
- Blank overlay: recopy the room URL; Lumia app must be running
- Cam freeze: USB bandwidth — drop to 720p, different ports
- BeamNG black: Game Capture → Window Capture (Windows Graphics Capture)
- Scene switch does nothing: name mismatch — copy from [source-map.md](../obs/source-map.md)
