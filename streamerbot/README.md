# Streamer.bot — clicks only (no code in Meld)

**You do not put code into Meld Studio.** Meld is import / drag-and-drop. Streamer.bot is also clicks: pick **Show Scene**, pick **RACE**.

The `.cs` file in this folder is optional. Skip it.

## Connect Meld (once)

1. Meld Studio → Settings → Advanced → **Allow remote connections**.
2. Streamer.bot → **Stream Apps** → **Meld Studio** → right-click → **Add**.
3. Host `127.0.0.1`. Auto Connect on. Connect.

## Make `!race` (repeat this pattern)

1. Streamer.bot → **Actions** → right-click → **Add**. Name it `Scene RACE`.
2. Add sub-action **Meld Studio** → **Show Scene**. Scene: `RACE`.
3. Add a **Command** trigger: `!race`. Enable it. Cooldown 3 seconds. Mods + you.

Do the same for the other scenes:

| Command | Show Scene |
| --- | --- |
| `!race` / `!live` | RACE |
| `!dual` | RACE DUAL |
| `!replay` | REPLAY |
| `!grid` | GRID |
| `!desk` | DESK |
| `!brb` | BRB |
| `!ending` | ENDING |
| `!starting` | STARTING SOON |

## Cam shots (also clicks)

New action `Cam Face`. Sub-actions **Meld Studio** → **Set Layer Visibility State**:

- `Cam / Face` = show
- `Cam / Room` = hide
- `Cam / Wheel` = hide
- `Cam / Pedals` = hide

Do that on scenes RACE, GRID, RACE DUAL, DESK (DESK only has Face + Room). Command: `!face`. Same idea for `!room` `!wheel` `!pedals` `!rig` (all show) `!game` (all hide).

Layer names in Meld must match exactly: `Cam / Face`, `Cam / Room`, `Cam / Wheel`, `Cam / Pedals`.

## You can skip Streamer.bot at first

Click the scene in Meld yourself. Add commands later when you want chat to switch scenes.

Official: [Meld + Streamer.bot](https://docs.streamer.bot/guide/stream-apps/meld-studio)
