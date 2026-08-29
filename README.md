# Rise Above — BeamNG OBS + Lumia

Off-road overlay kit for **BeamNG.drive** with **four cameras** (Face, Room, Wheel, Pedals) plus **Lumia Stream** for chat, alerts, lights, and camera switching. Casterlabs is not used. Tag is **@jengland91**.

Open [START-HERE.txt](START-HERE.txt). Two apps:

- **TikTok** — TikTok LIVE Studio only. Double-click `tools/Start-TikTokLayout.bat`. Build Dual layout from the [layout board](tiktok-studio/index.html). Do not open OBS.
- **Twitch / YouTube / Kick** — OBS. Double-click `tools/Install-OBS.bat`.

OBS creates two scene collections:

- **Rise Above BeamNG** — 1920×1080 for Twitch / YouTube / Kick
- **Rise Above BeamNG Vertical** — 1080×1920 for YouTube Shorts / Reels if you use OBS for those (TikTok is Studio)

Same scene names in both. Switch them with the dropdown at the top of OBS. Pick BeamNG on `Game / Main` and `Audio / Game` in both collections. Desktop Audio stays muted so Discord is not on the stream.

## TikTok LIVE Studio

TikTok is Studio only. Double-click `tools/Start-TikTokLayout.bat`, leave it open, and build Dual layout from the [layout board](tiktok-studio/index.html). Add sources on the phone canvas first, then resize on landscape. One overlay URL per scene. Do not run `Install-OBS.bat` for TikTok. Guide: [TikTok LIVE Studio](docs/tiktok.html).

## Audio

- **Desktop Audio** muted
- **Audio / Game** = Application Audio Capture of BeamNG.drive
- **Mic / Main** = your mic

## Scenes

| OBS scene | Wide overlay | Vertical overlay | Job |
| --- | --- | --- | --- |
| `STARTING SOON` | `overlays/starting-soon.html` | `overlays/vertical/starting-soon.html` | Countdown, staging lights |
| `GRID` | `overlays/chatting.html` | `overlays/vertical/chatting.html` | Big face + room + wheel + pedals |
| `RACE` | `overlays/live.html` | `overlays/vertical/live.html` | BeamNG + four cams + chat |
| `RACE DUAL` | `overlays/race-dual.html` | `overlays/vertical/race-dual.html` | Main view + second angle |
| `REPLAY` | `overlays/replay.html` | `overlays/vertical/replay.html` | Clean game, no cams |
| `BRB` | `overlays/brb.html` | `overlays/vertical/brb.html` | Pit stop |
| `ENDING` | `overlays/ending.html` | `overlays/vertical/ending.html` | Checkered / thanks |

In-game BeamNG cameras (C / Shift+C) stay on one source: `Game / Main`. Physical cameras are `Cam / Face`, `Cam / Room`, `Cam / Wheel`, and `Cam / Pedals`. A second BeamNG view (other monitor, bumper window) is `Game / Angle 2` on `RACE DUAL` only.

`?setup=1` on an overlay prints wells so you can park Lumia layers. Turn it off before going live.

## Who does what

- **OBS** — Twitch / YouTube / Kick capture, four cams, layout, audio
- **TikTok LIVE Studio** — Dual layout (phone + landscape). Overlay server + [layout board](tiktok-studio/index.html)
- **Lumia** — chatbox, alerts, goals, lights. Scene commands control OBS only.

## Customize

Edit `overlays/shared/config.js` in Notepad: `game` (BeamNG → SnowRunner etc.), `startingKicker` (TRAILHEAD), Monster green `colors.ember` (`#7CB701`), and `socials`. Save, then in OBS right-click the overlay → **Refresh**, or in TikTok LIVE Studio refresh the Link sources. Camera wells in OBS only move if you download a new zip and re-run `tools/Install-OBS.bat`.

### Your photos on Starting Soon / BRB / Ending

Drop `starting.jpg`, `brb.jpg`, and `ending.jpg` into `overlays/shared/backdrops/` (see that folder’s START-HERE). Same three files cover wide and vertical. Optional `starting-vertical.jpg` / `brb-vertical.jpg` / `ending-vertical.jpg` if you want a separate 9:16 crop. Then OBS → right-click overlay → **Refresh**. No installer re-run. Missing files keep the dark dirt background.

## Docs

- [OBS + BeamNG + multi-cam](docs/obs.html)
- [TikTok LIVE Studio layout](tiktok-studio/index.html)
- [TikTok LIVE Studio](docs/tiktok.html)
- [Lumia overlay, lights, cam director](docs/lumia.html)
- [Source map](obs/source-map.md)
