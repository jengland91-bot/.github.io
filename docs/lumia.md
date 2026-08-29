# Lumia Stream — chat for you

You want one chat box on the **gaming monitor** so you can read it. That is not chat on the stream for viewers.

Open [tools/chat-for-you.html](../tools/chat-for-you.html) or double-click `tools/Open-ChatForYou.bat`.

1. Lumia → Connections → Twitch (and Kick / YouTube). One Chatbox = all that chat. Leave Lumia running.
2. Do **not** paste a Chatbox into OBS if viewers should not see it. Leave `Lumia / Overlay` blank or Alerts only.
3. Drag the Lumia window onto the BeamNG monitor, or paste the overlay URL into Chat for you → Open chat window, then drag that window over.
4. Do not Game Capture that window in OBS.

If you already put chat in `Lumia / Overlay`, hide that source or remove the Chatbox from the overlay.

Connect guide: [Lumia + OBS](https://lumiastream.com/blogs/how-to-integrate-obs-streaming-software-with-lumia-stream)

## One overlay, not five browser sources

Only if you also want **viewers** to see chat or alerts. In Lumia’s overlay editor, build **one** overlay named something like `Rise Above Race`:

| Layer | Put it here (RACE) |
| --- | --- |
| Chatbox | 384×500 at **1488, 520** |
| Alerts | 860×200 at **530, 24** |
| Event list / labels | 420×70 at **48, 96** |
| Now Playing | 400×64 at **48, 800** |
| Goal | optional; skip on RACE if it covers the cams |

Colors: text `#E8DCC8`, accent Monster green `#7CB701`, backgrounds transparent or a light dark glass.

Copy the overlay URL once. OBS source `Lumia / Overlay`, 1920×1080 on the wide collection, 1080×1920 on the vertical collection, **above** the Rise Above HUD.

Vertical RACE chatbox: **1048×800 at 16, 1096**. Alerts: **1048×160 at 16, 16**. Duplicate the Lumia overlay for 9:16 if chat looks stretched; or keep one URL and park layers on the vertical wells.

GRID and RACE DUAL use different wells — either duplicate the overlay in Lumia with those positions, or keep one overlay and accept that chat sits in the RACE pocket on every scene (still readable). Two Lumia overlays (Race / Grid) is cleaner if the editor allows switching with the scene.

## Scene lights (Alerts → OBS)

| Scene | Light |
| --- | --- |
| `STARTING SOON` | Moss / trail green, slow breathe |
| `GRID` | Soft moss / white, face-friendly |
| `RACE` | Monster green `#7CB701` |
| `RACE DUAL` | Pine + a bit of moss on a second zone if you have one |
| `REPLAY` | Dim olive |
| `BRB` | Dim forest, 30–40% |
| `ENDING` | Dusk gold-olive pulse, then house white on stream stop |

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
