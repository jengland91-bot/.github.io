/**
 * Rise Above — TikTok LIVE Studio Dual layout.
 * Portrait is the source of truth. Landscape only resizes the same sources.
 */
window.RISE_TIKTOK_LAYOUT = {
  name: "Rise Above BeamNG",
  scenes: ["STARTING SOON", "GRID", "DESK", "RACE", "RACE DUAL", "REPLAY", "BRB", "ENDING"],
  overlays: {
    "STARTING SOON": "overlays/vertical/starting-soon.html?m=5",
    GRID: "overlays/vertical/chatting.html",
    DESK: "overlays/vertical/desk.html",
    RACE: "overlays/vertical/live.html",
    "RACE DUAL": "overlays/vertical/race-dual.html",
    REPLAY: "overlays/vertical/replay.html",
    BRB: "overlays/vertical/brb.html",
    ENDING: "overlays/vertical/ending.html",
  },
  phone: {
    canvas: { w: 1080, h: 1920 },
    "STARTING SOON": [
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
    ],
    GRID: [
      { name: "Cam / Face", x: 16, y: 88, w: 1048, h: 420, kind: "cam" },
      { name: "Cam / Room", x: 16, y: 524, w: 1048, h: 280, kind: "cam" },
      { name: "Cam / Wheel", x: 16, y: 820, w: 516, h: 200, kind: "cam" },
      { name: "Cam / Pedals", x: 548, y: 820, w: 516, h: 200, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1080, h: 1920, kind: "lumia" },
    ],
    DESK: [
      { name: "Game / Main", x: 0, y: 0, w: 1080, h: 608, kind: "game" },
      { name: "Cam / Face", x: 16, y: 624, w: 1048, h: 400, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1080, h: 1920, kind: "lumia" },
    ],
    RACE: [
      { name: "Game / Main", x: 0, y: 0, w: 1080, h: 608, kind: "game" },
      { name: "Cam / Face", x: 16, y: 624, w: 520, h: 220, kind: "cam" },
      { name: "Cam / Room", x: 544, y: 624, w: 520, h: 220, kind: "cam" },
      { name: "Cam / Wheel", x: 16, y: 860, w: 520, h: 220, kind: "cam" },
      { name: "Cam / Pedals", x: 544, y: 860, w: 520, h: 220, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1080, h: 1920, kind: "lumia" },
    ],
    "RACE DUAL": [
      { name: "Game / Main", x: 0, y: 0, w: 1080, h: 608, kind: "game" },
      { name: "Game / Angle 2", x: 16, y: 624, w: 1048, h: 200, kind: "game" },
      { name: "Cam / Face", x: 16, y: 840, w: 520, h: 180, kind: "cam" },
      { name: "Cam / Room", x: 544, y: 840, w: 520, h: 180, kind: "cam" },
      { name: "Cam / Wheel", x: 16, y: 1036, w: 520, h: 180, kind: "cam" },
      { name: "Cam / Pedals", x: 544, y: 1036, w: 520, h: 180, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1080, h: 1920, kind: "lumia" },
    ],
    REPLAY: [
      { name: "Game / Main", x: 0, y: 360, w: 1080, h: 608, kind: "game" },
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1080, h: 1920, kind: "lumia" },
    ],
    BRB: [
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
    ],
    ENDING: [
      { name: "Overlay Link", x: 0, y: 0, w: 1080, h: 1920, kind: "overlay" },
    ],
  },
  land: {
    canvas: { w: 1920, h: 1080 },
    "STARTING SOON": [
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
    ],
    GRID: [
      { name: "Cam / Face", x: 48, y: 168, w: 960, h: 540, kind: "cam" },
      { name: "Cam / Room", x: 1032, y: 168, w: 840, h: 360, kind: "cam" },
      { name: "Cam / Wheel", x: 1032, y: 544, w: 408, h: 200, kind: "cam" },
      { name: "Cam / Pedals", x: 1464, y: 544, w: 408, h: 200, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1920, h: 1080, kind: "lumia" },
    ],
    DESK: [
      { name: "Game / Main", x: 0, y: 0, w: 1920, h: 1080, kind: "game" },
      { name: "Cam / Face", x: 1256, y: 696, w: 640, h: 360, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1920, h: 1080, kind: "lumia" },
    ],
    RACE: [
      { name: "Game / Main", x: 0, y: 0, w: 1920, h: 1080, kind: "game" },
      { name: "Cam / Face", x: 48, y: 876, w: 320, h: 180, kind: "cam" },
      { name: "Cam / Room", x: 384, y: 876, w: 320, h: 180, kind: "cam" },
      { name: "Cam / Wheel", x: 720, y: 876, w: 320, h: 180, kind: "cam" },
      { name: "Cam / Pedals", x: 1056, y: 876, w: 320, h: 180, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1920, h: 1080, kind: "lumia" },
    ],
    "RACE DUAL": [
      { name: "Game / Main", x: 0, y: 0, w: 1920, h: 1080, kind: "game" },
      { name: "Game / Angle 2", x: 1248, y: 48, w: 640, h: 360, kind: "game" },
      { name: "Cam / Face", x: 48, y: 900, w: 240, h: 135, kind: "cam" },
      { name: "Cam / Room", x: 304, y: 900, w: 240, h: 135, kind: "cam" },
      { name: "Cam / Wheel", x: 560, y: 900, w: 240, h: 135, kind: "cam" },
      { name: "Cam / Pedals", x: 816, y: 900, w: 240, h: 135, kind: "cam" },
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1920, h: 1080, kind: "lumia" },
    ],
    REPLAY: [
      { name: "Game / Main", x: 0, y: 0, w: 1920, h: 1080, kind: "game" },
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
      { name: "Lumia Link", x: 0, y: 0, w: 1920, h: 1080, kind: "lumia" },
    ],
    BRB: [
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
    ],
    ENDING: [
      { name: "Overlay Link", x: 0, y: 0, w: 1920, h: 1080, kind: "overlay" },
    ],
  },
};
