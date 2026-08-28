# Source map

Names must match OBS and Lumia exactly.

The installer creates **two** scene collections. Same scene names in both. Switch them with the dropdown at the top of OBS.

- `Rise Above BeamNG` — 1920×1080 Twitch / YouTube
- `Rise Above BeamNG Vertical` — 1080×1920 TikTok / Shorts / Reels

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
| `Cam / Face` | Video Capture Device | Paste (Reference) onto GRID, RACE, and RACE DUAL |
| `Cam / Wheel` | Video Capture Device | Same |
| `Cam / Wide` | Video Capture Device | Optional rig / room |
| `Mic / Main` | Audio Input | Filters in docs/obs.md |
| `Lumia / Overlay` | Browser | Lumia overlay URL. 1920×1080 wide, 1080×1920 vertical |
| `Media / Hype Clip` | Media | Hidden; Lumia toggles it |
| `Audio / Staging Music` | Media | STARTING SOON / BRB |

## RACE transforms (wide 1920×1080)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1920 | 1080 | 0 | 0 |
| `Cam / Face` | 400 | 225 | 48 | 816 |
| `Cam / Wheel` | 400 | 225 | 464 | 816 |
| `Overlay / Race HUD` | 1920 | 1080 | 0 | 0 |
| `Lumia / Overlay` | 1920 | 1080 | 0 | 0 |

Lumia Chatbox layer: **384×500 at 1488, 520**. Alerts: **860×200 at 530, 24**.

## GRID transforms (wide)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Face` | 960 | 540 | 48 | 168 |
| `Cam / Wheel` | 840 | 473 | 1032 | 168 |
| Lumia Chatbox | 840 | 360 | 1032 | 660 |

## RACE DUAL transforms (wide)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1920 | 1080 | 0 | 0 |
| `Game / Angle 2` | 640 | 360 | 1248 | 48 |
| `Cam / Face` | 320 | 180 | 48 | 860 |
| `Cam / Wheel` | 320 | 180 | 384 | 860 |
| Lumia Chatbox | 640 | 580 | 1248 | 428 |

## RACE transforms (vertical 1080×1920)

Game is a 16:9 strip at the top. Face + wheel sit under it. Chat fills the rest.

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1080 | 608 | 0 | 0 |
| `Cam / Face` | 520 | 292 | 16 | 624 |
| `Cam / Wheel` | 520 | 292 | 544 | 624 |
| `Overlay / Race HUD` | 1080 | 1920 | 0 | 0 |
| `Lumia / Overlay` | 1080 | 1920 | 0 | 0 |

Lumia Chatbox: **1048×960 at 16, 932**. Alerts: **1048×160 at 16, 16**.

## GRID transforms (vertical)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Cam / Face` | 1048 | 590 | 16 | 88 |
| `Cam / Wheel` | 1048 | 392 | 16 | 696 |
| Lumia Chatbox | 1048 | 780 | 16 | 1104 |

## RACE DUAL transforms (vertical)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1080 | 608 | 0 | 0 |
| `Game / Angle 2` | 1048 | 280 | 16 | 624 |
| `Cam / Face` | 520 | 292 | 16 | 920 |
| `Cam / Wheel` | 520 | 292 | 544 | 920 |
| Lumia Chatbox | 1048 | 672 | 16 | 1228 |

## REPLAY transforms (vertical)

| Source | W | H | X | Y |
| --- | --- | --- | --- | --- |
| `Game / Main` | 1080 | 608 | 0 | 360 |

Right-click source → Transform → Edit Transform. Bounding Box type: **Scale to inner bounds**, center.

To stream wide and vertical **at the same time**, install [Aitum Vertical](https://aitum.tv/vertical) and copy the vertical transforms into its canvas. This kit’s second collection is for switching to 9:16 when you are only going to TikTok / Shorts / Reels.
