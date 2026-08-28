# Lumia Stream

Lumia owns **lights**, the **RGB overlay**, and **OBS actions** (scene changes, showing a clip). Casterlabs still owns the on-screen follow/sub/donation alert.

Guide: [Connect OBS](https://lumiastream.com/blogs/how-to-integrate-obs-streaming-software-with-lumia-stream)

## Connect OBS

1. OBS 28+ → Tools → **WebSocket Server Settings**
2. Enable server, port **4455**, authentication **on**
3. Copy the password
4. Lumia → Connections → Add → **OBS**
5. Host `localhost` (or `127.0.0.1`), port `4455`, paste password → Connect

OBS 27 and older need the WebSocket plugin. Update OBS instead.

## Lights

Same Connections page: add Hue, Nanoleaf, Govee, WLED, Twinkly, plugs, etc.

## Overlay in OBS

Lumia → overlay / room URL (looks like `https://lumiastream.com/overlay?room=…`).

OBS Browser source:

- Name: `Lumia / Overlay`
- 1920×1080
- Transparent CSS (same as the HUD)
- Place **above** the Rise Above HUD on LIVE and JUST CHATTING

If the Lumia overlay includes its own chat/alerts, turn those layers off in Lumia and leave Casterlabs in charge. Use Lumia overlay for RGB frames, HFX, and light-reactive art.

## Scene lights (Alerts → OBS)

Create an OBS-scene alert for each scene name. Scene names must match OBS exactly.

| Scene | Light feel |
| --- | --- |
| `STARTING SOON` | Warm amber, slow breathe. Staging. |
| `JUST CHATTING` | Soft ice / white, low saturation. Face-friendly. |
| `LIVE` | Ember `#FF4D1A`, a bit more intensity. |
| `BRB` | Dim cool blue, 30–40% brightness. |
| `ENDING` | Gold pulse, then a slow fade you can trigger on stream stop. |

Also useful:

- **Stream start** → LIVE colors + a short TTS “we’re live” only in your headphones if you want it
- **Stream stop** → lights to house/white so you are not sitting in red after the raid

## Chat / points → OBS (do not duplicate Casterlabs alerts)

Under a command or Twitch points redemption, add **OBS actions**:

### `!brb` / a “BRB” point redeem

1. Set current scene → `BRB`
2. Lights to BRB look
3. End tab (or a second redeem `!live`): scene → `LIVE`

### Hype clip (channel points)

OBS source `Media / Hype Clip` (hidden by default), Restart when active.

On the redeem:

1. Start: Set source visibility **on** — scene `LIVE`, source `Media / Hype Clip`
2. Delay = clip length
3. End: visibility **off**

Same pattern works for a PNG meme.

### Chat camera zoom (optional)

OBS action: Set scene item transform on `Cam / Main`, then revert after N seconds. Easy to overdo — test offline.

## Commands worth adding

Keep cooldowns honest so lights are not strobing.

| Command | Action |
| --- | --- |
| `!lights` | Cycle a safe accent (ember / ice / sand) |
| `!brb` | Scene `BRB` |
| `!live` | Scene `LIVE` |
| `!chat` | Scene `JUST CHATTING` |

User levels: everyone for `!lights` with a 30s cooldown; mods for scene switches if you do not want random scene changes.

## Follow / sub in Lumia

Use those events for **lights only** (flash ember 2s, return to LIVE color). Do **not** also enable Lumia’s on-screen alert if Casterlabs is already showing it.

## Troubleshooting

- Lumia cannot see scenes: OBS is closed, WebSocket off, or wrong password/port.
- Overlay blank in OBS: room URL stale — recopy from Lumia. Confirm Caffeinated is not required here; Lumia overlay needs the Lumia app running.
- Double alerts: disable on-screen alerts in one of the two apps.
- Scene switch does nothing: source/scene name mismatch (spaces, caps). Copy from [source-map.md](../obs/source-map.md).
