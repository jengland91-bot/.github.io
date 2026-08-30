# Streamer.bot — Meld scene + cam commands

Chat commands switch **Meld Studio** (not OBS). Import is copy-paste: Streamer.bot cannot load a raw `.cs` file, so you paste this into one action.

## Connect Meld

1. Open Meld Studio → Settings → Advanced → **Allow remote connections**.
2. Open Streamer.bot → **Stream Apps** → **Meld Studio**.
3. Right-click → **Add**. Host `127.0.0.1`. Name it `Local Meld`. Auto Connect on. Connect.

The status panel should show the current scene once Meld is open with the Rise Above session imported.

## One action

1. Streamer.bot → **Actions** → right-click → **Add**. Name: `Rise Above · Meld Router`.
2. Add sub-action **Core** → **C#** → **Execute C# Code**.
3. Paste everything in `Rise-Above-Meld.cs`. Compile. Save.

## Commands (triggers)

In **Commands** (or on the action, add **Command** triggers). Enable each one. Cooldown as listed. Suggested: **Mods + Broadcaster** for scene switches, **Everyone** for cam shots.

| Command | Cooldown | What it does |
| --- | --- | --- |
| `!race` / `!live` | 3s | Scene → RACE |
| `!dual` | 3s | Scene → RACE DUAL |
| `!replay` | 3s | Scene → REPLAY |
| `!grid` | 3s | Scene → GRID |
| `!desk` | 3s | Scene → DESK |
| `!brb` | 8s | Scene → BRB |
| `!ending` | 8s | Scene → ENDING |
| `!starting` | 8s | Scene → STARTING SOON |
| `!face` | 15s | Face cam only |
| `!room` | 15s | Room cam only |
| `!wheel` | 15s | Wheel cam only |
| `!pedals` | 15s | Pedals cam only |
| `!rig` | 15s | All cams on |
| `!game` | 15s | Hide cams (game only) |

Each command runs the **same** `Rise Above · Meld Router` action.

Cam commands need the layers named exactly `Cam / Face`, `Cam / Room`, `Cam / Wheel`, `Cam / Pedals` in Meld.

## Platforms

Add Twitch (and YouTube / Kick if you use them) under **Platforms** in Streamer.bot so commands arrive from chat. Social Stream Ninja does **not** replace this — SSN is the on-screen chat look. Streamer.bot is the brain.

## Lumia lights

Lumia does not talk to Meld the way it talks to OBS. Lights that follow the scene: in Streamer.bot, add a **Meld Studio → Scene Changed** trigger that calls a Lumia HTTP command, **or** keep lights on a default Monster green and fire alert flashes from Lumia only. Alerts still come from Lumia’s overlay URL.

Official: [Meld + Streamer.bot](https://docs.streamer.bot/guide/stream-apps/meld-studio) · [Import](https://docs.streamer.bot/guide/core/import-export)
