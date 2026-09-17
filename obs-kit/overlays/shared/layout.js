/**
 * One layout for overlays AND the OBS installer.
 * Wide = 1920×1080. Vertical = 1080×1920. Same overlay URL auto-flips.
 *
 * Cameras:
 *   Cam / Face   — face cam
 *   Cam / Room   — back cam
 *   Cam / Wheel  — wheel
 *   Cam / Pedals — pedals
 *
 * GAMING  = PC game + face + back
 * SIM     = sim + all four cams (horizontal row)
 * SIM RIG = sim + wheel and pedals only (switch to this from SIM)
 * Vertical copies are starting points — change those in the Vertical dock.
 */
window.STREAM_LAYOUT = {
  collectionWide: "J England Live",
  collectionVertical: "J England Vertical",
  fps: 60,
  overlayCss: "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }",
  /* OBS color_source ABGR for #07140e forest */
  backdropColor: 4279170055,
  canvas: {
    wide: { w: 1920, h: 1080 },
    vertical: { w: 1080, h: 1920 },
  },
  overlays: {
    "Overlay / Starting Soon": { file: "starting.html", shutdown: true, restart: true },
    "Overlay / Chat HUD": { file: "chatting.html" },
    "Overlay / Gaming HUD": { file: "desk.html" },
    "Overlay / Live HUD": { file: "live.html" },
    "Overlay / Rig HUD": { file: "rig.html" },
    "Overlay / Dual HUD": { file: "dual.html" },
    "Overlay / Replay HUD": { file: "replay.html" },
    "Overlay / IRL HUD": { file: "irl.html" },
    "Overlay / BRB": { file: "brb.html", shutdown: true, restart: true },
    "Overlay / Ending": { file: "ending.html", shutdown: true, restart: true },
    "Overlay / Stinger": { file: "stinger.html", shutdown: true, restart: true },
    "Overlay / Webcam Frame": { file: "webcam.html" },
  },
  scenes: [
    {
      id: "starting",
      name: "STARTING SOON",
      overlay: "Overlay / Starting Soon",
      items: {
        wide: [{ source: "Overlay / Starting Soon", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 }],
        vertical: [{ source: "Overlay / Starting Soon", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 }],
      },
    },
    {
      id: "chatting",
      name: "JUST CHATTING",
      overlay: "Overlay / Chat HUD",
      items: {
        wide: [
          { source: "Color / Backdrop", kind: "color", x: 0, y: 0, w: 1920, h: 1080 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 48, y: 140, w: 1104, h: 621 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 1176, y: 140, w: 696, h: 392 },
          { slot: "chat", source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / Chat HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { source: "Color / Backdrop", kind: "color", x: 0, y: 0, w: 1080, h: 1920 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 16, y: 88, w: 1048, h: 590 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 16, y: 694, w: 1048, h: 320 },
          { slot: "chat", source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / Chat HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "gaming",
      name: "GAMING",
      overlay: "Overlay / Gaming HUD",
      items: {
        wide: [
          { source: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 1408, y: 774, w: 480, h: 270 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 1072, y: 864, w: 320, h: 180 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / Gaming HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { slot: "game", source: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 16, y: 624, w: 520, h: 292 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 544, y: 624, w: 520, h: 292 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / Gaming HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "live",
      name: "SIM",
      overlay: "Overlay / Live HUD",
      items: {
        wide: [
          { source: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 40, y: 837, w: 354, h: 199 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 410, y: 837, w: 354, h: 199 },
          { slot: "wheel", source: "Cam / Wheel", kind: "camera", x: 780, y: 837, w: 354, h: 199 },
          { slot: "pedals", source: "Cam / Pedals", kind: "camera", x: 1150, y: 837, w: 354, h: 199 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Media / Hype Clip", kind: "media", x: 0, y: 0, w: 1920, h: 1080, enabled: false },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / Live HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { slot: "game", source: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 16, y: 624, w: 520, h: 220 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 544, y: 624, w: 520, h: 220 },
          { slot: "wheel", source: "Cam / Wheel", kind: "camera", x: 16, y: 860, w: 520, h: 220 },
          { slot: "pedals", source: "Cam / Pedals", kind: "camera", x: 544, y: 860, w: 520, h: 220 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / Live HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "rig",
      name: "SIM RIG",
      overlay: "Overlay / Rig HUD",
      items: {
        wide: [
          { source: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
          { slot: "wheel", source: "Cam / Wheel", kind: "camera", x: 40, y: 721, w: 560, h: 315 },
          { slot: "pedals", source: "Cam / Pedals", kind: "camera", x: 616, y: 721, w: 560, h: 315 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / Rig HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { slot: "game", source: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
          { slot: "wheel", source: "Cam / Wheel", kind: "camera", x: 16, y: 624, w: 1048, h: 280 },
          { slot: "pedals", source: "Cam / Pedals", kind: "camera", x: 16, y: 920, w: 1048, h: 280 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / Rig HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "dual",
      name: "DUAL",
      overlay: "Overlay / Dual HUD",
      items: {
        wide: [
          { source: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
          { slot: "angle", source: "Game / Angle 2", kind: "game2", x: 1248, y: 48, w: 640, h: 360 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 48, y: 900, w: 240, h: 135 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 304, y: 900, w: 240, h: 135 },
          { slot: "wheel", source: "Cam / Wheel", kind: "camera", x: 560, y: 900, w: 240, h: 135 },
          { slot: "pedals", source: "Cam / Pedals", kind: "camera", x: 816, y: 900, w: 240, h: 135 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / Dual HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { slot: "game", source: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
          { slot: "angle", source: "Game / Angle 2", kind: "game2", x: 16, y: 624, w: 1048, h: 200 },
          { slot: "face", source: "Cam / Face", kind: "camera", x: 16, y: 840, w: 520, h: 180 },
          { slot: "room", source: "Cam / Room", kind: "camera", x: 544, y: 840, w: 520, h: 180 },
          { slot: "wheel", source: "Cam / Wheel", kind: "camera", x: 16, y: 1036, w: 520, h: 180 },
          { slot: "pedals", source: "Cam / Pedals", kind: "camera", x: 544, y: 1036, w: 520, h: 180 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / Dual HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "replay",
      name: "REPLAY",
      overlay: "Overlay / Replay HUD",
      items: {
        wide: [
          { source: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / Replay HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { slot: "game", source: "Game / Main", kind: "game", x: 0, y: 360, w: 1080, h: 608 },
          { source: "Audio / Game", kind: "gameaudio" },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / Replay HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "irl",
      name: "IRL",
      overlay: "Overlay / IRL HUD",
      items: {
        wide: [
          { source: "Cam / Face", kind: "camera", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
          { source: "Overlay / IRL HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
        ],
        vertical: [
          { source: "Cam / Face", kind: "camera", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
          { source: "Overlay / IRL HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
        ],
      },
    },
    {
      id: "brb",
      name: "BRB",
      overlay: "Overlay / BRB",
      items: {
        wide: [{ source: "Overlay / BRB", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 }],
        vertical: [{ source: "Overlay / BRB", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 }],
      },
    },
    {
      id: "ending",
      name: "ENDING",
      overlay: "Overlay / Ending",
      items: {
        wide: [{ source: "Overlay / Ending", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 }],
        vertical: [{ source: "Overlay / Ending", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 }],
      },
    },
  ],
  lumiaWells: {
    wide: {
      chatting: { chat: { x: 1176, y: 556, w: 696, h: 428 }, alerts: { x: 200, y: 24, w: 860, h: 160 } },
      gaming: { chat: { x: 48, y: 774, w: 400, h: 270 }, alerts: { x: 200, y: 24, w: 860, h: 200 } },
      live: { chat: { x: 1520, y: 400, w: 360, h: 420 }, alerts: { x: 530, y: 24, w: 860, h: 200 } },
      rig: { chat: { x: 1192, y: 400, w: 688, h: 300 }, alerts: { x: 200, y: 24, w: 860, h: 200 } },
      dual: { chat: { x: 1248, y: 428, w: 640, h: 450 }, alerts: { x: 48, y: 24, w: 860, h: 200 } },
      irl: { alerts: { x: 530, y: 24, w: 860, h: 200 } },
    },
    vertical: {
      chatting: { chat: { x: 16, y: 1030, w: 1048, h: 830 }, alerts: { x: 16, y: 16, w: 1048, h: 160 } },
      gaming: { chat: { x: 16, y: 940, w: 1048, h: 912 }, alerts: { x: 16, y: 16, w: 1048, h: 160 } },
      live: { chat: { x: 16, y: 1096, w: 1048, h: 800 }, alerts: { x: 16, y: 16, w: 1048, h: 160 } },
      rig: { chat: { x: 16, y: 1220, w: 1048, h: 680 }, alerts: { x: 16, y: 16, w: 1048, h: 160 } },
      dual: { chat: { x: 16, y: 1232, w: 1048, h: 660 }, alerts: { x: 16, y: 16, w: 1048, h: 160 } },
      irl: { alerts: { x: 16, y: 40, w: 1048, h: 160 } },
    },
  },
  hotkeys: {
    "STARTING SOON": "Numpad 1",
    "JUST CHATTING": "Numpad 2",
    GAMING: "Numpad 3",
    SIM: "Numpad 4",
    "SIM RIG": "Numpad 5",
    REPLAY: "Numpad 6",
    IRL: "Numpad 7",
    BRB: "Numpad 8",
    ENDING: "Numpad 9",
  },
};
