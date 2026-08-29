# Meld Studio only — plug the kit in (no OBS)

You do not need OBS. The overlays are HTML files. In Meld they are **Browser** layers.

1. Extract the zip. Open Meld. Do not open OBS.
2. Double-click `tools/Start-MeldLayout.bat` and leave it open.
3. Add eight scenes: STARTING SOON, GRID, DESK, RACE, RACE DUAL, REPLAY, BRB, ENDING. Start with RACE.
4. Settings → General → **Multi Canvas** for the phone picture.
5. On the [layout board](../meld/index.html), copy the overlay URL and paste it onto that Meld canvas (or drag the HTML file from `overlays\` / `overlays/vertical\`).
6. Add Game Capture (BeamNG) and Video Device cameras. Size them to the board. Process Audio of the game + mic. No desktop / Discord.

Layout board: [meld/index.html](../meld/index.html)

Official: [Browser layers](https://meldstudio.co/docs/layers/) · [Multi Canvas](https://meldstudio.co/docs/outputs/multi-canvas/)

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

## Lumia

Chat for you: Lumia on the gaming monitor, or `tools/Open-ChatForYou.bat`. Do not capture that window.

`!race` does not switch Meld. Click the scene in Meld.

## Do not

- Open OBS or run `Install-OBS.bat`
- Capture desktop / Discord
- Put stream keys in this repo
