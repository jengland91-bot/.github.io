# Casterlabs Caffeinated

Caffeinated owns **on-stream** chat, alerts, labels, and goals. It also owns the **docks** you read while live. Keep Caffeinated running on the same PC as OBS.

Docs: [Widgets & Alerts](https://docs.casterlabs.co/caffeinated/widgets-alerts/) · [Docks](https://docs.casterlabs.co/caffeinated/docks)

## Accounts

Settings → Accounts: connect every platform you actually stream to. Chat and alerts can then be **combined** (one widget, all platforms) which is what this kit expects.

YouTube: channel subscribers count as **Followers** in Caffeinated. Channel members count as **Subscribers**.

## Match the overlay

Install **Rajdhani** (Google Fonts) on Windows if you want the HUD type. Caffeinated can use any font installed on the PC.

| Token | Value |
| --- | --- |
| Text | `#F4EFE8` |
| Highlight (usernames) | `#FF4D1A` |
| Ice accent (optional) | `#5CE1E6` |
| Background | fully transparent |
| Outline | 1–2 px dark |
| Shadow | on |

## Widgets to create

Give them these names inside Caffeinated so the copied URLs stay identifiable. Then use the **same names** on the OBS Browser sources.

| Caffeinated widget | OBS source name | LIVE size / pos | JUST CHATTING size / pos |
| --- | --- | --- | --- |
| Alerts (all platforms, all event types you want) | `Casterlabs / Alerts` | 860×200 at 530, 24 | 860×200 at 176, 24 |
| Chat | `Casterlabs / Chat` | 400×460 at 1472, 560 | 648×860 at 1216, 96 |
| Recent Follower label | `Casterlabs / Labels` | 420×70 at 48, 96 | 420×70 at 56, 96 |
| Goal (followers or subs) | `Casterlabs / Goal` | 480×52 at 720, 1004 | 480×52 at 366, 1004 |
| Now Playing | `Casterlabs / Now Playing` | 360×68 at 48, 678 | 420×68 at 56, 804 |
| Emoji Rain | `Casterlabs / Emoji Rain` | 1920×1080 at 0, 0 | same |

You can split Recent Follow and Recent Sub into two 210×70 sources sitting side by side in the labels well.

### Alerts

Create **one** combined alert set (Follow, Sub, Donation, Raid) unless you truly want per-platform art. Unique names if you split them.

- Duration: 6–8 seconds
- Donation TTS: optional, keep it quieter than your mic
- Raid: Twitch and Kick only in Caffeinated today

Copy the widget URL (link icon) → OBS Browser source. Do not also fire the same alert as a Lumia on-screen graphic.

### Chat

- Message style: **Bottom-up**
- LIVE: make messages disappear after ~20 seconds so the well stays readable over gameplay
- JUST CHATTING: leave messages on longer or persistent
- Show platform icons: **on**
- Badges: on
- Events in chat: follow/sub/raid **off** if the alert widget already covers them (stops double on-screen spam)

### Docks (operator only)

In Caffeinated, Docks tab → copy URL.

OBS → Docks → Custom Browser Docks:

- `Chat`
- `Activity Feed`
- `Viewer List`

These need Caffeinated running. They will not work on a second PC that does not have Caffeinated.

## Paste as Reference

After the widgets exist in LIVE, copy each Casterlabs source and **Paste (Reference)** into JUST CHATTING, then change only the transform (size/position). One browser process per widget.

## Test

Caffeinated has test/send controls on each widget. Fire a follow while OBS is on LIVE and on JUST CHATTING. Confirm the alert sits in the dashed well, not over your face.
