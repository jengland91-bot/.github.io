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
    const parts = [STREAM.style, STREAM.liveWord]
      .map((p) => String(p || "").trim())
      .filter(Boolean);
    return parts.length ? parts.join(" · ") : "";
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
    fill("[data-tagline]", taglineText());
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

  function mode() {
    if (params.has("preview")) document.body.classList.add("preview");
    if (params.has("setup")) document.body.classList.add("setup");
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
      node.textContent = `${pad(Math.floor(remaining / 60))}:${pad(remaining % 60)}`;
      remaining -= 1;
    };
    render();
    setInterval(render, 1000);
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

    for (let i = 0; i < 42; i += 1) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.8 + 0.3,
        s: Math.random() * 0.35 + 0.05,
        a: Math.random() * 0.35 + 0.05,
        violet: Math.random() > 0.62,
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
        ctx.beginPath();
        ctx.fillStyle = p.violet ? `rgba(167, 139, 250, ${p.a})` : `rgba(62, 224, 234, ${p.a})`;
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
  window.addEventListener("resize", applyCanvas);
})();
