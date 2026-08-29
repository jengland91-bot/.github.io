(function () {
  const STREAM = window.STREAM || {};
  const params = new URLSearchParams(location.search);

  function applyColors() {
    const colors = STREAM.colors || {};
    const accent = params.get("accent") || colors.ember;
    if (accent) document.documentElement.style.setProperty("--ember", accent);
    if (colors.amber) document.documentElement.style.setProperty("--amber", colors.amber);
    if (colors.ice) document.documentElement.style.setProperty("--ice", colors.ice);
    if (colors.sand) document.documentElement.style.setProperty("--sand", colors.sand);
    if (colors.paper) document.documentElement.style.setProperty("--paper", colors.paper);
  }

  function fill(selector, value) {
    if (!value) return;
    document.querySelectorAll(selector).forEach((el) => {
      el.textContent = value;
    });
  }

  function applyIdentity() {
    const name = params.get("name") || STREAM.name;
    fill("[data-name]", name);
    fill("[data-brand]", STREAM.brand);
    fill("[data-tagline]", STREAM.tagline);
    fill("[data-handle]", STREAM.handle);
    fill("[data-brb]", STREAM.brbMessage);
    fill("[data-ending]", STREAM.endingMessage);
    fill("[data-chatting-title]", STREAM.chattingTitle);
    fill("[data-live-title]", STREAM.liveTitle);
    fill("[data-dual-title]", STREAM.dualTitle);
    fill("[data-replay-title]", STREAM.replayTitle);
    fill("[data-staging-pill]", STREAM.stagingPill);
    fill("[data-hold-pill]", STREAM.holdPill);
    fill("[data-checkered-pill]", STREAM.checkeredPill);
    fill("[data-starting-kicker]", STREAM.startingKicker);
    fill("[data-starting-line1]", STREAM.startingLine1);
    fill("[data-starting-line2]", STREAM.startingLine2);
    fill("[data-brb-kicker]", STREAM.brbKicker);
    fill("[data-brb-line1]", STREAM.brbLine1);
    fill("[data-brb-line2]", STREAM.brbLine2);
    fill("[data-ending-kicker]", STREAM.endingKicker);
    fill("[data-ending-line1]", STREAM.endingLine1);
    fill("[data-ending-line2]", STREAM.endingLine2);
  }

  function socialHandle(value) {
    if (!value) return "";
    let s = String(value).trim();
    s = s.replace(/^https?:\/\//i, "");
    s = s.replace(/^www\./i, "");
    s = s.replace(/^(youtube\.com\/@|youtube\.com\/c\/|youtube\.com\/channel\/|youtube\.com\/|twitch\.tv\/|tiktok\.com\/@|tiktok\.com\/|kick\.com\/|instagram\.com\/|facebook\.com\/|x\.com\/|twitter\.com\/|discord\.gg\/|discord\.com\/invite\/)/i, "");
    s = s.replace(/\/.*$/, "");
    s = s.replace(/^@/, "");
    return s;
  }

  function socials() {
    const row = document.querySelector("[data-socials]");
    if (!row) return;
    const map = {
      twitch: "TWITCH",
      youtube: "YT",
      kick: "KICK",
      tiktok: "TIKTOK",
      instagram: "IG",
      facebook: "FB",
      x: "X",
      twitter: "X",
      discord: "DISCORD",
    };
    const items = STREAM.socials || {};
    row.innerHTML = "";
    Object.entries(map).forEach(([key, label]) => {
      const handle = socialHandle(items[key]);
      if (!handle) return;
      const span = document.createElement("span");
      span.textContent = `${label}  ${handle}`;
      row.appendChild(span);
    });
    if (!row.childElementCount && STREAM.handle) {
      const span = document.createElement("span");
      span.textContent = STREAM.handle;
      row.appendChild(span);
    }
  }

  function mode() {
    if (params.has("preview")) document.body.classList.add("preview");
    if (params.has("setup")) document.body.classList.add("setup");
    if (document.body.classList.contains("vertical")) {
      document.documentElement.classList.add("vertical");
    }
  }

  function clock() {
    const nodes = document.querySelectorAll("[data-clock]");
    if (!nodes.length) return;
    const tick = () => {
      const now = new Date();
      const text = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      nodes.forEach((n) => {
        n.textContent = text;
      });
    };
    tick();
    setInterval(tick, 1000);
  }

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function countdown() {
    const node = document.querySelector("[data-countdown]");
    if (!node) return;
    const minutes = Number(params.get("m") || STREAM.startingMinutes || 5);
    let remaining = Math.max(0, Math.round(minutes * 60));

    const render = () => {
      if (remaining <= 0) {
        node.textContent = "GOING LIVE";
        node.classList.add("done");
        return;
      }
      const m = Math.floor(remaining / 60);
      const s = remaining % 60;
      node.textContent = `${pad(m)}:${pad(s)}`;
      remaining -= 1;
    };
    render();
    setInterval(render, 1000);
  }

  function dust() {
    const canvas = document.getElementById("dust");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const particles = [];
    const count = 36;
    const vertical = document.body.classList.contains("vertical");
    const W = vertical ? 1080 : 1920;
    const H = vertical ? 1920 : 1080;

    function resize() {
      canvas.width = W;
      canvas.height = H;
    }

    function spawn() {
      particles.length = 0;
      for (let i = 0; i < count; i += 1) {
        particles.push({
          x: Math.random() * W,
          y: Math.random() * H,
          r: Math.random() * 1.8 + 0.4,
          s: Math.random() * 0.45 + 0.12,
          a: Math.random() * 0.35 + 0.08,
        });
      }
    }

    function frame() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.y -= p.s;
        p.x += Math.sin(p.y / 40) * 0.15;
        if (p.y < -4) {
          p.y = H + 4;
          p.x = Math.random() * W;
        }
        ctx.beginPath();
        ctx.fillStyle = `rgba(210, 150, 70, ${p.a})`;
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      });
      requestAnimationFrame(frame);
    }

    resize();
    spawn();
    frame();
  }

  applyColors();
  applyIdentity();
  socials();
  mode();
  clock();
  countdown();
  dust();
})();
