/** OBS overlay pack + multi-stream setup for Josh / jengland91 */
export const overlayOrigin = 'https://jenglandblog.netlify.app';

export const show = {
  name: 'Josh England',
  short: 'J England',
  handle: '@jengland91',
  line: 'Sim racing · Games · IRL',
  game: 'BeamNG',
  gameNote: 'Change this in src/data/obs.ts, or append ?game=YourTitle to any overlay URL.',
  startingMinutes: 5,
};

export const overlayScenes = [
  {
    id: 'starting',
    name: 'STARTING',
    job: 'First 2–5 minutes while chat joins. Mic optional, music low.',
    kind: 'hold' as const,
    kicker: 'Staging',
    title: 'Starting soon',
    message: 'Grab a drink — going live in a minute.',
  },
  {
    id: 'live',
    name: 'LIVE',
    job: 'Main sim / game layout. Full game, face cam, Lumia alerts.',
    kind: 'hud' as const,
    kicker: 'Live',
    title: 'Live',
    message: '',
  },
  {
    id: 'desk',
    name: 'DESK',
    job: 'Desktop games, gear talk, reviews. Bigger cam, desktop behind.',
    kind: 'hud' as const,
    kicker: 'Desk',
    title: 'Desk',
    message: '',
  },
  {
    id: 'chatting',
    name: 'CHATTING',
    job: 'Just chatting. Large cam, Lumia chat on the side.',
    kind: 'hud' as const,
    kicker: 'Grid',
    title: 'Chatting',
    message: '',
  },
  {
    id: 'irl',
    name: 'IRL',
    job: 'Phone, Insta360, action cam. Minimal chrome so the footage reads.',
    kind: 'hud' as const,
    kicker: 'IRL',
    title: 'IRL',
    message: '',
  },
  {
    id: 'replay',
    name: 'REPLAY',
    job: 'Source Record / replay clip. Watermark + cam.',
    kind: 'hud' as const,
    kicker: 'Replay',
    title: 'Replay',
    message: '',
  },
  {
    id: 'brb',
    name: 'BRB',
    job: 'Breaks without ending the stream. Mute the mic in OBS.',
    kind: 'hold' as const,
    kicker: 'Hold',
    title: 'Be right back',
    message: 'Stepping off the rig. Stay here.',
  },
  {
    id: 'ending',
    name: 'ENDING',
    job: 'Last 2–3 minutes. Point at YouTube, /links, and the raid.',
    kind: 'hold' as const,
    kicker: 'Checkered',
    title: 'Thanks for watching',
    message: 'VODs and gear live at jenglandblog.netlify.app/links',
  },
];

export const extraOverlays = [
  { id: 'stinger', name: 'Stinger', job: 'JE wipe. Use as a scene, or record it to WebM for a stinger transition.' },
  { id: 'lower-third', name: 'Lower third', job: 'Name + handle bar. Drop on IRL or interviews.' },
  { id: 'webcam-frame', name: 'Webcam frame', job: 'Cyan cam border only. Put your camera under it.' },
  { id: 'well', name: 'Lumia well', job: 'Labeled empty box. Temporary stand-in until you paste a Lumia URL.' },
];

export const lumiaWells = {
  alerts: { width: 860, height: 200, x: 530, y: 36, label: 'Lumia alerts' },
  labels: { width: 420, height: 72, x: 48, y: 104, label: 'Lumia event list' },
  chat: { width: 380, height: 520, x: 48, y: 360, label: 'Lumia chatbox' },
  nowPlaying: { width: 400, height: 64, x: 48, y: 900, label: 'Lumia now playing' },
  face: { width: 400, height: 225, x: 1472, y: 807, label: 'Face cam' },
};

export const platforms = [
  {
    id: 'twitch',
    name: 'Twitch',
    url: 'https://www.twitch.tv/jengland91',
    canvas: 'Main 16:9',
    where: 'OBS Settings → Stream (built-in). Leave this as Twitch so chat, markers, and Enhanced Broadcasting stay native.',
    bitrate: '6,000 kbps CBR',
    keyframe: '2s',
    note: 'Cap at 6k unless you are Twitch Partnered with transcoding headroom. 1080p60 NVENC.',
  },
  {
    id: 'kick',
    name: 'Kick',
    url: 'https://kick.com/jengland91',
    canvas: 'Main 16:9',
    where: 'Aitum Multistream / Stream Suite → Main Outputs → Kick. Paste the key from Creator Dashboard → Stream URL and Key.',
    bitrate: '6,000–8,000 kbps CBR',
    keyframe: '2s',
    note: 'Copy the RTMPS URL from your own dashboard. Kick keys are per-account — do not reuse a tutorial URL.',
  },
  {
    id: 'youtube',
    name: 'YouTube (16:9)',
    url: 'https://www.youtube.com/@Joshengland91',
    canvas: 'Main 16:9',
    where: 'Aitum Main Outputs → YouTube. Create a live stream in YouTube Studio and paste that key.',
    bitrate: '8,000 kbps CBR (1080p60)',
    keyframe: '2s',
    note: 'YouTube can take more bitrate than Twitch. Keep this as a separate encode so Twitch stays at 6k.',
  },
  {
    id: 'youtube-shorts',
    name: 'YouTube Shorts / vertical',
    url: 'https://www.youtube.com/@Joshengland91',
    canvas: 'Vertical 9:16',
    where: 'Aitum Vertical Outputs → YouTube. This is a second YouTube live (separate key) using the vertical canvas.',
    bitrate: '4,500–6,000 kbps CBR',
    keyframe: '2s',
    note: 'YouTube cannot restream one key as both 16:9 and Shorts. Two lives, two keys, scene-linked canvases.',
  },
  {
    id: 'x',
    name: 'X',
    url: 'https://x.com/',
    canvas: 'Main 16:9',
    where: 'Aitum Main Outputs → X. Requires X Premium. Create a source in Media Studio / Producer and match the server endpoint.',
    bitrate: '9,000 kbps CBR · 1080p30 or 720p60',
    keyframe: '3s',
    note: 'Allowed, not free. Add this last — it is the hungriest extra encode. Skip it until upload and GPU have headroom.',
  },
];

export const plugins = [
  {
    name: 'OBS Studio 31+',
    required: true,
    why: 'The encoder. Do not use Streamlabs Desktop as the main app.',
    href: 'https://obsproject.com/',
    note: 'WebSocket v5 is already built in. Tools → WebSocket Server Settings → Enable. Lumia needs this.',
  },
  {
    name: 'Aitum Stream Suite (or Multistream + Vertical)',
    required: true,
    why: 'Multi-stream + second 9:16 canvas. This is the “Aitum multi” stack. Stream Suite is the newer all-in-one.',
    href: 'https://aitum.tv/products/stream-suite',
    note: 'Install Stream Suite OR the older Multistream + Vertical pair — not both. If Multistream already works, keep it and add Vertical from https://aitum.tv/products/vertical',
  },
  {
    name: 'OBS WebSocket',
    required: true,
    why: 'Lumia Stream, Stream Deck, and almost every bot talk to OBS over this.',
    href: 'https://obsproject.com/kb/obs-websocket-overview',
    note: 'Built into OBS 28+. Do not install the old v4 plugin.',
  },
  {
    name: 'Move (Exeldro)',
    required: false,
    why: 'Sources slide instead of popping. Makes scene changes look like a real show.',
    href: 'https://obsproject.com/forum/resources/move.913/',
    note: 'Set the scene transition to Move, then add Move filters on the cam / game sources.',
  },
  {
    name: 'Source Record',
    required: false,
    why: 'Records one source (clean game, clean cam) while you stream. Editing YouTube later depends on this.',
    href: 'https://obsproject.com/forum/resources/source-record.1285/',
    note: 'Add as a filter on • Game and • Face Cam. Use a different folder than the main recording.',
  },
  {
    name: 'Shaderfilter',
    required: false,
    why: 'Blur, glow, corner-pin, VHS. This is the StreamFX replacement that still tracks current OBS.',
    href: 'https://obsproject.com/forum/resources/obs-shaderfilter.1736/',
    note: 'StreamFX is patchy on OBS 31/32. Prefer Shaderfilter + 3D Effect.',
  },
  {
    name: '3D Effect',
    required: false,
    why: 'Tilt / perspective on cam or overlays without StreamFX.',
    href: 'https://obsproject.com/forum/resources/3d-effect.1692/',
  },
  {
    name: 'Source Clone',
    required: false,
    why: 'Reuse the same cam/game on the vertical canvas without capturing twice.',
    href: 'https://obsproject.com/forum/resources/source-clone.1632/',
    note: 'Aitum Vertical can also nest / clone the main canvas. Use one method, not both on the same source.',
  },
  {
    name: 'Downstream Keyer',
    required: false,
    why: 'Alerts, labels, and a webcam frame that stay on every scene so you are not duplicating them.',
    href: 'https://obsproject.com/forum/resources/downstream-keyer.1254/',
    note: 'Put Lumia Alerts + Labels in DSK 1. Hide DSK on STARTING/BRB/ENDING if you want those screens clean.',
  },
  {
    name: 'Advanced Scene Switcher',
    required: false,
    why: 'Auto STARTING → LIVE after the countdown, mute mic on BRB, switch to ENDING on a hotkey sequence.',
    href: 'https://obsproject.com/forum/resources/advanced-scene-switcher.395/',
  },
  {
    name: 'Replay Source',
    required: false,
    why: 'Instant in-stream replays (crashes, saves, clips) without leaving OBS.',
    href: 'https://obsproject.com/forum/resources/replay-source.686/',
  },
  {
    name: 'Directory Watch Media',
    required: false,
    why: 'Auto-play the newest file in a folder — Source Record dumps, phone dumps, highlight clips.',
    href: 'https://obsproject.com/forum/resources/directory-watch-media.801/',
  },
  {
    name: 'Media Controls',
    required: false,
    why: 'Play/pause/seek media sources from a dock. Needed once you have intro/outro/replay files.',
    href: 'https://obsproject.com/forum/resources/media-controls.1032/',
  },
  {
    name: 'Waveform',
    required: false,
    why: 'Audio meters that do not lie. Catch the clipped mic before chat does.',
    href: 'https://obsproject.com/forum/resources/waveform.1423/',
  },
  {
    name: 'Background Removal',
    required: false,
    why: 'Cam cutout without a green screen. Optional — a real key looks better if you have the cloth.',
    href: 'https://obsproject.com/forum/resources/background-removal.1404/',
  },
  {
    name: 'Input Overlay',
    required: false,
    why: 'Show wheel / keyboard / pad on sim or desk games.',
    href: 'https://obsproject.com/forum/resources/input-overlay.552/',
  },
  {
    name: 'DistroAV (NDI)',
    required: false,
    why: 'Bring in a second PC, a phone, or an IRL kit over the LAN.',
    href: 'https://github.com/DistroAV/DistroAV',
  },
  {
    name: 'StreamFX',
    required: false,
    why: 'Classic blur / 3D transform pack. Only if you already have a build that matches your OBS version.',
    href: 'https://github.com/Xaymar/obs-StreamFX',
    note: 'Skip on a fresh OBS 31/32 install. Use Shaderfilter instead.',
  },
];

export const audioTracks = [
  { track: 1, use: 'Stream mix — everything' },
  { track: 2, use: 'Twitch VOD track — mute copyright music here' },
  { track: 3, use: 'Mic only (Source Record / YouTube VO)' },
  { track: 4, use: 'Game / desktop only' },
  { track: 5, use: 'Discord / IRL spare' },
  { track: 6, use: 'Hold music (STARTING / BRB / ENDING)' },
];

export const bitrates = {
  launch: {
    label: 'Launch (start here)',
    upload: '~20 Mbps stable',
    outputs: [
      'Twitch built-in 1080p60 @ 6,000',
      'Kick Aitum 1080p60 @ 6,000',
      'YouTube Aitum 1080p60 @ 8,000',
    ],
  },
  dual: {
    label: 'YouTube Shorts add-on',
    upload: '~26 Mbps stable',
    outputs: [
      'Everything in Launch',
      'YouTube vertical 1080×1920 @ 4,500–6,000',
    ],
  },
  full: {
    label: 'Full (X last)',
    upload: '~35 Mbps stable + GPU that can run 4–5 NVENC sessions',
    outputs: [
      'Everything in dual',
      'X Premium 1080p30 @ 9,000',
    ],
  },
};

export const lumiaSteps = [
  'Open Lumia Stream → Connections → OBS. Use OBS 28+ (WebSocket v5).',
  'In OBS: Tools → WebSocket Server Settings → Enable. Set a password. Port 4455 is fine.',
  'Paste host 127.0.0.1, port 4455, and the password into Lumia. Connect. Scene names from this pack should appear.',
  'In Lumia Overlay UI (overlays.lumiastream.com) create four overlays: Alerts, Chatbox, Event list, Now playing.',
  'Copy each overlay URL. In OBS, edit the matching “Lumia · …” browser source and paste it. Width/height are already set.',
  'Connect Twitch, Kick, and YouTube inside Lumia so one chatbox and one alert box cover the multi-stream.',
  'Optional: Lumia actions → Switch OBS scene. Name them the same as this pack (STARTING, LIVE, BRB…) so Stream Deck / phone match.',
];

export const aitumSteps = [
  'Dock Aitum (Stream Suite or Multistream). Gear icon → Main Outputs.',
  'Leave OBS built-in stream on Twitch.',
  'Add Kick. Paste your dashboard stream key. Custom encoder: NVENC H.264, 6,000–8,000, keyframe 2s.',
  'Add YouTube. Paste the 16:9 live key. Custom encoder: NVENC H.264, 8,000, keyframe 2s.',
  'Install / enable Vertical canvas at 1080×1920, 60 fps. Create scenes with the same names as main (STARTING, LIVE, …).',
  'Turn on scene linking so a main scene switch also switches vertical.',
  'Gear → Vertical Outputs → add YouTube with the Shorts / second live key.',
  'X is optional: Premium account, Producer source, match the server, 1080p30 @ ~9,000, keyframe 3s.',
];

export function overlayUrl(id: string, vertical = false) {
  const path = vertical ? `/overlays/v/${id}` : `/overlays/${id}`;
  return `${overlayOrigin}${path}`;
}
