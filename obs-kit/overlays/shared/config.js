/**
 * J England live kit — edit this file, save, then in OBS right-click the overlay → Refresh.
 * Hosted copy: https://jenglandblog.netlify.app/overlays/shared/config.js
 *
 * Easier: use the control panel. Leave `game` blank until you want a specific title.
 * URL overrides still work: starting.html?m=5&game=iRacing
 */
window.STREAM = {
  name: "Josh England",
  brand: "J ENGLAND",
  handle: "@jengland91",
  site: "jenglandblog.netlify.app",

  game: "",
  style: "",
  liveWord: "Live",
  tagline: "Sim racing · Gaming · IRL",

  startingKicker: "GOING LIVE",
  startingLine1: "STARTING",
  startingLine2: "SOON",

  brbKicker: "HOLDING",
  brbLine1: "BE RIGHT",
  brbLine2: "BACK",
  brbMessage: "Grabbing a drink. Don't go anywhere.",

  endingKicker: "THAT'S A WRAP",
  endingLine1: "THANKS FOR",
  endingLine2: "WATCHING",
  endingMessage: "VODs, gear, and codes → jenglandblog.netlify.app/links",

  chattingTitle: "CHAT",
  deskTitle: "DESK",
  liveTitle: "LIVE",
  dualTitle: "DUAL",
  replayTitle: "REPLAY",
  irlTitle: "IRL",
  stagingPill: "STAGING",
  holdPill: "BRB",
  checkeredPill: "END",

  colors: {
    cyan: "#3eea86",
    violet: "#14b8a6",
    paper: "#f3f1ec",
    muted: "#9aa3b2",
    ink: "#070c09",
  },

  socials: {
    twitch: "jengland91",
    youtube: "Joshengland91",
    kick: "jengland91",
    tiktok: "jengland91",
    instagram: "jengland91",
    x: "",
    facebook: "",
    discord: "",
  },

  /* Optional photos. Leave these and the kit uses the branded CSS screens. */
  backdrops: {
    starting: "../branding/starting-soon-1920x1080.svg",
    brb: "../branding/brb-1920x1080.svg",
    ending: "../branding/ending-soon-1920x1080.svg",
    startingVertical: "",
    brbVertical: "",
    endingVertical: "",
  },

  startingMinutes: 5,
};
