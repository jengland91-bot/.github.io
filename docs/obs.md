# OBS Studio — scene map

Canvas is **1920×1080**. Scene names are exact — Lumia Stream matches them as written.

## Video

Settings → Video:

| Field | Value |
| --- | --- |
| Base (Canvas) | 1920 × 1080 |
| Output (Scaled) | 1920 × 1080 |
| FPS | 60 if the PC can hold it, else 30 |
| Color Format | NV12 |
| Color Space | Rec. 709 |
| Color Range | Limited |

Settings → Output → Output Mode: **Advanced**

Twitch 1080p (typical cap):

| Field | NVIDIA | AMD | Intel | CPU |
| --- | --- | --- | --- | --- |
| Encoder | NVENC (new) | AMF | QuickSync | x264 |
| Rate control | CBR | CBR | CBR | CBR |
| Bitrate | 6000 Kbps | 6000 | 6000 | 4500–6000 |
| Keyframe | 2 | 2 | 2 | 2 |
| Preset | Quality / P5 | Quality | Quality | veryfast |
| Profile | High | High | High | high |
| B-frames | 2 | 2 | 2 | 2 |

YouTube can take more bitrate (8000–12000) if the uplink is clean.

Audio: **48 kHz**, AAC **160 Kbps** (stereo) or **160** on Track 1.

## Audio filters (mic)

Add these on **Mic / Main**, top to bottom:

1. **Noise Suppression** — RNNoise
2. **Noise Gate** — only if the room is noisy (open close to the noise floor)
3. **3-Band Equalizer** or **Advanced** — small cut around 200–300 Hz if it is boxy, slight presence at 4–6 kHz
4. **Compressor** — ratio 3:1, threshold so talking just kisses it, attack ~2 ms, release ~80 ms
5. **Limiter** — ceiling −1.5 dB

Keep desktop audio and mic on separate tracks if you record (Track 1 = stream mix, Track 2 = mic, Track 3 = game).

## Browser source defaults

Every overlay:

- Width **1920**, Height **1080**
- FPS 30
- Custom CSS:

```css
body { background-color: rgba(0, 0, 0, 0); margin: 0; overflow: hidden; }
```

- Shutdown source when not visible: **on** for STARTING SOON / BRB / ENDING / stinger
- Refresh browser when scene becomes active: **on** for STARTING SOON (restarts the countdown)
- Hardware acceleration: on

Use a **local file** pointing at this repo, or the GitHub Pages URL once Pages is enabled.

Starting Soon countdown length: `starting-soon.html?m=5` (minutes).

## Source order (bottom → top)

### LIVE

1. `Game / Capture` — Game Capture (Vulkan/DX) or Display Capture as fallback
2. `Cam / Main` — 360×270 at **X 48, Y 762**
3. `Casterlabs / Chat` — 400×460 at **X 1472, Y 560**
4. `Casterlabs / Now Playing` — 360×68 at **X 48, Y 678** (optional)
5. `Casterlabs / Labels` — 420×70 at **X 48, Y 96**
6. `Casterlabs / Goal` — 480×52 at **X 720, Y 1004**
7. `Overlay / Live HUD` — 1920×1080 at **0, 0** (`live.html`)
8. `Casterlabs / Alerts` — 860×200 at **X 530, Y 24**
9. `Casterlabs / Emoji Rain` — 1920×1080 at **0, 0** (optional)
10. `Lumia / Overlay` — 1920×1080 at **0, 0**
11. `Media / Hype Clip` — hidden. Lumia sets visibility for channel-point clips. Check **Restart playback when source becomes active** and **Close file when inactive**.

### JUST CHATTING

1. `Cam / Main` — 1100×619 at **X 56, Y 168** (16:9)
2. `Casterlabs / Chat` — 648×860 at **X 1216, Y 96**
3. `Casterlabs / Now Playing` — 420×68 at **X 56, Y 804**
4. `Casterlabs / Labels` — 420×70 at **X 56, Y 96**
5. `Casterlabs / Goal` — 480×52 at **X 366, Y 1004**
6. `Overlay / Chatting HUD` — `chatting.html`
7. `Casterlabs / Alerts` — 860×200 at **X 176, Y 24**
8. `Lumia / Overlay`

Right-click `Cam / Main` → **Copy** → in the other scene **Paste (Reference)** so both scenes share one camera.

Same for Casterlabs sources: **Paste (Reference)** so one widget URL is not duplicated as two independent browsers.

### STARTING SOON / BRB / ENDING / INTERMISSION

1. Color source `#07080C` full canvas (safety if the HTML fails)
2. Matching overlay HTML
3. Optional `Audio / Staging Music` (media source, loop, monitoring as needed)

## Hotkeys

Settings → Hotkeys:

| Scene | Suggested |
| --- | --- |
| STARTING SOON | Numpad 1 |
| JUST CHATTING | Numpad 2 |
| LIVE | Numpad 3 |
| BRB | Numpad 4 |
| ENDING | Numpad 5 |

Transition: **Fade 300 ms**. Skip a stinger until the rest is stable. `overlays/stinger.html` is there if you want a 1.1s ember wipe later.

## Docks (not on stream)

OBS → Docks → Custom Browser Docks. Paste Casterlabs Chat, Activity Feed, and Viewer List. Park them on a second monitor.

## Placement helper

Add `live.html?setup=1` (or `chatting.html?setup=1`) while lining up widgets. The wells light up with sizes. Switch the URL back to the version without `setup=1` before going live.
