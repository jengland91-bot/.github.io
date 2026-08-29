# Rise Above — BeamNG kit (Meld / OBS / Lumia)

Off-road overlay kit for **BeamNG.drive** with **four cameras** (Face, Room, Wheel, Pedals). **Lumia Stream** for chat, alerts, lights. Casterlabs is not used. Tag is **@jengland91**.

Open [START-HERE.txt](START-HERE.txt).

- **Meld Studio** — [Import the OBS scenes](docs/meld.html) with File → Import OBS Session, then go live from Meld. Multi Canvas is the phone picture (no Aitum). Layout board: [meld/index.html](meld/index.html).
- **Twitch / YouTube / Kick + TikTok/Shorts from OBS** — OBS + [Aitum Multi + Vertical](docs/aitum.html). Stay on collection `Rise Above BeamNG`. Do not add Restream.
- **Chat for you** — Lumia on the gaming monitor, or `tools/Open-ChatForYou.bat`. Not a streaming app.

OBS (if you still use it, or as the import source for Meld) creates two scene collections:

- **Rise Above BeamNG** — 1920×1080. This is the collection Meld should import.
- **Rise Above BeamNG Vertical** — 1080×1920 if you stream phone-only from OBS with no wide canvas. With Aitum Vertical, stay on the wide collection. In Meld, use Multi Canvas instead of this collection.

Same scene names in both. Switch them with the dropdown at the top of OBS. Pick BeamNG on `Game / Main` and `Audio / Game` in both collections. Desktop Audio stays muted so Discord is not on the stream.

## Aitum (wide + phone from OBS)

[Aitum Multistream](https://aitum.tv/products/multi) sends extra sites. [Aitum Vertical](https://aitum.tv/products/vertical) is the 1080×1920 canvas. You need both. After Vertical is installed, run `tools/Install-AitumVertical.bat` (OBS 32.1+) to fill the Vertical Scenes dock. Guide: [Aitum Multi + Vertical](docs/aitum.html).

## Audio

- **Desktop Audio** muted
- **Audio / Game** = Application Audio Capture of BeamNG.drive
- **Mic / Main** = your mic

## Scenes

| OBS scene | Wide overlay | Vertical overlay | Job |
| --- | --- | --- | --- |
| `STARTING SOON` | `overlays/starting-soon.html` | `overlays/vertical/starting-soon.html` | Countdown, staging lights |
| `GRID` | `overlays/chatting.html` | `overlays/vertical/chatting.html` | Big face + room + wheel + pedals |
| `DESK` | `overlays/desk.html` | `overlays/vertical/desk.html` | Other games: full game + face + room, no wheel/pedals |
| `RACE` | `overlays/live.html` | `overlays/vertical/live.html` | BeamNG + four cams + chat |
| `RACE DUAL` | `overlays/race-dual.html` | `overlays/vertical/race-dual.html` | Main view + second angle |
| `REPLAY` | `overlays/replay.html` | `overlays/vertical/replay.html` | Clean game, no cams |
| `BRB` | `overlays/brb.html` | `overlays/vertical/brb.html` | Pit stop |
| `ENDING` | `overlays/ending.html` | `overlays/vertical/ending.html` | Checkered / thanks |

In-game BeamNG cameras (C / Shift+C) stay on one source: `Game / Main`. Physical cameras are `Cam / Face`, `Cam / Room`, `Cam / Wheel`, and `Cam / Pedals`. A second BeamNG view (other monitor, bumper window) is `Game / Angle 2` on `RACE DUAL` only. For other games, click `DESK`, then pick that game on `Game / Main` and `Audio / Game`. Switch both back to BeamNG when you go to `RACE`.

`?setup=1` on an overlay prints wells so you can park Lumia layers. Turn it off before going live.

## Who does what

- **Meld Studio** — go-live app if you switched off OBS. Import OBS scenes, then Multi Canvas for phone. [Meld guide](docs/meld.html)
- **OBS** — capture + layout if you stay in OBS, or the one-time source Meld imports
- **TikTok LIVE Studio** — Dual layout (phone + landscape). Overlay server + [layout board](tiktok-studio/index.html)
- **Lumia** — chatbox, alerts, goals, lights. Scene commands control OBS only, not Meld.

## Customize

Edit `overlays/shared/config.js` in Notepad, or double-click `tools/Change-Game.bat` to swap the Starting Soon game title (`BeamNG` → `SnowRunner` etc.). Also set `startingKicker` (TRAILHEAD), Monster green `colors.ember` (`#7CB701`), and `socials`. Save, then in OBS right-click the overlay → **Refresh**, in Meld refresh the Browser overlay, or in TikTok LIVE Studio refresh the Link sources. Camera wells in OBS only move if you download a new zip and re-run `tools/Install-OBS.bat`. Then in Meld: File → Import OBS Session again if you want those new positions.

### Your photos on Starting Soon / BRB / Ending

Drop `starting.jpg`, `brb.jpg`, and `ending.jpg` into `overlays/shared/backdrops/` (see that folder’s START-HERE). Same three files cover wide and vertical. Optional `starting-vertical.jpg` / `brb-vertical.jpg` / `ending-vertical.jpg` if you want a separate 9:16 crop. Then OBS → right-click overlay → **Refresh**, or in Meld refresh the Browser overlay. No installer re-run. Missing files keep the dark dirt background.

## Docs

- [Meld Studio — import scenes](docs/meld.html)
- [OBS + BeamNG + multi-cam](docs/obs.html)
- [Aitum Multi + Vertical](docs/aitum.html)
- [Lumia / chat for you](docs/lumia.html)
- [Source map](obs/source-map.md)
