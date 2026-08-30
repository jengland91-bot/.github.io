# Rise Above — BeamNG kit (Meld Studio)

Off-road overlay kit for **BeamNG.drive** with **four cameras** (Face, Room, Wheel, Pedals). Go live from **Meld Studio**. **Lumia Stream** for alerts and lights. **Streamer.bot** for `!race` / `!face`. **Social Stream Ninja** for chat on stream. Tag is **@jengland91**.

Open [START-HERE.txt](START-HERE.txt). Apps you need: [apps.html](apps.html) / [APPS.md](APPS.md).

## Drag and drop (Meld)

1. Download **only** `IMPORT-THIS-IN-MELD.json` (see [GET-THE-KIT.txt](GET-THE-KIT.txt)). Windows will not block a JSON file.
2. In Meld: **File → Import Session** → that file. You should see STARTING SOON. Overlays load from the internet.
3. If Meld crashed from the old bat: **File → Restore from Backup**, then Import Session.
4. Add Game Capture + four Video Device cameras. Size them on the [layout board](meld/index.html).

Guides: [Meld](docs/meld.html) · [Social Stream Ninja](docs/socialstream.html) · [Streamer.bot](docs/streamerbot.html) · [Lumia](docs/lumia.html)

## Who does what

| App | On the picture | For you |
| --- | --- | --- |
| Meld Studio | Game, cameras, go-live | Scenes |
| This kit | HUD, Starting Soon, BRB, Ending | Layout board |
| Social Stream Ninja | Chat + featured shoutouts | Dock |
| Lumia Stream | Alerts + lights | Chat-for-you on the gaming monitor |
| Streamer.bot | Nothing visual | Optional `!race` `!brb` `!face` → Meld (clicks, not code) |

## Scenes

| Scene | Wide overlay | Vertical overlay | Job |
| --- | --- | --- | --- |
| `STARTING SOON` | `overlays/starting-soon.html` | `overlays/vertical/starting-soon.html` | Countdown, staging lights |
| `GRID` | `overlays/chatting.html` | `overlays/vertical/chatting.html` | Big face + room + wheel + pedals |
| `DESK` | `overlays/desk.html` | `overlays/vertical/desk.html` | Other games: full game + face + room, no wheel/pedals |
| `RACE` | `overlays/live.html` | `overlays/vertical/live.html` | BeamNG + four cams + chat |
| `RACE DUAL` | `overlays/race-dual.html` | `overlays/vertical/race-dual.html` | Main view + second angle |
| `REPLAY` | `overlays/replay.html` | `overlays/vertical/replay.html` | Clean game, no cams |
| `BRB` | `overlays/brb.html` | `overlays/vertical/brb.html` | Pit stop |
| `ENDING` | `overlays/ending.html` | `overlays/vertical/ending.html` | Checkered / thanks |

## Customize

Edit `overlays/shared/config.js` in Notepad, or double-click `tools/Change-Game.bat` for the Starting Soon title. Paste Social Stream Ninja `ssn.session` and optional `lumia.overlayUrl` in that same file. Drop `starting.jpg` / `brb.jpg` / `ending.jpg` in `overlays/shared/backdrops/`. Then reload the Browser layers in Meld.

## Audio

Process Audio of BeamNG + your mic. Do not capture desktop / Discord.
