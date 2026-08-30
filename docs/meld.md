# Meld Studio — import the session (no OBS)

You do not need OBS. Overlays are HTML. In Meld they are **Browser** layers.

## Fast path (import)

1. Extract the zip. Double-click `1-OPEN-IN-MELD.bat`.
2. That copies `Rise-Above-Meld.json` to your Desktop and opens Meld.
3. Meld → **File → Import Session** → `Rise-Above-Meld.json` on the Desktop.
4. You get eight scenes plus HUD / Social Stream / Lumia browser layers.
5. Add **Game Capture** (`Game / Main`) and **Video Device** cameras. Size them to the [layout board](../meld/index.html). Overlay stays on top.
6. Process Audio of the game + mic. No desktop / Discord.

## Drag and drop (if you skip import)

Open `DROP-INTO-MELD\`. Drag `RACE - Main.html` onto the Main canvas on scene RACE. Drag `RACE - Portrait.html` onto Portrait if Multi Canvas is on. Repeat per scene.

Or copy the overlay URL from the layout board and paste it onto the canvas.

Official: [Browser layers](https://meldstudio.co/docs/layers/) · [Import Session](https://meldstudio.co/docs/sessions/) · [Multi Canvas](https://meldstudio.co/docs/outputs/multi-canvas/)

## Overlay files

| Scene | Main | Portrait |
| --- | --- | --- |
| STARTING SOON | `overlays/starting-soon.html` | `overlays/vertical/starting-soon.html` |
| GRID | `overlays/chatting.html` | `overlays/vertical/chatting.html` |
| DESK | `overlays/desk.html` | `overlays/vertical/desk.html` |
| RACE | `overlays/live.html` | `overlays/vertical/live.html` |
| RACE DUAL | `overlays/race-dual.html` | `overlays/vertical/race-dual.html` |
| REPLAY | `overlays/replay.html` | `overlays/vertical/replay.html` |
| BRB | `overlays/brb.html` | `overlays/vertical/brb.html` |
| ENDING | `overlays/ending.html` | `overlays/vertical/ending.html` |

## Add-ons

- **Social Stream Ninja** — chat on stream. Session ID in `overlays/shared/config.js`. [Guide](socialstream.md)
- **Lumia** — alerts + lights. Chat-for-you on the gaming monitor. [Guide](lumia.md)
- **Streamer.bot** — optional. Clicks: Show Scene. No code in Meld. [Guide](streamerbot.md)

You do not put code into Meld. Click the scene in Meld, or later add Streamer.bot Show Scene commands.

## Do not

- Open OBS or run `Install-OBS.bat`
- Capture desktop / Discord
- Put stream keys in this repo
