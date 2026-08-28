# OBS + BeamNG + multi-cam

Two canvases. Scene names are exact — Lumia matches them as written.

- Collection **Rise Above BeamNG**: **1920×1080**
- Collection **Rise Above BeamNG Vertical**: **1080×1920**

Switch collections with the dropdown at the top of OBS. Numpad 1–7 fire the same scene names on whichever collection is active. Pick BeamNG on `Game / Main` in **both**.

## Video / encode

Same as a normal 1080p stream: NV12, Rec. 709, Limited. Twitch CBR 6000, keyframe 2, NVENC Quality. Audio 48 kHz.

Mic filters top → bottom: RNNoise → (optional gate) → EQ → Compressor 3:1 → Limiter −1.5 dB.

Keep game audio and mic on separate tracks if you record.

## BeamNG capture

1. BeamNG: **borderless windowed**, native 1920×1080 if the PC can hold it.
2. Turn **Steam overlay** off for BeamNG (Steam → BeamNG → Properties → Overlay).
3. OBS source `Game / Main`: **Game Capture** → Capture specific window → `BeamNG.drive`.
4. Uncheck Capture Cursor.
5. If the source is **black** (common with Vulkan): change that source to **Window Capture**, method **Windows Graphics Capture**, pick BeamNG.

Do not use Display Capture unless both of those fail — it grabs your whole monitor.

In-game cameras (C, Shift+C, chase / hood / cockpit / orbit) are **not** extra OBS sources. They all come through `Game / Main`. Switch those with BeamNG, not OBS.

## Multi-cam (physical)

Typical race rig:

| Source | What it sees |
| --- | --- |
| `Game / Main` | BeamNG |
| `Cam / Face` | You |
| `Cam / Wheel` | Hands / wheel |
| `Game / Angle 2` | Optional second BeamNG view |

### Second BeamNG angle

Only needed for `RACE DUAL`. Options:

- Second monitor with a BeamNG camera (external camera app, or a windowed second view if you use one)
- A bumper/hood window if you run a camera UI mod
- Skip Angle 2 and use Dual only when you actually have it — otherwise stay on `RACE` and swap in-game cameras

### USB

- Two webcams on **different** USB controllers (one rear motherboard, one front/header or a different controller)
- 720p 30fps per cam is plenty next to 1080p game
- Leave **Deactivate when not showing** **off** so Lumia/hotkey switches do not wait on USB reconnect

Create each cam once, then **Copy → Paste (Reference)** into the other scenes so OBS does not open the device twice.

Crop with **Alt + drag**. Matching Rec. 709 / Limited on the cams keeps skin from looking orange next to BeamNG.

## Source order — RACE (bottom → top)

1. `Game / Main`
2. `Cam / Face`
3. `Cam / Wheel`
4. `Overlay / Race HUD` (`live.html`)
5. `Lumia / Overlay`
6. `Media / Hype Clip` (hidden)

## GRID

1. `Cam / Face` (large)
2. `Cam / Wheel`
3. `Overlay / Grid HUD`
4. `Lumia / Overlay`

## RACE DUAL

1. `Game / Main` (full)
2. `Game / Angle 2` (640×360 at 1248, 48)
3. `Cam / Face` / `Cam / Wheel` (small, bottom left)
4. `Overlay / Dual HUD`
5. `Lumia / Overlay`

## REPLAY

1. `Game / Main` only
2. `Overlay / Replay HUD`
3. `Lumia / Overlay` (alerts only is fine; hide the chatbox layer in Lumia for this scene if you can, or accept chat on the side)

## Vertical (1080×1920)

Collection **Rise Above BeamNG Vertical**. Game sits in a 16:9 strip (1080×608) at the top of RACE. Face + wheel under that. Chat fills the phone-shaped remainder. Full numbers: [source-map.md](../obs/source-map.md).

To go live on TikTok / Shorts / Reels only: switch to that collection, then Start Streaming.

To run wide and vertical **at the same time**, install [Aitum Vertical](https://aitum.tv/vertical) and copy the vertical transforms into its canvas. OBS cannot hold two canvas sizes in one collection without that plugin.

## Browser sources

- Wide: 1920×1080, FPS 30. Vertical: 1080×1920, FPS 30
- CSS: `body { background-color: rgba(0, 0, 0, 0); margin: 0; overflow: hidden; }`
- Local file pointing at this repo (`overlays/…` or `overlays/vertical/…`)

## Hotkeys

| Scene | Suggested |
| --- | --- |
| STARTING SOON | Numpad 1 |
| GRID | Numpad 2 |
| RACE | Numpad 3 |
| RACE DUAL | Numpad 4 |
| REPLAY | Numpad 5 |
| BRB | Numpad 6 |
| ENDING | Numpad 7 |

Fade 300 ms. Lumia can fire the same scene changes from chat.

## Placement helper

`live.html?setup=1` and `vertical/live.html?setup=1` while lining up Lumia layers. Remove `setup=1` before going live.
