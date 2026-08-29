# Aitum Multi + Vertical — Rise Above

Stay in OBS. Do not add Restream. Do not run TikTok LIVE Studio at the same time as OBS → TikTok.

You need **two** plugins:

- [Aitum Multistream](https://aitum.tv/products/multi) — extra destinations
- [Aitum Vertical](https://aitum.tv/products/vertical) — 1080×1920 canvas (or Stream Suite, which includes both)

Stay on **Rise Above BeamNG**. Install [Aitum Vertical](https://aitum.tv/products/vertical), reopen OBS, then run `tools/Install-AitumVertical.bat` (OBS 32.1+). That fills the **Vertical Scenes** dock with the seven phone scenes. Right-click each → Linked Scenes → matching wide scene.

If Vertical Scenes is missing: Multistream is not enough — install Vertical, then OBS → Docks → Vertical Scenes / Vertical Sources / Aitum Vertical.

## Where each picture goes

| Canvas | Aitum | Platforms |
| --- | --- | --- |
| 1920×1080 | OBS Stream + Main Outputs | Twitch, YouTube, Kick, Facebook |
| 1080×1920 | Vertical Outputs | TikTok, YouTube vertical / Shorts live |

Keys stay in the dashboards (Twitch creator, YouTube Studio, Kick dashboard, TikTok LIVE Center). Never paste keys into this repo.

TikTok needs a LIVE stream key. No key = skip TikTok in Aitum. Aitum cannot send wide + vertical to TikTok at the same time; send the phone canvas to TikTok.

## Chat

Lumia on the gaming monitor, or `tools/Open-ChatForYou.bat`. Not a second streaming app.
