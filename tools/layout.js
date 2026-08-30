/**
 * Rise Above BeamNG — layout used by the installer.
 * Positions match overlays/shared/theme.css wells.
 */
window.RISE_LAYOUT = {
  collectionName: "Rise Above BeamNG",
  canvas: { width: 1920, height: 1080, fps: 60 },
  transition: { name: "Fade", durationMs: 300 },
  css: "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }",

  scenes: [
    "STARTING SOON",
    "GRID",
    "DESK",
    "RACE",
    "RACE DUAL",
    "REPLAY",
    "BRB",
    "ENDING",
  ],

  overlays: {
    "Overlay / Starting Soon": { file: "starting-soon.html", query: "?m=5", shutdown: true, restart: true },
    "Overlay / Grid HUD": { file: "chatting.html", shutdown: false, restart: false },
    "Overlay / Desk HUD": { file: "desk.html", shutdown: false, restart: false },
    "Overlay / Race HUD": { file: "live.html", shutdown: false, restart: false },
    "Overlay / Dual HUD": { file: "race-dual.html", shutdown: false, restart: false },
    "Overlay / Replay HUD": { file: "replay.html", shutdown: false, restart: false },
    "Overlay / BRB": { file: "brb.html", shutdown: true, restart: true },
    "Overlay / Ending": { file: "ending.html", shutdown: true, restart: true },
  },

  items: {
    "STARTING SOON": [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Overlay / Starting Soon", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
    ],
    GRID: [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Cam / Face", kind: "camera", x: 48, y: 168, w: 960, h: 540 },
      { name: "Cam / Room", kind: "camera", x: 1032, y: 168, w: 840, h: 360 },
      { name: "Cam / Wheel", kind: "camera", x: 1032, y: 544, w: 408, h: 200 },
      { name: "Cam / Pedals", kind: "camera", x: 1464, y: 544, w: 408, h: 200 },
      { name: "Overlay / Grid HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Social Stream / Chat", kind: "ssn", x: 1032, y: 760, w: 840, h: 268 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
    ],
    DESK: [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Cam / Face", kind: "camera", x: 1256, y: 696, w: 640, h: 360 },
      { name: "Cam / Room", kind: "camera", x: 760, y: 786, w: 480, h: 270 },
      { name: "Overlay / Desk HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Social Stream / Chat", kind: "ssn", x: 344, y: 786, w: 400, h: 270 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
    ],
    RACE: [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Cam / Face", kind: "camera", x: 48, y: 876, w: 320, h: 180 },
      { name: "Cam / Room", kind: "camera", x: 384, y: 876, w: 320, h: 180 },
      { name: "Cam / Wheel", kind: "camera", x: 720, y: 876, w: 320, h: 180 },
      { name: "Cam / Pedals", kind: "camera", x: 1056, y: 876, w: 320, h: 180 },
      { name: "Overlay / Race HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Social Stream / Chat", kind: "ssn", x: 1488, y: 520, w: 384, h: 500 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Media / Hype Clip", kind: "media", x: 0, y: 0, w: 1920, h: 1080, enabled: false },
    ],
    "RACE DUAL": [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Game / Angle 2", kind: "game", x: 1248, y: 48, w: 640, h: 360 },
      { name: "Cam / Face", kind: "camera", x: 48, y: 900, w: 240, h: 135 },
      { name: "Cam / Room", kind: "camera", x: 304, y: 900, w: 240, h: 135 },
      { name: "Cam / Wheel", kind: "camera", x: 560, y: 900, w: 240, h: 135 },
      { name: "Cam / Pedals", kind: "camera", x: 816, y: 900, w: 240, h: 135 },
      { name: "Overlay / Dual HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Social Stream / Chat", kind: "ssn", x: 1248, y: 428, w: 640, h: 580 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
    ],
    REPLAY: [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Overlay / Replay HUD", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1920, h: 1080 },
    ],
    BRB: [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Overlay / BRB", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
    ],
    ENDING: [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Overlay / Ending", kind: "browser", x: 0, y: 0, w: 1920, h: 1080 },
    ],
  },
};

window.RISE_LAYOUT_VERTICAL = {
  collectionName: "Rise Above BeamNG Vertical",
  canvas: { width: 1080, height: 1920, fps: 60 },
  transition: { name: "Fade", durationMs: 300 },
  css: "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }",

  scenes: [
    "STARTING SOON",
    "GRID",
    "DESK",
    "RACE",
    "RACE DUAL",
    "REPLAY",
    "BRB",
    "ENDING",
  ],

  overlays: {
    "Overlay / Starting Soon": { file: "vertical/starting-soon.html", query: "?m=5", shutdown: true, restart: true },
    "Overlay / Grid HUD": { file: "vertical/chatting.html", shutdown: false, restart: false },
    "Overlay / Desk HUD": { file: "vertical/desk.html", shutdown: false, restart: false },
    "Overlay / Race HUD": { file: "vertical/live.html", shutdown: false, restart: false },
    "Overlay / Dual HUD": { file: "vertical/race-dual.html", shutdown: false, restart: false },
    "Overlay / Replay HUD": { file: "vertical/replay.html", shutdown: false, restart: false },
    "Overlay / BRB": { file: "vertical/brb.html", shutdown: true, restart: true },
    "Overlay / Ending": { file: "vertical/ending.html", shutdown: true, restart: true },
  },

  items: {
    "STARTING SOON": [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Overlay / Starting Soon", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
    ],
    GRID: [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Cam / Face", kind: "camera", x: 16, y: 88, w: 1048, h: 420 },
      { name: "Cam / Room", kind: "camera", x: 16, y: 524, w: 1048, h: 280 },
      { name: "Cam / Wheel", kind: "camera", x: 16, y: 820, w: 516, h: 200 },
      { name: "Cam / Pedals", kind: "camera", x: 548, y: 820, w: 516, h: 200 },
      { name: "Overlay / Grid HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Social Stream / Chat", kind: "ssn", x: 16, y: 1036, w: 1048, h: 816 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
    ],
    DESK: [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Cam / Face", kind: "camera", x: 16, y: 624, w: 520, h: 300 },
      { name: "Cam / Room", kind: "camera", x: 544, y: 624, w: 520, h: 300 },
      { name: "Overlay / Desk HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Social Stream / Chat", kind: "ssn", x: 16, y: 940, w: 1048, h: 912 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
    ],
    RACE: [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Cam / Face", kind: "camera", x: 16, y: 624, w: 520, h: 220 },
      { name: "Cam / Room", kind: "camera", x: 544, y: 624, w: 520, h: 220 },
      { name: "Cam / Wheel", kind: "camera", x: 16, y: 860, w: 520, h: 220 },
      { name: "Cam / Pedals", kind: "camera", x: 544, y: 860, w: 520, h: 220 },
      { name: "Overlay / Race HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Social Stream / Chat", kind: "ssn", x: 16, y: 1096, w: 1048, h: 800 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Media / Hype Clip", kind: "media", x: 0, y: 0, w: 1080, h: 1920, enabled: false },
    ],
    "RACE DUAL": [
      { name: "Game / Main", kind: "game", x: 0, y: 0, w: 1080, h: 608 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Game / Angle 2", kind: "game", x: 16, y: 624, w: 1048, h: 200 },
      { name: "Cam / Face", kind: "camera", x: 16, y: 840, w: 520, h: 180 },
      { name: "Cam / Room", kind: "camera", x: 544, y: 840, w: 520, h: 180 },
      { name: "Cam / Wheel", kind: "camera", x: 16, y: 1036, w: 520, h: 180 },
      { name: "Cam / Pedals", kind: "camera", x: 544, y: 1036, w: 520, h: 180 },
      { name: "Overlay / Dual HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Social Stream / Chat", kind: "ssn", x: 16, y: 1232, w: 1048, h: 660 },
      { name: "Social Stream / Featured", kind: "ssn", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
    ],
    REPLAY: [
      { name: "Game / Main", kind: "game", x: 0, y: 360, w: 1080, h: 608 },
      { name: "Audio / Game", kind: "gameaudio" },
      { name: "Overlay / Replay HUD", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
      { name: "Lumia / Overlay", kind: "lumia", x: 0, y: 0, w: 1080, h: 1920 },
    ],
    BRB: [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Overlay / BRB", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
    ],
    ENDING: [
      { name: "Color / Backdrop", kind: "color" },
      { name: "Overlay / Ending", kind: "browser", x: 0, y: 0, w: 1080, h: 1920 },
    ],
  },
};

window.RISE_LAYOUTS = [window.RISE_LAYOUT, window.RISE_LAYOUT_VERTICAL];

window.RISE_AITUM_SOURCE_MAP = {
  "Overlay / Starting Soon": "Overlay / Starting Soon V",
  "Overlay / Grid HUD": "Overlay / Grid HUD V",
  "Overlay / Desk HUD": "Overlay / Desk HUD V",
  "Overlay / Race HUD": "Overlay / Race HUD V",
  "Overlay / Dual HUD": "Overlay / Dual HUD V",
  "Overlay / Replay HUD": "Overlay / Replay HUD V",
  "Overlay / BRB": "Overlay / BRB V",
  "Overlay / Ending": "Overlay / Ending V",
  "Lumia / Overlay": "Lumia / Overlay V",
  "Color / Backdrop": "Color / Backdrop V",
};

window.LUMIA_COMMANDS = [
  { name: "race", message: "Scene \u2192 RACE", cooldownDuration: 3000, description: "Meld: Show Scene RACE" },
  { name: "dual", message: "Scene \u2192 RACE DUAL", cooldownDuration: 3000, description: "Meld: Set current scene RACE DUAL" },
  { name: "replay", message: "Scene \u2192 REPLAY", cooldownDuration: 3000, description: "Meld: Set current scene REPLAY" },
  { name: "grid", message: "Scene \u2192 GRID", cooldownDuration: 3000, description: "Meld: Set current scene GRID" },
  { name: "desk", message: "Scene \u2192 DESK", cooldownDuration: 3000, description: "Meld: Set current scene DESK (sit at desk, other games)" },
  { name: "brb", message: "Scene \u2192 BRB", cooldownDuration: 8000, description: "Meld: Set current scene BRB" },
  { name: "live", message: "Scene \u2192 RACE", cooldownDuration: 3000, description: "Meld: Set current scene RACE" },
  { name: "face", message: "Face cam on", cooldownDuration: 15000, description: "Meld: Cam / Face on; Room, Wheel, Pedals off (RACE / GRID / RACE DUAL / DESK)" },
  { name: "room", message: "Room cam on", cooldownDuration: 15000, description: "Meld: Cam / Room on; Face, Wheel, Pedals off (RACE / GRID / RACE DUAL / DESK)" },
  { name: "rig", message: "All cams on", cooldownDuration: 15000, description: "Meld: Cam / Face, Room, Wheel, Pedals on" },
  { name: "wheel", message: "Wheel cam on", cooldownDuration: 15000, description: "Meld: Cam / Wheel on; Face, Room, Pedals off (RACE / GRID / RACE DUAL)" },
  { name: "pedals", message: "Pedals cam on", cooldownDuration: 15000, description: "Meld: Cam / Pedals on; Face, Room, Wheel off (RACE / GRID / RACE DUAL)" },
  { name: "game", message: "Game only", cooldownDuration: 15000, description: "Meld: hide Cam / Face, Room, Wheel, Pedals" },
];
