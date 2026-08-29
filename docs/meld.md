# Meld Studio — put the Rise Above scenes in Meld

Yes. Meld can take the same eight scenes. Fastest path is **File → Import OBS Session** after the OBS kit is installed. Overlay HTML does not change. Aitum is not used in Meld — turn on **Multi Canvas** for the phone picture.

Layout board: [meld/index.html](../meld/index.html) or `tools/Open-MeldLayout.bat`.

Official docs: [Sessions](https://meldstudio.co/docs/sessions/) · [Multi Canvas](https://meldstudio.co/docs/outputs/multi-canvas/)

## Path A — import OBS

1. Extract the zip. If OBS is empty, run `tools/Install-OBS.bat`.
2. OBS collection dropdown = **Rise Above BeamNG** (1920×1080). Do not switch to **Rise Above BeamNG Vertical**.
3. File → Save in OBS. Close OBS. Do not go live from OBS and Meld to the same site at the same time.
4. Meld → **File → Import OBS Session**. That imports the most recently saved OBS session. Meld backs up your current Meld session first.
5. You should see STARTING SOON, GRID, DESK, RACE, RACE DUAL, REPLAY, BRB, ENDING.
6. Missing Source Assistant (warning icon, bottom left): pick BeamNG, the four cameras, and your mic. One fix updates every scene that uses that layer.
7. Audio = game process + mic. No desktop / Discord.
8. If a Browser overlay is blank, browse to the HTML in this extracted folder.

Import only brings the **wide** collection. The vertical OBS collection is a second OBS show. For phone in Meld: **Settings → General → Multi Canvas**, then build Portrait layers from the layout board (`overlays/vertical/*.html`).

## Path B — no OBS

Skip the installer. Open the layout board. In Meld add the eight scene names. Drag overlay HTML onto the canvas. Size game and cameras to the X / Y / W / H on the board.

`tools/Start-MeldLayout.bat` serves `http://127.0.0.1:5500/` if you want URL browser layers instead of local files.

## Scenes

| Scene | Main overlay | Portrait overlay |
| --- | --- | --- |
| STARTING SOON | `overlays/starting-soon.html` | `overlays/vertical/starting-soon.html` |
| GRID | `overlays/chatting.html` | `overlays/vertical/chatting.html` |
| DESK | `overlays/desk.html` | `overlays/vertical/desk.html` |
| RACE | `overlays/live.html` | `overlays/vertical/live.html` |
| RACE DUAL | `overlays/race-dual.html` | `overlays/vertical/race-dual.html` |
| REPLAY | `overlays/replay.html` | `overlays/vertical/replay.html` |
| BRB | `overlays/brb.html` | `overlays/vertical/brb.html` |
| ENDING | `overlays/ending.html` | `overlays/vertical/ending.html` |

DESK = sit-at-desk other games (full game + face + room, no wheel/pedals). Switch Game and Process Audio to that game; switch both back to BeamNG for RACE.

## Lumia

Chat for you: Lumia on the gaming monitor, or `tools/Open-ChatForYou.bat`. Do not capture that window.

Viewer alerts: Lumia URL as a Browser layer above the HUD.

`!race` / `!desk` / `!face` control OBS only. Switch scenes in Meld.

## Do not

- Stream the same destination from OBS and Meld at once
- Import the OBS Vertical collection as Main
- Expect Aitum plugins to appear
- Put stream keys in this repo
