/** Copy-paste channel bios, panels, and scene notes for Josh / jengland91 */
export const streamingKit = {
  verdict: {
    software: 'Meld Studio',
    why: 'You already multistream Twitch + Kick + YouTube through Meld, and your overlay workflow is built for it. Switching to OBS or Streamlabs only makes sense if Meld blocks a specific feature you need — not for “looking more professional.” Professional comes from scenes, audio, lighting, and brand consistency.',
    whenObs:
      'Move to OBS only if you need a specific plugin ecosystem Meld cannot cover (niche filters, advanced scripting, certain chat bots that only ship OBS browser sources). Expect a full rebuild of scenes.',
    whenStreamlabs:
      'Avoid Streamlabs as the main encoder if you care about performance and control. It is heavier than OBS/Meld and adds little once you already multistream from Meld.',
  },
  brand: {
    colors: ['#0b0d12', '#00f2fe', '#a855f7', '#f4f7fb'],
    voice: 'Real-world creator who races sims, shoots photos, and goes IRL — not a neon esports clone.',
    sameEverywhere: 'Same avatar + same cyan accent on Twitch and Kick. YouTube can feel broader (photo + off-road + long-form).',
  },
  bios: {
    twitch: `Sim racing · games · IRL
Photographer / content creator / trophy truck co-driver.
Gear I actually use + partner codes → jenglandblog.netlify.app/links
Business: jengland9191@yahoo.com`,
    kick: `Live sim racing, games, and IRL.
Josh England — photographer, creator, Moza sim rig, real dirt when I can.
Links, Amazon gear, codes → jenglandblog.netlify.app/links
@jengland91 everywhere`,
    youtube: `Josh England — photographer, sim racer, off-road / trophy truck co-driver, and streamer.

Here you'll find longer videos: gear walkthroughs, sim racing sessions, camera kits, desert runs, and behind-the-scenes from the work — not just live VODs.

Live streams also land here. For go-live alerts catch me on Twitch + Kick (@jengland91).

Portfolio: riseabovephoto.com
Gear + codes: jenglandblog.netlify.app
Amazon: amazon.com/shop/jengland91
Business: jengland9191@yahoo.com`,
    youtubeHandleShort: `Photo · sim racing · off-road · streams. Real gear, real dirt, real laps.`,
  },
  panels: [
    {
      title: 'Schedule',
      image: '/branding/panel-schedule.svg',
      link: 'https://jenglandblog.netlify.app/links',
      body: 'Nights: sim racing, games, or IRL. Follow for go-live pings — schedule shifts with real life and race weeks.',
    },
    {
      title: 'Socials',
      image: '/branding/panel-socials.svg',
      link: 'https://jenglandblog.netlify.app/links',
      body: '@jengland91 on YouTube, TikTok, Instagram. Full hub: jenglandblog.netlify.app/links',
    },
    {
      title: 'Gear I use',
      image: '/branding/panel-gear.svg',
      link: 'https://www.amazon.com/shop/jengland91',
      body: 'Moza rig, cams, mic — the kit from stream and the truck. Amazon storefront (affiliate).',
    },
    {
      title: 'Codes + support',
      image: '/branding/panel-discord.svg',
      link: 'https://jenglandblog.netlify.app/partners',
      body: 'Moza / Insta360 codes and Buy Me a Coffee: jenglandblog.netlify.app/partners',
    },
  ],
  scenes: [
    {
      name: 'STARTING',
      job: 'First 2–5 minutes while chat joins',
      layers: [
        'starting-soon-1920x1080.svg (or offline PNG) full screen',
        'Optional: low music + mic muted or soft talk',
        'Browser alert source if you use one',
      ],
    },
    {
      name: 'SIM',
      job: 'Main sim racing layout',
      layers: [
        'Game capture (full frame)',
        'Face cam bottom-right ~320×240 or 400×300 with thin cyan border',
        'Optional room / wheel cam tiny strip bottom-left',
        'Chat-readable alert area top-right clear of UI',
        'Keep HUD clean — no giant frames',
      ],
    },
    {
      name: 'DESK',
      job: 'Talking, gear, desktop games',
      layers: [
        'Display capture or game',
        'Face cam larger (corner or side)',
        'Optional second cam on desk / wheel',
      ],
    },
    {
      name: 'IRL',
      job: 'Phone / action cam / Insta360',
      layers: [
        'Main camera full bleed',
        'Minimal lower-third name only if needed',
        'No busy overlays outdoors — readability first',
      ],
    },
    {
      name: 'BRB',
      job: 'Breaks without ending stream',
      layers: ['brb-1920x1080.svg', 'Mic off or muted filter', 'Keep chat alerts on'],
    },
    {
      name: 'ENDING',
      job: 'Last 2–3 minutes',
      layers: [
        'ending-soon-1920x1080.svg',
        'Say where VODs / YouTube / links live',
        'Raid or shout out when it fits',
      ],
    },
  ],
  assets: [
    { label: 'Avatar 800×800', href: '/branding/avatar-800x800.png' },
    { label: 'Twitch banner 1200×480', href: '/branding/twitch-banner-1200x480.png' },
    { label: 'Kick banner 1280×700', href: '/branding/kick-banner-1280x700.png' },
    { label: 'YouTube banner 2560×1440', href: '/branding/youtube-banner-2560x1440.png' },
    { label: 'Offline / stream screen 1920×1080', href: '/branding/offline-screen-1920x1080.png' },
    { label: 'Starting Soon SVG', href: '/branding/starting-soon-1920x1080.svg' },
    { label: 'BRB SVG', href: '/branding/brb-1920x1080.svg' },
    { label: 'Ending SVG', href: '/branding/ending-soon-1920x1080.svg' },
  ],
  checklist: [
    'Same avatar on Twitch + Kick (+ YouTube profile photo).',
    'Paste bios from this page — keep under character limits.',
    'Twitch: Brand tab → profile banner + offline screen.',
    'Kick: Profile picture + channel banner.',
    'YouTube: Channel banner (safe-center text) + About + Featured channels / links.',
    'Meld: build the 6 scenes above; multistream as you already do.',
    'Audio first: mic louder than game; noise gate / EQ if available.',
    'One CTA per stream: follow, Discord/links, or gear — not all at once.',
  ],
};
