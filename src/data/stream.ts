export const streamKit = {
  collectionWide: 'J England Live',
  collectionVertical: 'J England Vertical',
  overlayOrigin: 'https://jenglandblog.netlify.app',
  scenes: [
    { name: 'STARTING SOON', overlay: '/overlays/starting.html', job: 'Countdown while chat joins. Generic “Sim racing · Gaming · IRL” until you type a title in the control panel.' },
    { name: 'JUST CHATTING', overlay: '/overlays/chatting.html', job: 'Face cam + back cam. No game.' },
    { name: 'GAMING', overlay: '/overlays/desk.html', job: 'PC game with face cam and back cam. No wheel or pedals.' },
    { name: 'SIM', overlay: '/overlays/live.html', job: 'Sim gameplay with all four cams in a row on the horizontal canvas. Vertical is a 2×2 you can move later.' },
    { name: 'SIM RIG', overlay: '/overlays/rig.html', job: 'Same sim game, but only wheel + pedals, larger. Switch here from SIM.' },
    { name: 'DUAL', overlay: '/overlays/dual.html', job: 'Main view + second angle. Skip until you have Angle 2.' },
    { name: 'REPLAY', overlay: '/overlays/replay.html', job: 'Clean game, no cams. Pair with Source Record / Replay Source.' },
    { name: 'IRL', overlay: '/overlays/irl.html', job: 'Full-bleed cam, thin lower third. Phone / Insta360 / action cam.' },
    { name: 'BRB', overlay: '/overlays/brb.html', job: 'Hold screen. Leave Lumia alerts on.' },
    { name: 'ENDING', overlay: '/overlays/ending.html', job: 'Thanks + socials. Raid from Twitch if you want.' },
  ],
  destinations: [
    {
      canvas: '1920×1080',
      via: 'OBS Stream + Aitum Main Outputs',
      platforms: [
        { name: 'Twitch', note: 'Set OBS Settings → Stream to Twitch. 1080p60, CBR 6000, keyframe 2s.' },
        { name: 'YouTube', note: 'Aitum Main Output. Create a horizontal stream in YouTube Studio and paste that key.' },
        { name: 'Kick', note: 'Aitum Main Output. Key from Kick dashboard → Stream.' },
        { name: 'X', note: 'Allowed with X Premium. Aitum has an X output. Create a source in X Producer and match the server endpoint.' },
      ],
    },
    {
      canvas: '1080×1920',
      via: 'Aitum Vertical Outputs',
      platforms: [
        { name: 'YouTube Shorts / vertical live', note: 'Second YouTube stream key. Same overlay URL, browser source sized 1080×1920.' },
        { name: 'Kick / TikTok portrait', note: 'Only if that platform gives you a vertical key. Do not send the wide canvas to a portrait destination.' },
      ],
    },
  ],
  plugins: {
    already: [
      {
        name: 'OBS Studio',
        why: 'You already have this. Stay on OBS 31+ so Aitum Vertical and WebSocket behave.',
        url: 'https://obsproject.com/download',
      },
      {
        name: 'OBS WebSocket',
        why: 'Built into OBS 28+. Enable it: Tools → WebSocket Server Settings. Lumia and the scene installer both use this.',
        url: 'https://github.com/obsproject/obs-websocket',
      },
    ],
    required: [
      {
        name: 'Aitum Stream Suite (or Multistream + Vertical)',
        why: 'This is the “Aitum multi” plugin. Stream Suite is the current combined install. Multistream sends Kick / YouTube / X. Vertical is the 9:16 canvas for Shorts. Do not also run Restream.',
        url: 'https://aitum.tv/products/stream-suite',
      },
      {
        name: 'Lumia Stream',
        why: 'Chat, alerts, lights, and !sim / !brb scene changes over OBS WebSocket. Not an OBS plugin — the desktop app.',
        url: 'https://lumiastream.com/',
      },
    ],
    recommended: [
      {
        name: 'Move',
        why: 'Animates sources between scenes so cams slide instead of popping. The right replacement for a lot of old “stream effects” motion.',
        url: 'https://obsproject.com/forum/resources/move-transition.913/',
      },
      {
        name: 'Source Record',
        why: 'Records one source (game, face, wheel) to disk while you stream. Best storage plugin for YouTube VODs and Shorts recuts.',
        url: 'https://obsproject.com/forum/resources/source-record.1285/',
      },
      {
        name: 'Source Clone',
        why: 'Second copy of a cam or game without opening the USB device twice.',
        url: 'https://obsproject.com/forum/resources/source-clone.1632/',
      },
      {
        name: 'Downstream Keyer',
        why: 'Keeps Lumia alerts / webcam frame on every scene without pasting the same source nine times.',
        url: 'https://obsproject.com/forum/resources/downstream-keyer.1254/',
      },
      {
        name: 'Replay Source',
        why: 'Instant replay buffer you can dump onto the REPLAY scene.',
        url: 'https://obsproject.com/forum/resources/replay-source.686/',
      },
      {
        name: 'Directory Watch Media',
        why: 'Watches a folder and loads the newest file. Pair with Source Record for auto-replays.',
        url: 'https://obsproject.com/forum/resources/directory-watch-media.801/',
      },
      {
        name: 'Advanced Scene Switcher',
        why: 'Hotkeys, timers, and “if starting soon has been up 5 minutes → SIM”.',
        url: 'https://obsproject.com/forum/resources/advanced-scene-switcher.395/',
      },
    ],
    look: [
      {
        name: 'Composite Blur',
        why: 'Background blur on cams. StreamFX is discontinued — use this instead of StreamFX blur.',
        url: 'https://obsproject.com/forum/resources/composite-blur.1780/',
      },
      {
        name: 'Stroke Glow Shadow',
        why: 'Clean cam borders and glows without a giant PNG frame.',
        url: 'https://obsproject.com/forum/resources/stroke-glow-shadow.1790/',
      },
      {
        name: 'Advanced Masks',
        why: 'Rounded cams, feathered IRL frames, source-shaped masks.',
        url: 'https://obsproject.com/forum/resources/advanced-masks.1856/',
      },
      {
        name: 'obs-shaderfilter',
        why: 'The actual “stream effects” bucket: glows, CRT, chromatic, custom HLSL.',
        url: 'https://obsproject.com/forum/resources/obs-shaderfilter.1736/',
      },
      {
        name: 'Background Removal',
        why: 'Optional virtual backdrop on face cam if the garage is messy.',
        url: 'https://obsproject.com/forum/resources/background-removal.1404/',
      },
      {
        name: 'Waveform',
        why: 'Audio visualizer for Just Chatting / BRB music so the screen is not dead.',
        url: 'https://obsproject.com/forum/resources/waveform.1423/',
      },
    ],
    extra: [
      {
        name: 'DistroAV (NDI)',
        why: 'Bring in a phone, Insta360, or second PC over the LAN.',
        url: 'https://github.com/DistroAV/DistroAV',
      },
      {
        name: 'Input Overlay',
        why: 'Wheel / keyboard / mouse overlay for sim racing if you want inputs on screen.',
        url: 'https://obsproject.com/forum/resources/input-overlay.552/',
      },
      {
        name: 'Source Dock',
        why: 'Extra preview docks for Angle 2 or a cam without fullscreening it.',
        url: 'https://obsproject.com/forum/resources/source-dock.1317/',
      },
      {
        name: 'Media Playlist Source',
        why: 'BRB / starting music and hype clips in a folder.',
        url: 'https://obsproject.com/forum/resources/media-playlist-source.1397/',
      },
    ],
    skip: [
      {
        name: 'StreamFX',
        why: 'Abandoned. Do not install on OBS 31+. Composite Blur + Stroke Glow Shadow + shaderfilter cover it.',
      },
      {
        name: 'Restream / Streamlabs Encoder',
        why: 'Aitum already multi-streams. A second encoder fights OBS for the GPU and looks worse.',
      },
      {
        name: 'Meld Studio',
        why: 'You asked to leave it. Overlays in this kit are OBS browser sources, not Meld scenes.',
      },
    ],
  },
  encode: {
    canvas: '1920×1080 at 60fps. Color NV12, Rec. 709, Limited.',
    twitch: 'NVENC H.264, CBR 6000 kbps, keyframe 2s, preset P5 / Quality, look-ahead off, psycho AQ on.',
    youtube: 'Aitum can reuse the encoder or run a second NVENC at 8–12k for 1080p60.',
    vertical: '1080×1920, 30 or 60fps, H.264 CBR 4500–8000. Separate YouTube key.',
    audio: '48 kHz. Mic: RNNoise → EQ → Compressor 3:1 → Limiter −1.5 dB. Desktop Audio muted. Game via Application Audio Capture.',
  },
  lumia: [
    '!sim / !live / !race / !cams → SIM (all four cameras)',
    '!rig / !wheel → SIM RIG (wheel + pedals)',
    '!chat / !grid → JUST CHATTING',
    '!gaming / !desk / !pc → GAMING',
    '!dual → DUAL',
    '!replay → REPLAY',
    '!irl → IRL',
    '!brb → BRB',
    '!end → ENDING',
    '!start → STARTING SOON',
  ],
  checklist: [
    'Install Aitum Stream Suite (Multistream + Vertical). Confirm the Vertical Scenes dock exists.',
    'Enable OBS WebSocket. Copy the password.',
    'On the streaming PC, OPEN-OBS.bat (daily). One time: DOUBLE-CLICK-ME.bat → Switch overlays to this folder so URLs stop using :8765.',
    'If scenes are missing: open overlays/install.html from the kit folder (Chrome) → Connect → Load scenes into OBS (J England Live).',
    'Assign Cam / Face (face), Cam / Room (back cam), Cam / Wheel, Cam / Pedals. Set Game / Main. Mute Desktop Audio.',
    'OBS Settings → Stream = Twitch. Aitum Main outputs = YouTube 16:9 + Kick. Aitum Vertical output = YouTube Shorts key.',
    'In the Vertical Scenes dock, make STARTING SOON / JUST CHATTING / PLAYING / BRB / ENDING and Linked Scenes them to the widescreen names (see tonight.html).',
    'Stream Deck: Elgato OBS Studio plugin, same WebSocket password, one Scene button per name. Or click the control panel.',
    'Optional: paste the Lumia overlay URL into Lumia / Overlay. Import lumia-commands.json.',
    'Test: STARTING SOON → GAMING or SIM → BRB → ENDING. Confirm Twitch + YouTube + Kick + Shorts all have picture.',
    'Close Meld Studio so it is not grabbing the same cameras.',
  ],
};
