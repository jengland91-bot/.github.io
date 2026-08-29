/**
 * Rise Above — stream identity
 *
 * CHANGE NAMES / COLORS / PHOTO PATHS HERE. Then in OBS: right-click the
 * overlay source → Refresh. You do not need to run the installer again.
 *
 * Photos: drop starting.jpg, brb.jpg, ending.jpg in shared/backdrops/
 * (see that folder's START-HERE). Same files work for wide and vertical.
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
       facebook: "joshengland91"
       discord: "1483831196570878084"  or  "https://discord.com/users/1483831196570878084"
                (a discord.gg invite URL also works)
       x: leave "" until you want it on screen
  */
  socials: {
    twitch: "jengland91",
    youtube: "jengland91",
    kick: "jengland91",
    tiktok: "jengland91",
    instagram: "jengland91",
    facebook: "joshengland91",
    x: "",
    discord: "1483831196570878084",
  },

  /* Off-road dirt / dusk / pine palette (not neon gaming green) */
  colors: {
    ember: "#4A6B32",
    amber: "#8A7A38",
    ice: "#7A9A5C",
    sand: "#C4B490",
    paper: "#E8DCC8",
  },

  /* Photos on Starting Soon / BRB / Ending. Paths are from the overlays/ folder.
     Drop files in overlays/shared/backdrops/ then OBS → right-click overlay → Refresh.
     Vertical scenes use the same three files unless a *-vertical.jpg is present.
     Change a path here if you want a different filename. */
  backdrops: {
    starting: "shared/backdrops/starting.jpg",
    brb: "shared/backdrops/brb.jpg",
    ending: "shared/backdrops/ending.jpg",
    startingVertical: "shared/backdrops/starting-vertical.jpg",
    brbVertical: "shared/backdrops/brb-vertical.jpg",
    endingVertical: "shared/backdrops/ending-vertical.jpg",
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
