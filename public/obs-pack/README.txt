J England OBS pack
==================

1. OBS Studio 31+ from https://obsproject.com
2. Scene Collection → Import → this file (J-England.json)
3. Switch to the collection named "J England"
4. Video: 1920x1080, 60 fps
5. Stream (built-in): Twitch
6. Replace sources inside the nested scenes whose names start with "•"
7. Paste Lumia overlay URLs into the four "Lumia ·" browser sources
8. Aitum Multistream / Stream Suite:
   - Main outputs: Kick + YouTube 16:9
   - Vertical canvas 1080x1920, same scene names, overlays from /overlays/v/
   - Vertical output: YouTube Shorts (second stream key)
   - X is optional (Premium)

Full guide after deploy:
https://jenglandblog.netlify.app/obs

Overlay wall:
https://jenglandblog.netlify.app/overlays

Horizontal overlays (browser source 1920x1080):
  STARTING  https://jenglandblog.netlify.app/overlays/starting
  LIVE      https://jenglandblog.netlify.app/overlays/live
  DESK      https://jenglandblog.netlify.app/overlays/desk
  CHATTING  https://jenglandblog.netlify.app/overlays/chatting
  IRL       https://jenglandblog.netlify.app/overlays/irl
  REPLAY    https://jenglandblog.netlify.app/overlays/replay
  BRB       https://jenglandblog.netlify.app/overlays/brb
  ENDING    https://jenglandblog.netlify.app/overlays/ending
  STINGER   https://jenglandblog.netlify.app/overlays/stinger

Vertical overlays (browser source 1080x1920) — duplicate the scene in Aitum Vertical, same name:
  STARTING  https://jenglandblog.netlify.app/overlays/v/starting
  LIVE      https://jenglandblog.netlify.app/overlays/v/live
  DESK      https://jenglandblog.netlify.app/overlays/v/desk
  CHATTING  https://jenglandblog.netlify.app/overlays/v/chatting
  IRL       https://jenglandblog.netlify.app/overlays/v/irl
  REPLAY    https://jenglandblog.netlify.app/overlays/v/replay
  BRB       https://jenglandblog.netlify.app/overlays/v/brb
  ENDING    https://jenglandblog.netlify.app/overlays/v/ending

Query params:
  ?game=BeamNG
  ?minutes=8
  ?guides=1     (show Lumia wells)
