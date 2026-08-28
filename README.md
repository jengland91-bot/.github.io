# Rise Above — OBS + Lumia + Casterlabs

A race-broadcast overlay kit wired for **OBS Studio**, **Lumia Stream** (lights + scene control), and **Casterlabs Caffeinated** (chat, alerts, labels, docks).

Open [the preview](index.html) or jump straight to the [setup checklist](setup.html).

## What you get

| Scene | Overlay | Job |
| --- | --- | --- |
| `STARTING SOON` | `overlays/starting-soon.html` | Countdown, socials, staging lights |
| `JUST CHATTING` | `overlays/chatting.html` | Big cam, tall chat, lower third |
| `LIVE` | `overlays/live.html` | Gameplay HUD, small cam, chat well |
| `BRB` | `overlays/brb.html` | Pit-stop hold screen |
| `ENDING` | `overlays/ending.html` | Checkered / thanks |

Setup mode (`?setup=1`) prints the exact wells where Casterlabs widgets and the webcam sit. Turn it off before you go live.

## Split the work so nothing double-fires

- **OBS** captures the game, cam, and mic. It is the layout.
- **Casterlabs** draws chat, alerts, goals, and labels on stream, plus docks only you see.
- **Lumia** drives lights, RGB overlay, and OBS actions (scene switch, show a clip). It does **not** also play the same follow/sub alert on screen.

## Customize

Edit `overlays/shared/config.js`:

- `name`, `brand`, `tagline`, `handle`
- `socials` (leave a platform blank to hide it)
- `colors.ember` for the accent
- `startingMinutes` (or append `?m=10` on the Starting Soon URL)

Then right-click the overlay Browser source in OBS → **Refresh**.

## Docs

- [OBS scenes, audio, encoding](docs/obs.html)
- [Casterlabs widgets, sizes, docks](docs/casterlabs.html)
- [Lumia connection and light recipes](docs/lumia.html)
- [Source map (names Lumia must match)](obs/source-map.md)

## Downloads

- [OBS Studio](https://obsproject.com/)
- [Casterlabs Caffeinated](https://casterlabs.co/)
- [Lumia Stream](https://lumiastream.com/)
