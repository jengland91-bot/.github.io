# Social Stream Ninja — chat on the stream

Viewers see **Social Stream Ninja**. You still read chat on the gaming monitor with **Lumia** (or the SSN dock). Do not put two chat boxes in the same pocket.

## Install

1. Chrome / Edge: [socialstream.ninja](https://socialstream.ninja/) → install the extension.
   Or download the desktop app from the same site.
2. Open Twitch / YouTube / Kick / TikTok chat. Click the icon → Enable.
3. Copy the **session ID**. Same ID everywhere.

## Plug into this kit

1. Paste the session ID into `overlays/shared/config.js` → `ssn.session`.
2. Save. In Meld, reload **Social Stream / Chat** and **Social Stream / Featured**.
3. Those layers are already in `meld/Rise-Above-Meld.json`. Chat is sized to the HUD well. Featured is full-screen (click a message in the dock to shout it out).

Layout board: [socialstream/index.html](../socialstream/index.html)

## Dock (for you)

`https://socialstream.ninja/dock.html?session=YOUR_ID`

Keep this on a side monitor. Click a message to send it to Featured. Do not Game Capture the dock.

## If chat is blank

- Dock empty? The source tab / app is not capturing chat yet. Fix that first.
- Dock has messages, Meld is empty? Session ID mismatch. Same string in config.js and the extension.
- Reload the Browser layer after saving config.js.
- Leave `Start-MeldLayout.bat` running.

Official: [OBS quick start](https://socialstream.ninja/docs/obs-quick-start.html) (same Browser URL idea as Meld).
