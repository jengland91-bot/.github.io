# Source map

Lumia Stream and this overlay kit depend on **exact** names. Copy-paste them.

## Scenes

- `STARTING SOON`
- `JUST CHATTING`
- `LIVE`
- `BRB`
- `ENDING`

Optional: `INTERMISSION`

## Sources

| Name | Type | Notes |
| --- | --- | --- |
| `Overlay / Starting Soon` | Browser | `starting-soon.html?m=5` |
| `Overlay / Chatting HUD` | Browser | `chatting.html` |
| `Overlay / Live HUD` | Browser | `live.html` |
| `Overlay / BRB` | Browser | `brb.html` |
| `Overlay / Ending` | Browser | `ending.html` |
| `Overlay / Intermission` | Browser | `intermission.html` |
| `Cam / Main` | Video Capture Device | Paste (Reference) between scenes |
| `Game / Capture` | Game Capture | LIVE only |
| `Mic / Main` | Audio Input | Filters documented in docs/obs.md |
| `Casterlabs / Alerts` | Browser | Combined alerts URL |
| `Casterlabs / Chat` | Browser | Chat widget URL |
| `Casterlabs / Labels` | Browser | Recent follow / sub |
| `Casterlabs / Goal` | Browser | Goal widget |
| `Casterlabs / Now Playing` | Browser | Optional |
| `Casterlabs / Emoji Rain` | Browser | Optional, full canvas |
| `Lumia / Overlay` | Browser | Lumia room URL |
| `Media / Hype Clip` | Media | Hidden; Lumia toggles visibility |
| `Audio / Staging Music` | Media | STARTING SOON / BRB |

## LIVE transforms (pixels)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Main` | 360 | 270 | 48 | 762 |
| `Casterlabs / Chat` | 400 | 460 | 1472 | 560 |
| `Casterlabs / Alerts` | 860 | 200 | 530 | 24 |
| `Casterlabs / Goal` | 480 | 52 | 720 | 1004 |
| `Casterlabs / Labels` | 420 | 70 | 48 | 96 |
| `Casterlabs / Now Playing` | 360 | 68 | 48 | 678 |
| HUD / Lumia / Emoji Rain | 1920 | 1080 | 0 | 0 |

## JUST CHATTING transforms

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Main` | 1100 | 619 | 56 | 168 |
| `Casterlabs / Chat` | 648 | 860 | 1216 | 96 |
| `Casterlabs / Alerts` | 860 | 200 | 176 | 24 |
| `Casterlabs / Goal` | 480 | 52 | 366 | 1004 |
| `Casterlabs / Labels` | 420 | 70 | 56 | 96 |
| `Casterlabs / Now Playing` | 420 | 68 | 56 | 804 |

Right-click a source → Transform → Edit Transform → set Position and Size (or Bounding Box).
