(function () {
  const STREAM = window.STREAM || {};
  const LAYOUT = window.STREAM_LAYOUT || {};
  const params = new URLSearchParams(location.search);

  function applyColors() {
    const colors = STREAM.colors || {};
    const root = document.documentElement.style;
    if (colors.cyan) root.setProperty("--cyan", colors.cyan);
    if (colors.violet) root.setProperty("--violet", colors.violet);
    if (colors.paper) root.setProperty("--paper", colors.paper);
    if (colors.muted) root.setProperty("--muted", colors.muted);
    if (colors.ink) root.setProperty("--ink", colors.ink);
    const accent = params.get("accent");
    if (accent) root.setProperty("--cyan", accent);
  }

  function fill(selector, value) {
    const text = value == null ? "" : String(value);
    document.querySelectorAll(selector).forEach((el) => {
      el.textContent = text;
    });
  }

  function currentGame() {
    const fromUrl = params.get("game") || params.get("title");
    if (fromUrl && String(fromUrl).trim()) return String(fromUrl).trim();
    return String(STREAM.game || "").trim();
  }

  function taglineText() {
    const custom = String(STREAM.tagline || "").trim();
    if (custom) return custom;
    return String(STREAM.style || "").trim();
  }

  function applyIdentity() {
    fill("[data-name]", STREAM.name);
    fill("[data-brand]", STREAM.brand);
    fill("[data-handle]", STREAM.handle);
    fill("[data-site]", STREAM.site);
    fill("[data-game]", currentGame());
    document.querySelectorAll("[data-game]").forEach((el) => {
      el.hidden = !currentGame();
    });
    const tagline = taglineText();
    fill("[data-tagline]", tagline);
    document.querySelectorAll("[data-tagline]").forEach((el) => {
      el.hidden = !tagline;
    });
    fill("[data-brb]", STREAM.brbMessage);
    fill("[data-ending]", STREAM.endingMessage);
    fill("[data-chatting-title]", STREAM.chattingTitle);
    fill("[data-desk-title]", STREAM.deskTitle);
    fill("[data-live-title]", STREAM.liveTitle);
    fill("[data-dual-title]", STREAM.dualTitle);
    fill("[data-replay-title]", STREAM.replayTitle);
    fill("[data-irl-title]", STREAM.irlTitle);
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
    s = s.replace(
      /^(youtube\.com\/@|youtube\.com\/c\/|youtube\.com\/channel\/|youtube\.com\/|twitch\.tv\/|tiktok\.com\/@|tiktok\.com\/|kick\.com\/|kik\.com\/|instagram\.com\/|facebook\.com\/|x\.com\/|twitter\.com\/|discord\.gg\/|discord\.com\/invite\/)/i,
      ""
    );
    s = s.replace(/\/.*$/, "");
    s = s.replace(/^@/, "");
    return s;
  }

  function socials() {
    const row = document.querySelector("[data-socials]");
    if (!row) return;
    const map = {
      twitch: "Twitch",
      youtube: "YouTube",
      kick: "Kick",
      tiktok: "TikTok",
      instagram: "IG",
      x: "X",
      twitter: "X",
      facebook: "FB",
      discord: "Discord",
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

  function isVerticalCanvas() {
    if (params.get("h") === "1" || params.get("wide") === "1") return false;
    if (params.get("v") === "1" || params.get("vertical") === "1") return true;
    if (window.innerWidth > 0 && window.innerHeight > 0) {
      return window.innerHeight > window.innerWidth;
    }
    return document.body.classList.contains("vertical");
  }

  function applyCanvas() {
    const vertical = isVerticalCanvas();
    document.documentElement.classList.toggle("vertical", vertical);
    document.body.classList.toggle("vertical", vertical);
    applyWells();
  }

  function placeWell(el, box, canvas) {
    if (!el || box.w == null) return;
    el.classList.add("placed");
    el.style.left = (box.x / canvas.w) * 100 + "%";
    el.style.top = (box.y / canvas.h) * 100 + "%";
    el.style.width = (box.w / canvas.w) * 100 + "%";
    el.style.height = (box.h / canvas.h) * 100 + "%";
  }

  function applyWells() {
    document.querySelectorAll(".well").forEach((el) => el.classList.remove("placed"));
    const sceneId = document.body.dataset.scene;
    const scene = (LAYOUT.scenes || []).find((s) => s.id === sceneId);
    if (!scene) return;
    const mode = document.body.classList.contains("vertical") ? "vertical" : "wide";
    const canvas = (LAYOUT.canvas && LAYOUT.canvas[mode]) || { w: 1920, h: 1080 };
    (scene.items[mode] || []).forEach((item) => {
      if (!item.slot || item.w == null) return;
      placeWell(document.querySelector(`[data-slot="${item.slot}"]`), item, canvas);
    });

    const wells = (((LAYOUT.lumiaWells || {})[mode] || {})[sceneId]) || {};
    Object.entries(wells).forEach(([slot, box]) => {
      placeWell(document.querySelector(`[data-slot="${slot}"]`), box, canvas);
    });
  }

  function decorateWells() {
    document.querySelectorAll(".well").forEach((el) => {
      if (el.querySelector(".c")) return;
      ["tl", "tr", "bl", "br"].forEach((pos) => {
        const corner = document.createElement("i");
        corner.className = "c " + pos;
        el.appendChild(corner);
      });
    });
  }

  function mode() {
    if (params.has("preview")) document.body.classList.add("preview");
    if (params.has("setup")) document.body.classList.add("setup");
    decorateWells();
    applyCanvas();
  }

  function clock() {
    const nodes = document.querySelectorAll("[data-clock]");
    if (!nodes.length) return;
    const tick = () => {
      const text = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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

  let countdownTimer = null;
  const RING = 2 * Math.PI * 52;

  function countdown() {
    const node = document.querySelector("[data-countdown]");
    if (!node) return;
    if (countdownTimer) {
      clearInterval(countdownTimer);
      countdownTimer = null;
    }
    const ring = document.querySelector("[data-ring]");
    const total = Math.max(1, Math.round(Number(params.get("m") || STREAM.startingMinutes || 5) * 60));
    if (!STREAM.goLiveAt) STREAM.goLiveAt = Date.now() + total * 1000;

    const render = () => {
      const remaining = Math.max(0, Math.round((Number(STREAM.goLiveAt) - Date.now()) / 1000));
      if (ring) {
        const used = 1 - remaining / total;
        ring.style.strokeDasharray = String(RING);
        ring.style.strokeDashoffset = String(Math.max(0, RING * used));
      }
      if (remaining <= 0) {
        node.textContent = "GOING LIVE";
        node.classList.add("done");
        return;
      }
      node.classList.remove("done");
      node.textContent = `${pad(Math.floor(remaining / 60))}:${pad(remaining % 60)}`;
    };
    render();
    countdownTimer = setInterval(render, 250);
  }

  async function pullNow() {
    try {
      const res = await fetch("shared/now.json?t=" + Date.now(), { cache: "no-store" });
      if (!res.ok) return;
      const data = await res.json();
      const prevGo = STREAM.goLiveAt;
      Object.keys(data).forEach((key) => {
        if (data[key] == null) return;
        STREAM[key] = data[key];
      });
      applyIdentity();
      socials();
      if (document.querySelector("[data-countdown]") && String(prevGo) !== String(STREAM.goLiveAt)) {
        countdown();
      }
    } catch (_) {}
  }

  function backdrop() {
    const body = document.body;
    const scene = body.dataset.scene;
    if (!["starting", "brb", "ending"].includes(scene)) return;
    if (body.classList.contains("vertical")) return;

    const cfg = STREAM.backdrops || {};
    const src = cfg[scene];
    if (!src) return;

    let img = document.querySelector(".backdrop-photo");
    if (!img) {
      img = document.createElement("img");
      img.className = "backdrop-photo";
      img.alt = "";
      img.setAttribute("aria-hidden", "true");
      body.insertBefore(img, body.firstChild);
    }
    img.addEventListener("load", () => {
      if (img.naturalWidth) body.classList.add("has-backdrop");
    });
    img.addEventListener("error", () => body.classList.remove("has-backdrop"));
    img.src = src;
  }

  function dust() {
    const canvas = document.getElementById("dust");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const particles = [];
    const vertical = document.body.classList.contains("vertical");
    const W = vertical ? 1080 : 1920;
    const H = vertical ? 1920 : 1080;

    canvas.width = W;
    canvas.height = H;

    function hexRgb(hex, fallback) {
      const h = String(hex || "").replace("#", "");
      if (h.length !== 6) return fallback;
      return {
        r: parseInt(h.slice(0, 2), 16),
        g: parseInt(h.slice(2, 4), 16),
        b: parseInt(h.slice(4, 6), 16),
      };
    }
    const mint = hexRgb((STREAM.colors || {}).cyan, { r: 62, g: 234, b: 134 });
    const teal = hexRgb((STREAM.colors || {}).violet, { r: 20, g: 184, b: 166 });

    for (let i = 0; i < 42; i += 1) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.8 + 0.3,
        s: Math.random() * 0.35 + 0.05,
        a: Math.random() * 0.35 + 0.05,
        teal: Math.random() > 0.62,
      });
    }

    function frame() {
      ctx.clearRect(0, 0, W, H);
      particles.forEach((p) => {
        p.y -= p.s;
        p.x += Math.sin(p.y / 50) * 0.18;
        if (p.y < -4) {
          p.y = H + 4;
          p.x = Math.random() * W;
        }
        const c = p.teal ? teal : mint;
        ctx.beginPath();
        ctx.fillStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${p.a})`;
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      });
      requestAnimationFrame(frame);
    }
    frame();
  }

  applyColors();
  applyIdentity();
  socials();
  mode();
  clock();
  countdown();
  backdrop();
  dust();
  pullNow();
  setInterval(pullNow, 2000);
  window.addEventListener("resize", applyCanvas);
})();
