# Source map

Names must match OBS and Lumia exactly.

The installer creates **two** scene collections. Same scene names in both. Switch them with the dropdown at the top of OBS.

- `Rise Above BeamNG` — 1920×1080 Twitch / YouTube / Kick
- `Rise Above BeamNG Vertical` — 1080×1920 YouTube Shorts / Reels if you go live from OBS (TikTok is TikTok LIVE Studio, not this collection)

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
| `Overlay / Starting Soon` | Browser | Wide: `starting-soon.html?m=5`. Vertical: `vertical/starting-soon.html?m=5` |
| `Overlay / Grid HUD` | Browser | Wide: `chatting.html`. Vertical: `vertical/chatting.html` |
| `Overlay / Race HUD` | Browser | Wide: `live.html`. Vertical: `vertical/live.html` |
| `Overlay / Dual HUD` | Browser | Wide: `race-dual.html`. Vertical: `vertical/race-dual.html` |
| `Overlay / Replay HUD` | Browser | Wide: `replay.html`. Vertical: `vertical/replay.html` |
| `Overlay / BRB` | Browser | Wide: `brb.html`. Vertical: `vertical/brb.html` |
| `Overlay / Ending` | Browser | Wide: `ending.html`. Vertical: `vertical/ending.html` |
| `Game / Main` | Game Capture | BeamNG.drive. Pick the window in **both** collections |
| `Game / Angle 2` | Game or Window Capture | Second view. RACE DUAL only |
| `Cam / Face` | Video Capture Device | Close-up. Paste (Reference) onto GRID, RACE, and RACE DUAL |
| `Cam / Room` | Video Capture Device | Face + room. Same scenes |
| `Cam / Wheel` | Video Capture Device | Hands / wheel. Same scenes |
| `Cam / Pedals` | Video Capture Device | Pedals. Same scenes |
| `Mic / Main` | Audio Input | Your mic. Desktop Audio stays muted |
| `Audio / Game` | Application Audio Capture | BeamNG only. Discord stays off |
| `Lumia / Overlay` | Browser | Lumia overlay URL. 1920×1080 wide, 1080×1920 vertical |
| `Media / Hype Clip` | Media | Hidden; Lumia toggles it |
| `Audio / Staging Music` | Media | STARTING SOON / BRB |

LIVE / GRID / DUAL words on the HUD come from `overlays/shared/config.js`. Change them there, then in OBS right-click the overlay → **Refresh**. Camera positions only update if you re-run `Install-OBS.bat` from a new zip.

## RACE transforms (wide 1920×1080)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1920 | 1080 | 0 | 0 |
| `Audio / Game` | — | — | — | — |
| `Cam / Face` | 320 | 180 | 48 | 876 |
| `Cam / Room` | 320 | 180 | 384 | 876 |
| `Cam / Wheel` | 320 | 180 | 720 | 876 |
| `Cam / Pedals` | 320 | 180 | 1056 | 876 |
| `Overlay / Race HUD` | 1920 | 1080 | 0 | 0 |
| `Lumia / Overlay` | 1920 | 1080 | 0 | 0 |

Lumia Chatbox layer: **384×500 at 1488, 520**. Alerts: **860×200 at 530, 24**.

## GRID transforms (wide)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Face` | 960 | 540 | 48 | 168 |
| `Cam / Room` | 840 | 360 | 1032 | 168 |
| `Cam / Wheel` | 408 | 200 | 1032 | 544 |
| `Cam / Pedals` | 408 | 200 | 1464 | 544 |
| Lumia Chatbox | 840 | 268 | 1032 | 760 |

## RACE DUAL transforms (wide)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1920 | 1080 | 0 | 0 |
| `Game / Angle 2` | 640 | 360 | 1248 | 48 |
| `Cam / Face` | 240 | 135 | 48 | 900 |
| `Cam / Room` | 240 | 135 | 304 | 900 |
| `Cam / Wheel` | 240 | 135 | 560 | 900 |
| `Cam / Pedals` | 240 | 135 | 816 | 900 |
| Lumia Chatbox | 640 | 580 | 1248 | 428 |

## RACE transforms (vertical 1080×1920)

Game is a 16:9 strip at the top. Four cams sit under it. Chat fills the rest.

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1080 | 608 | 0 | 0 |
| `Cam / Face` | 520 | 220 | 16 | 624 |
| `Cam / Room` | 520 | 220 | 544 | 624 |
| `Cam / Wheel` | 520 | 220 | 16 | 860 |
| `Cam / Pedals` | 520 | 220 | 544 | 860 |
| `Overlay / Race HUD` | 1080 | 1920 | 0 | 0 |
| `Lumia / Overlay` | 1080 | 1920 | 0 | 0 |

Lumia Chatbox: **1048×800 at 16, 1096**. Alerts: **1048×160 at 16, 16**.

## GRID transforms (vertical)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Face` | 1048 | 420 | 16 | 88 |
| `Cam / Room` | 1048 | 280 | 16 | 524 |
| `Cam / Wheel` | 516 | 200 | 16 | 820 |
| `Cam / Pedals` | 516 | 200 | 548 | 820 |
| Lumia Chatbox | 1048 | 816 | 16 | 1036 |

## RACE DUAL transforms (vertical)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1080 | 608 | 0 | 0 |
| `Game / Angle 2` | 1048 | 200 | 16 | 624 |
| `Cam / Face` | 520 | 180 | 16 | 840 |
| `Cam / Room` | 520 | 180 | 544 | 840 |
| `Cam / Wheel` | 520 | 180 | 16 | 1036 |
| `Cam / Pedals` | 520 | 180 | 544 | 1036 |
| Lumia Chatbox | 1048 | 660 | 16 | 1232 |

## REPLAY transforms (vertical)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1080 | 608 | 0 | 360 |

Right-click source → Transform → Edit Transform. Bounding Box type: **Scale to inner bounds**, center.

To stream wide and vertical **at the same time from OBS**, install [Aitum Vertical](https://aitum.tv/products/vertical) **and** [Aitum Multistream](https://aitum.tv/products/multi). Stay on collection `Rise Above BeamNG`. Build the phone layout in the Vertical dock. Destinations: [docs/aitum.html](../docs/aitum.html).

Stay on collection `Rise Above BeamNG` while Multi + Vertical are running. The separate `Rise Above BeamNG Vertical` collection is only if you stream 9:16 by itself.
