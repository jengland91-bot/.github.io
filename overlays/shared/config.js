/**
 * Rise Above — CHANGE THIS FILE
 *
 * Open in Notepad. Save. Then in Meld: reload the Browser overlay.
 * Names, colors, SSN session, Lumia URL, photos.
 *
 * Photos: drop starting.jpg, brb.jpg, ending.jpg in shared/backdrops/
 */
window.STREAM = {
  name: "Josh",
  /* Big word next to LIVE. Leave blank to hide it. Put something here if you want it back. */
  brand: "",
  handle: "@jengland91",

  /* TODAY'S GAME — this is the big title on STARTING SOON.
     Easiest: double-click tools\Change-Game.bat and pick / type the name.
     Or change the word in quotes here, Save, then in Meld reload the Browser overlay.
     Examples: "BeamNG"  "SnowRunner"  "Forza Horizon"  "GTA V"
     Leave tagline blank unless you want to type the whole subtitle yourself. */
  game: "BeamNG",
  style: "Off-road",
  liveWord: "Live",
  tagline: "",

  /* Small word above STARTING SOON. That is the "trail ahead" line.
     Examples: TRAILHEAD, GRID WALK, LOBBY, STAGING */
  startingKicker: "TRAILHEAD",
  startingLine1: "STARTING",
  startingLine2: "SOON",

  brbKicker: "TRAIL BREAK",
  brbLine1: "BE RIGHT",
  brbLine2: "BACK",
  brbMessage: "Grabbing a wrench. Back on the trail in a minute.",

  endingKicker: "END OF TRAIL",
  endingLine1: "THANKS FOR",
  endingLine2: "WATCHING",
  endingMessage: "Thanks for riding along.",

  chattingTitle: "GRID",
  /* Small word on the DESK scene pill. Sit-at-desk other games. */
  deskTitle: "DESK",
  liveTitle: "LIVE",
  dualTitle: "DUAL",
  replayTitle: "REPLAY",
  stagingPill: "STAGING",
  holdPill: "HOLDING",
  checkeredPill: "CHECKERED",

  /* Monster green #7CB701 is the main accent (pills, hazard tape, cam wells). */
  colors: {
    ember: "#7CB701",
    amber: "#8A7A38",
    ice: "#9BB86A",
    sand: "#C4B490",
    paper: "#E8DCC8",
  },

  /* Links. Username OR a full https:// URL. Blank = hide that one. */
  socials: {
    twitch: "jengland91",
    youtube: "joshengland91",
    kick: "jengland91",
    tiktok: "jengland91",
    instagram: "jengland91",
    facebook: "jengland91",
    x: "",
    discord: "",
  },

  /*
   * Social Stream Ninja — chat on stream for viewers.
   * Open the SSN extension / app, copy the session ID, paste it here.
   * Same ID in the dock, the chat overlay, and the featured overlay.
   */
  ssn: {
    session: "",
  },

  /*
   * Lumia Stream — alerts + lights. Paste the overlay URL from Lumia here.
   * Leave blank if you only want alerts on your gaming monitor (chat-for-you).
   */
  lumia: {
    overlayUrl: "",
  },

  /* Photos on Starting Soon / BRB / Ending. Paths from the overlays/ folder. */
  backdrops: {
    starting: "shared/backdrops/starting.jpg",
    brb: "shared/backdrops/brb.jpg",
    ending: "shared/backdrops/ending.jpg",
    startingVertical: "shared/backdrops/starting-vertical.jpg",
    brbVertical: "shared/backdrops/brb-vertical.jpg",
    endingVertical: "shared/backdrops/ending-vertical.jpg",
  },

  startingMinutes: 5,
};
