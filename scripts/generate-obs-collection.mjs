/**
 * Generates an OBS Studio scene collection for J England.
 * Run: node scripts/generate-obs-collection.mjs
 */
import { randomUUID } from 'node:crypto';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const origin = 'https://jenglandblog.netlify.app';
const out = join(dirname(fileURLToPath(import.meta.url)), '..', 'public', 'obs-pack', 'J-England.json');

const uuids = new Map();
const uuid = (name) => {
  if (!uuids.has(name)) uuids.set(name, randomUUID());
  return uuids.get(name);
};

const color = (hex) => {
  const n = hex.replace('#', '');
  const r = parseInt(n.slice(0, 2), 16);
  const g = parseInt(n.slice(2, 4), 16);
  const b = parseInt(n.slice(4, 6), 16);
  return (255 << 24) | (b << 16) | (g << 8) | r;
};

function browser(name, url, width, height, { shutdown = false, restart = false } = {}) {
  return {
    prev_ver: 520093696,
    name,
    uuid: uuid(name),
    id: 'browser_source',
    versioned_id: 'browser_source',
    settings: {
      css: '',
      fps: 30,
      fps_custom: false,
      height,
      reroute_audio: false,
      restart_when_active: restart,
      shutdown,
      url,
      webpage_control_level: 0,
      width,
    },
    mixers: 0,
    sync: 0,
    flags: 0,
    volume: 1.0,
    balance: 0.5,
    enabled: true,
    muted: false,
    hotkeys: {},
    deinterlace_mode: 0,
    deinterlace_field_order: 0,
    monitoring_type: 0,
    private_settings: {},
    filters: [],
  };
}

function colorSource(name, width, height, hex) {
  return {
    prev_ver: 520093696,
    name,
    uuid: uuid(name),
    id: 'color_source_v3',
    versioned_id: 'color_source_v3',
    settings: { color: color(hex), width, height },
    mixers: 0,
    sync: 0,
    flags: 0,
    volume: 1.0,
    balance: 0.5,
    enabled: true,
    muted: false,
    hotkeys: {},
    deinterlace_mode: 0,
    deinterlace_field_order: 0,
    monitoring_type: 0,
    private_settings: {},
    filters: [],
  };
}

function item(name, id, extra = {}) {
  return {
    name,
    source_uuid: uuid(name),
    visible: extra.visible ?? true,
    locked: extra.locked ?? false,
    rot: 0.0,
    pos: { x: extra.x ?? 0.0, y: extra.y ?? 0.0 },
    scale: { x: extra.sx ?? 1.0, y: extra.sy ?? 1.0 },
    align: extra.align ?? 5,
    bounds_type: extra.bounds_type ?? 0,
    bounds_align: extra.bounds_align ?? 0,
    bounds_crop: false,
    bounds: extra.bounds ?? { x: 0.0, y: 0.0 },
    crop_left: 0,
    crop_top: 0,
    crop_right: 0,
    crop_bottom: 0,
    id,
    group_item_backup: false,
    scale_filter: 'disable',
    blend_method: 'default',
    blend_type: 'normal',
    show_transition: { duration: 0 },
    hide_transition: { duration: 0 },
    private_settings: {},
  };
}

function scene(name, items, size) {
  const settings = {
    custom_size: Boolean(size),
    id_counter: items.length + 1,
    items,
  };
  if (size) {
    settings.cx = size.w;
    settings.cy = size.h;
  }
  return {
    prev_ver: 520093696,
    name,
    uuid: uuid(name),
    id: 'scene',
    versioned_id: 'scene',
    settings,
    mixers: 0,
    sync: 0,
    flags: 0,
    volume: 1.0,
    balance: 0.5,
    enabled: true,
    muted: false,
    hotkeys: {},
    deinterlace_mode: 0,
    deinterlace_field_order: 0,
    monitoring_type: 0,
    private_settings: {},
    filters: [],
  };
}

const overlays = {
  starting: `${origin}/overlays/starting`,
  live: `${origin}/overlays/live`,
  desk: `${origin}/overlays/desk`,
  chatting: `${origin}/overlays/chatting`,
  irl: `${origin}/overlays/irl`,
  replay: `${origin}/overlays/replay`,
  brb: `${origin}/overlays/brb`,
  ending: `${origin}/overlays/ending`,
  stinger: `${origin}/overlays/stinger`,
};

const sources = [
  colorSource('Placeholder · Game', 1920, 1080, '#151c28'),
  colorSource('Placeholder · Face', 400, 225, '#1c2430'),
  colorSource('Placeholder · Desktop', 1920, 1080, '#12161f'),
  colorSource('Placeholder · IRL', 1920, 1080, '#16120e'),
  colorSource('Placeholder · Replay', 1920, 1080, '#1a1420'),

  browser('Overlay · STARTING', overlays.starting, 1920, 1080, { shutdown: true, restart: true }),
  browser('Overlay · LIVE', overlays.live, 1920, 1080),
  browser('Overlay · DESK', overlays.desk, 1920, 1080),
  browser('Overlay · CHATTING', overlays.chatting, 1920, 1080),
  browser('Overlay · IRL', overlays.irl, 1920, 1080),
  browser('Overlay · REPLAY', overlays.replay, 1920, 1080),
  browser('Overlay · BRB', overlays.brb, 1920, 1080, { shutdown: true, restart: true }),
  browser('Overlay · ENDING', overlays.ending, 1920, 1080, { shutdown: true, restart: true }),
  browser('Overlay · Stinger', overlays.stinger, 1920, 1080, { shutdown: true, restart: true }),

  browser('Lumia · Alerts', `${origin}/overlays/well?label=Lumia%20alerts`, 860, 200),
  browser('Lumia · Chat', `${origin}/overlays/well?label=Lumia%20chat`, 380, 520),
  browser('Lumia · Labels', `${origin}/overlays/well?label=Lumia%20labels`, 420, 72),
  browser('Lumia · Now Playing', `${origin}/overlays/well?label=Now%20playing`, 400, 64),
];

const nested = [
  scene('• Game', [item('Placeholder · Game', 1)], { w: 1920, h: 1080 }),
  scene('• Face Cam', [item('Placeholder · Face', 1)], { w: 400, h: 225 }),
  scene('• Desktop', [item('Placeholder · Desktop', 1)], { w: 1920, h: 1080 }),
  scene('• IRL Cam', [item('Placeholder · IRL', 1)], { w: 1920, h: 1080 }),
];

const program = [
  scene('STARTING', [item('Overlay · STARTING', 1)]),
  scene('LIVE', [
    item('• Game', 1),
    item('• Face Cam', 2, { x: 1472, y: 807 }),
    item('Lumia · Alerts', 3, { x: 530, y: 36 }),
    item('Lumia · Labels', 4, { x: 48, y: 104 }),
    item('Lumia · Now Playing', 5, { x: 48, y: 900 }),
    item('Overlay · LIVE', 6),
  ]),
  scene('DESK', [
    item('• Desktop', 1),
    item('• Face Cam', 2, { x: 1472, y: 807 }),
    item('Lumia · Chat', 3, { x: 48, y: 360 }),
    item('Lumia · Alerts', 4, { x: 530, y: 36 }),
    item('Overlay · DESK', 5),
  ]),
  scene('CHATTING', [
    item('• Face Cam', 1, {
      x: 80,
      y: 220,
      bounds_type: 2,
      bounds: { x: 880, y: 495 },
    }),
    item('Lumia · Chat', 2, { x: 1492, y: 220 }),
    item('Lumia · Alerts', 3, { x: 530, y: 36 }),
    item('Overlay · CHATTING', 4),
  ]),
  scene('IRL', [
    item('• IRL Cam', 1),
    item('Lumia · Alerts', 2, { x: 530, y: 36 }),
    item('Overlay · IRL', 3),
  ]),
  scene('REPLAY', [
    item('Placeholder · Replay', 1),
    item('• Face Cam', 2, { x: 1472, y: 807 }),
    item('Overlay · REPLAY', 3),
  ]),
  scene('BRB', [item('Overlay · BRB', 1)]),
  scene('ENDING', [item('Overlay · ENDING', 1)]),
  scene('STINGER', [item('Overlay · Stinger', 1)]),
];

const collection = {
  current_scene: 'LIVE',
  current_program_scene: 'LIVE',
  current_preview_scene: 'STARTING',
  scene_order: [
    ...program.map((s) => ({ name: s.name })),
    ...nested.map((s) => ({ name: s.name })),
  ],
  name: 'J England',
  groups: [],
  quick_transitions: [
    { duration: 300, fade_to_black: false, hotkeys: [], id: 1, name: 'Cut' },
    { duration: 300, fade_to_black: true, hotkeys: [], id: 2, name: 'Fade to Black' },
  ],
  transitions: [
    { id: 'fade_transition', name: 'Fade', settings: {} },
    { id: 'cut_transition', name: 'Cut', settings: {} },
  ],
  saved_projectors: [],
  current_transition: 'Fade',
  transition_duration: 280,
  preview_locked: false,
  scaling_enabled: false,
  scaling_level: 0,
  scaling_off_x: 0.0,
  scaling_off_y: 0.0,
  sources: [...sources, ...nested, ...program],
  modules: {
    'scripts-tool': [],
    'output-timer': { streamTimerEnabled: false, recordTimerEnabled: false },
  },
};

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, `${JSON.stringify(collection, null, 4)}\n`);
console.log(`Wrote ${out}`);
