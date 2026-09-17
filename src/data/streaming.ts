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
    colors: ['#0b0d12', '#00f2fe', '#10b981', '#f4f7fb'],
    voice: 'Real-world creator who races sims, shoots photos, and goes IRL — not a neon esports clone.',
    sameEverywhere:
      'Same clean banner + avatar on Twitch and Kick. Keep YouTube parked until you decide the long-form mix.',
  },
  bios: {
    twitch: `Sim racing | games | IRL
Josh England — photographer & creator.
Links + gear → jenglandblog.netlify.app/links`,
    kick: `Sim racing | games | IRL
Josh England — photographer & creator.
Links + gear → jenglandblog.netlify.app/links`,
    youtube: `Josh England — photographer, sim racer, off-road / trophy truck co-driver, and streamer.

(Coming soon: longer videos — gear, sim sessions, desert runs, behind the scenes.)

Live alerts: Twitch + Kick @jengland91
Links: jenglandblog.netlify.app/links`,
    youtubeHandleShort: `Photo · sim racing · off-road · streams.`,
  },
  starter: {
    focus: 'Twitch + Kick first. Same banner energy, same short bio. Build panels and clip highlights later.',
    bio: `Sim racing | games | IRL
Josh England — photographer & creator.
Links + gear → jenglandblog.netlify.app/links`,
    doToday: [
      'Upload the clean banner on Twitch (1200×480) and Kick (1280×700).',
      'Upload the JE avatar on both.',
      'Paste the starter bio on both (they match on purpose).',
      'Add one panel that links to jenglandblog.netlify.app/links.',
      'Go live with Meld as you already do — polish overlays later.',
    ],
    later: [
      'Add clip panels / highlight reels once you have VODs.',
      'Expand schedule + socials panels.',
      'Build YouTube when long-form direction is clear.',
    ],
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
      body: 'Sim rig, cams, mic — the kit from stream and the truck. Amazon storefront (affiliate).',
    },
    {
      title: 'Codes + support',
      image: '/branding/panel-discord.svg',
      link: 'https://jenglandblog.netlify.app/partners',
      body: 'Partner codes and Buy Me a Coffee: jenglandblog.netlify.app/partners',
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
    { label: 'Full brand pack ZIP (recommended)', href: '/branding/jengland-streaming-brand-pack.zip' },
    { label: 'Avatar 800×800 (use this)', href: '/branding/avatar-800x800.png' },
    { label: 'Twitch clean banner 1200×480 (use this)', href: '/branding/twitch-banner-clean-1200x480.png' },
    { label: 'Kick clean banner 1280×700 (use this)', href: '/branding/kick-banner-clean-1280x700.png' },
    { label: 'Offline clean screen 1920×1080', href: '/branding/offline-screen-clean-1920x1080.png' },
    { label: 'Starting Soon SVG', href: '/branding/starting-soon-1920x1080.svg' },
    { label: 'BRB SVG', href: '/branding/brb-1920x1080.svg' },
    { label: 'Ending SVG', href: '/branding/ending-soon-1920x1080.svg' },
    { label: 'Links panel graphic', href: '/branding/panel-socials.svg' },
  ],
  checklist: [
    'Upload clean banner + JE avatar on Twitch and Kick today.',
    'Paste the same short starter bio on both.',
    'Add one panel linking to jenglandblog.netlify.app/links.',
    'Keep streaming in Meld — scenes can stay simple (STARTING / SIM / BRB / ENDING).',
    'Park YouTube branding until long-form direction is clear.',
    'When you have clips, add highlight panels and swap banner photography later.',
  ],
};
