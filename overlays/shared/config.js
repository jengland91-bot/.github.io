/**
 * Rise Above — stream identity
 *
 * CHANGE NAMES HERE. Then in OBS: right-click the overlay source → Refresh.
 * You do not need to run the installer again just to rename LIVE / GRID / etc.
 */
window.STREAM = {
  name: "Josh",
  brand: "RISE ABOVE",
  tagline: "BeamNG. Off-road. Live.",
  handle: "@jengland91",

  /* These show on Starting Soon, BRB, and Ending (wide and vertical).
     Put a username OR a full https:// link. Leave blank to hide that platform.
     Save this file, then in OBS: right-click the overlay source -> Refresh.

     Examples:
       twitch:  "jengland91"  or  "https://twitch.tv/jengland91"
       youtube: "jengland91"  or  "https://youtube.com/@jengland91"
       kick:    "jengland91"  or  "https://kick.com/jengland91"
       tiktok:  "jengland91"
       instagram: "jengland91"
       facebook / x / discord: leave "" until you want them on screen
  */
  socials: {
    twitch: "jengland91",
    youtube: "jengland91",
    kick: "jengland91",
    tiktok: "jengland91",
    instagram: "jengland91",
    facebook: "",
    x: "",
    discord: "",
  },

  /* Off-road dirt / dusk palette */
  colors: {
    ember: "#C65A12",
    amber: "#E0A04A",
    ice: "#9AAB70",
    sand: "#D4C4A0",
    paper: "#EDE4D4",
  },

  startingMinutes: 5,

  brbMessage: "Grabbing a wrench. Back on the trail in a minute.",
  endingMessage: "Thanks for riding along.",

  /* These words show on the overlay pills and title cards. */
  chattingTitle: "GRID",
  liveTitle: "LIVE",
  dualTitle: "DUAL",
  replayTitle: "REPLAY",
  stagingPill: "STAGING",
  holdPill: "HOLDING",
  checkeredPill: "CHECKERED",

  startingKicker: "TRAILHEAD",
  startingLine1: "STARTING",
  startingLine2: "SOON",

  brbKicker: "TRAIL BREAK",
  brbLine1: "BE RIGHT",
  brbLine2: "BACK",

  endingKicker: "END OF TRAIL",
  endingLine1: "THANKS FOR",
  endingLine2: "WATCHING",
};
