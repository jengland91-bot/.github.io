# Aitum Multi + Vertical — Rise Above

Stay in OBS. Do not add Restream. Do not run TikTok LIVE Studio at the same time as OBS → TikTok.

You need **two** plugins:

- [Aitum Multistream](https://aitum.tv/products/multi) — extra destinations
- [Aitum Vertical](https://aitum.tv/products/vertical) — 1080×1920 canvas (or Stream Suite, which includes both)

Stay on collection **Rise Above BeamNG**. Vertical is a second canvas inside that collection.

## Docks

OBS → Docks: Aitum Multistream, Aitum Vertical, Vertical Scenes, Vertical Sources.

## Phone canvas

Vertical size 1080×1920. Same seven scene names. RACE: game 1080×608 at 0,0; four cams under it; `overlays/vertical/live.html` 1080×1920. Add **existing** sources (do not duplicate cameras). Right-click Vertical scene → Linked Scenes → matching wide scene.

## Where each picture goes

| Canvas | Aitum | Platforms |
| --- | --- | --- |
| 1920×1080 | OBS Stream + Main Outputs | Twitch, YouTube, Kick, Facebook |
| 1080×1920 | Vertical Outputs | TikTok, YouTube vertical / Shorts live |

Keys stay in the dashboards (Twitch creator, YouTube Studio, Kick dashboard, TikTok LIVE Center). Never paste keys into this repo.

TikTok needs a LIVE stream key. No key = skip TikTok in Aitum. Aitum cannot send wide + vertical to TikTok at the same time; send the phone canvas to TikTok.

## Chat

Lumia on the gaming monitor, or `tools/Open-ChatForYou.bat`. Not a second streaming app.
