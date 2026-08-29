# OBS + BeamNG + multi-cam

Two canvases. Scene names are exact — Lumia matches them as written.

- Collection **Rise Above BeamNG**: **1920×1080**
- Collection **Rise Above BeamNG Vertical**: **1080×1920**

Switch collections with the dropdown at the top of OBS. Numpad 1–7 fire the same scene names on whichever collection is active. Numpad 8 is `DESK`. Pick BeamNG on `Game / Main` in **both** for racing. For other games, click `DESK` and pick that game on `Game / Main` and `Audio / Game`.

## Video / encode

Same as a normal 1080p stream: NV12, Rec. 709, Limited. Twitch CBR 6000, keyframe 2, NVENC Quality. Audio 48 kHz.

Mic filters top → bottom: RNNoise → (optional gate) → EQ → Compressor 3:1 → Limiter −1.5 dB.

Keep game audio and mic on separate tracks if you record. Discord never goes on those tracks.

## Audio (no Discord)

The installer mutes **Desktop Audio** on **both** the wide and vertical collections so Discord, Chrome, and other apps are not on the stream. You still hear them in your headset.

1. Mixer: **Desktop Audio** muted (speaker with an X).
2. **Mic / Main** = your mic. Unmuted.
3. **Audio / Game** = Application Audio Capture. Double-click it in **both** collections → pick **BeamNG.drive**.
4. Game Capture’s “Capture audio” is off so you do not get double game sound, and so Discord cannot sneak in through that checkbox.
5. Do not add Display/Desktop audio back. That is what pulls Discord in.

If you still hear Discord on VODs: Desktop Audio got unmuted. Mute it again. In Discord, you can keep output on your headset.

## Kick, Twitch, YouTube, TikTok, Instagram, Facebook, Discord

Edit `overlays/shared/config.js`. The `socials` object is the list that prints on Starting Soon, BRB, and Ending:

```
twitch: "jengland91"            // or "https://twitch.tv/jengland91"
youtube: "joshengland91"          // or "https://youtube.com/@joshengland91"
kick: "jengland91"              // or "https://kick.com/jengland91"
tiktok: "jengland91"
instagram: "jengland91"
facebook: "jengland91"
x: ""
discord: ""                    // leave blank for now
```

Save. In OBS: right-click the overlay source → Refresh. You do not need to re-run the installer just to change links.

## Change the game title on STARTING SOON

Easiest: double-click `tools/Change-Game.bat`, pick or type the game, then in OBS right-click `Overlay / Starting Soon` → Refresh (or click GRID and back to STARTING SOON). No installer re-run.

Same file if you prefer Notepad: `overlays/shared/config.js`. Change `game`. Starting Soon prints that as a big title, then `style` + `liveWord` as **Off-road. Live.** `startingKicker` is the small word above STARTING SOON (TRAILHEAD). Accent is `colors.ember` = `#7CB701`.

Optional URL override: `starting-soon.html?m=5&game=SnowRunner`.

## BeamNG capture

1. BeamNG: **borderless windowed**, native 1920×1080 if the PC can hold it.
2. Turn **Steam overlay** off for BeamNG (Steam → BeamNG → Properties → Overlay).
3. OBS source `Game / Main`: **Game Capture** → Capture specific window → `BeamNG.drive`.
4. Uncheck Capture Cursor.
5. If the source is **black** (common with Vulkan): change that source to **Window Capture**, method **Windows Graphics Capture**, pick BeamNG.

Do not use Display Capture unless both of those fail — it grabs your whole monitor.

In-game cameras (C, Shift+C, chase / hood / cockpit / orbit) are **not** extra OBS sources. They all come through `Game / Main`. Switch those with BeamNG, not OBS.

## Multi-cam (physical)

Typical off-road rig:

| Source | What it sees |
| --- | --- |
| `Game / Main` | BeamNG |
| `Cam / Face` | Close-up of you |
| `Cam / Room` | Face + room |
| `Cam / Wheel` | Hands / wheel |
| `Cam / Pedals` | Pedals |
| `Game / Angle 2` | Optional second BeamNG view |

### Second BeamNG angle

Only needed for `RACE DUAL`. Options:

- Second monitor with a BeamNG camera (external camera app, or a windowed second view if you use one)
- A bumper/hood window if you run a camera UI mod
- Skip Angle 2 and use Dual only when you actually have it — otherwise stay on `RACE` and swap in-game cameras

### USB

- Four capture devices on **different** USB controllers when you can (rear motherboard vs front/header)
- 720p 30fps per cam is plenty next to 1080p game
- Leave **Deactivate when not showing** **off** so Lumia/hotkey switches do not wait on USB reconnect

Create each cam once, then **Copy → Paste (Reference)** into the other scenes so OBS does not open the device twice.

Crop with **Alt + drag**. Matching Rec. 709 / Limited on the cams keeps skin from looking orange next to BeamNG.

## Source order — RACE (bottom → top)

1. `Game / Main`
2. `Audio / Game`
3. `Cam / Face`
4. `Cam / Room`
5. `Cam / Wheel`
6. `Cam / Pedals`
7. `Overlay / Race HUD` (`live.html`)
8. `Lumia / Overlay`
9. `Media / Hype Clip` (hidden)

## GRID

1. `Cam / Face` (large)
2. `Cam / Room`
3. `Cam / Wheel`
4. `Cam / Pedals`
5. `Overlay / Grid HUD`
6. `Lumia / Overlay`

## DESK (other games)

1. `Game / Main` (full)
2. `Audio / Game` (pick that game, not BeamNG)
3. `Cam / Face` (640×360 at 1256, 696)
4. `Overlay / Desk HUD` (`desk.html`)
5. `Lumia / Overlay`

No room / wheel / pedals. When you go back to racing, pick BeamNG on `Game / Main` and `Audio / Game` again, then click `RACE`.

## RACE DUAL

1. `Game / Main` (full)
2. `Game / Angle 2` (640×360 at 1248, 48)
3. `Cam / Face` / `Cam / Room` / `Cam / Wheel` / `Cam / Pedals` (small, bottom)
4. `Overlay / Dual HUD`
5. `Lumia / Overlay`

## REPLAY

1. `Game / Main` only
2. `Audio / Game`
3. `Overlay / Replay HUD`
4. `Lumia / Overlay` (alerts only is fine; hide the chatbox layer in Lumia for this scene if you can, or accept chat on the side)

## Vertical (1080×1920)

Collection **Rise Above BeamNG Vertical**. Game sits in a 16:9 strip (1080×608) at the top of RACE. Face, room, wheel, and pedals sit under that. Chat fills the phone-shaped remainder. Same **Desktop Audio muted + Audio / Game + Mic / Main** rules. Full numbers: [source-map.md](../obs/source-map.md).

To run wide and vertical **at the same time from OBS**, install [Aitum Vertical](https://aitum.tv/products/vertical) and [Aitum Multistream](https://aitum.tv/products/multi). Stay on collection **Rise Above BeamNG**. Run `tools/Install-AitumVertical.bat` (OBS 32.1+) to fill the Vertical Scenes dock. Destinations: [aitum.html](aitum.html).

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
| DESK | Numpad 8 |

Fade 300 ms. Lumia can fire the same scene changes from chat.

## Placement helper

`live.html?setup=1` and `vertical/live.html?setup=1` while lining up Lumia layers. Remove `setup=1` before going live.
