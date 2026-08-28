# Source map

Names must match OBS and Lumia exactly.

## Scenes

- `STARTING SOON`
- `GRID`
- `RACE`
- `RACE DUAL`
- `REPLAY`
- `BRB`
- `ENDING`

## Sources

| Name | Type | Notes |
| --- | --- | --- |
| `Overlay / Starting Soon` | Browser | `starting-soon.html?m=5` |
| `Overlay / Grid HUD` | Browser | `chatting.html` |
| `Overlay / Race HUD` | Browser | `live.html` |
| `Overlay / Dual HUD` | Browser | `race-dual.html` |
| `Overlay / Replay HUD` | Browser | `replay.html` |
| `Overlay / BRB` | Browser | `brb.html` |
| `Overlay / Ending` | Browser | `ending.html` |
| `Game / Main` | Game Capture | BeamNG.drive. Paste (Reference) on RACE, RACE DUAL, REPLAY |
| `Game / Angle 2` | Game or Window Capture | Second view. RACE DUAL only |
| `Cam / Face` | Video Capture Device | Paste (Reference) on GRID, RACE, RACE DUAL |
| `Cam / Wheel` | Video Capture Device | Same |
| `Cam / Wide` | Video Capture Device | Optional rig / room |
| `Mic / Main` | Audio Input | Filters in docs/obs.md |
| `Lumia / Overlay` | Browser | Single Lumia overlay URL, 1920×1080 |
| `Media / Hype Clip` | Media | Hidden; Lumia toggles it |
| `Audio / Staging Music` | Media | STARTING SOON / BRB |

## RACE transforms

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1920 | 1080 | 0 | 0 |
| `Cam / Face` | 400 | 225 | 48 | 816 |
| `Cam / Wheel` | 400 | 225 | 464 | 816 |
| `Overlay / Race HUD` | 1920 | 1080 | 0 | 0 |
| `Lumia / Overlay` | 1920 | 1080 | 0 | 0 |

Lumia Chatbox layer: **384×500 at 1488, 520**. Alerts: **860×200 at 530, 24**.

## GRID transforms

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Face` | 960 | 540 | 48 | 168 |
| `Cam / Wheel` | 840 | 473 | 1032 | 168 |
| Lumia Chatbox | 840 | 360 | 1032 | 660 |

## RACE DUAL transforms

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1920 | 1080 | 0 | 0 |
| `Game / Angle 2` | 640 | 360 | 1248 | 48 |
| `Cam / Face` | 320 | 180 | 48 | 860 |
| `Cam / Wheel` | 320 | 180 | 384 | 860 |
| Lumia Chatbox | 640 | 580 | 1248 | 428 |

Right-click source → Transform → Edit Transform. Bounding Box type: **Scale to inner bounds**, center.
