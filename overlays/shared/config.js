/**
 * Rise Above — CHANGE THIS FILE
 *
 * Open in Notepad. Save. Then in OBS: right-click the overlay → Refresh.
 * You do not need to run the installer again for names, colors, links, or photos.
 *
 * Photos: drop starting.jpg, brb.jpg, ending.jpg in shared/backdrops/
 */
window.STREAM = {
  name: "Josh",
  brand: "RISE ABOVE",
  handle: "@jengland91",

  /* WHAT GAME ARE YOU PLAYING?
     Starting Soon prints:  BeamNG. Off-road. Live.
     Swap the game name when you change titles. Examples:
       game: "BeamNG"
       game: "SnowRunner"
       game: "Forza"
     Leave tagline blank unless you want to type the whole line yourself. */
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
    youtube: "jengland91",
    kick: "jengland91",
    tiktok: "jengland91",
    instagram: "jengland91",
    facebook: "jengland91",
    x: "",
    discord: "",
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
