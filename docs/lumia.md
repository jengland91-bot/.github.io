# Lumia Stream — chat for you

You want one chat box on the **gaming monitor** so you can read it. That is not chat on the stream for viewers.

**On stream, viewers see Social Stream Ninja** — not the Lumia Chatbox. Lumia on the stream is alerts (and lights). Streamer.bot switches Meld scenes (`!race`). See [apps.html](../apps.html).

Open [tools/chat-for-you.html](../tools/chat-for-you.html) or double-click `tools/Open-ChatForYou.bat`.

1. Lumia → Connections → Twitch (and Kick / YouTube). One Chatbox = all that chat. Leave Lumia running.
2. Do **not** put a Chatbox on the Meld Lumia overlay if viewers should not see it. Alerts only on stream.
3. Drag the Lumia window onto the BeamNG monitor, or paste the overlay URL into Chat for you → Open chat window, then drag that window over.
4. Do not capture that window in Meld.

If you already put chat in `Lumia / Overlay`, hide that layer or remove the Chatbox from the overlay.

## Viewer alerts (optional)

In Lumia’s overlay editor, build **one** overlay named something like `Rise Above Race`. Put Alerts (and optional Event list / Now Playing) on the wells. Copy the overlay URL into `overlays/shared/config.js` → `lumia.overlayUrl`. Reload the Lumia / Overlay Browser layer in Meld. It sits above the HUD.

| Layer | Put it here (RACE) |
| --- | --- |
| Alerts | 860×200 at **530, 24** |
| Event list / labels | 420×70 at **48, 96** |
| Now Playing | 400×64 at **48, 800** |

Colors: text `#E8DCC8`, accent Monster green `#7CB701`, backgrounds transparent.

Chat on stream is Social Stream Ninja, not the Lumia Chatbox.

## Scene lights (optional)

Set these in Lumia. Streamer.bot can fire a Lumia command when you switch Meld scenes.

| Scene | Light |
| --- | --- |
| `STARTING SOON` | Moss / trail green, slow breathe |
| `GRID` | Soft moss / white, face-friendly |
| `DESK` | Moss (sit at desk, other games) |
| `RACE` | Monster green `#7CB701` |
| `RACE DUAL` | Pine + a bit of moss on a second zone if you have one |
| `REPLAY` | Dim olive |
| `BRB` | Dim forest, 30–40% |
| `ENDING` | Dusk gold-olive pulse |

Follow/sub in Lumia: **on-screen alert + a 2s light flash**.

## Camera director (Streamer.bot → Meld)

Clicks in Streamer.bot: Show Scene, or Set Layer Visibility State. No code in Meld. See [streamerbot.md](streamerbot.md).

## Troubleshooting

- Blank overlay: recopy the URL into config.js; Lumia app must be running; overlay server window still open
- Cam freeze: USB bandwidth — drop to 720p, different ports
- BeamNG black: Game Capture → Display Capture of the BeamNG window
