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
    const text = value == null ? "" : String(value);
    document.querySelectorAll(selector).forEach((el) => {
      el.textContent = text;
    });
  }

  function currentGame() {
    const fromUrl = params.get("game") || params.get("title");
    if (fromUrl && String(fromUrl).trim()) return String(fromUrl).trim();
    if (window.GAME_TITLE && String(window.GAME_TITLE).trim()) {
      return String(window.GAME_TITLE).trim();
    }
    return String(STREAM.game || "").trim();
  }

  function taglineText() {
    const custom = String(STREAM.tagline || "").trim();
    if (custom) return custom;
    const gameOnPage = document.querySelector("[data-game]");
    const parts = gameOnPage
      ? [STREAM.style, STREAM.liveWord]
      : [currentGame(), STREAM.style, STREAM.liveWord];
    const clean = parts.map((p) => String(p || "").trim()).filter(Boolean);
    if (!clean.length) return "";
    return clean.join(". ") + ".";
  }

  function applyIdentity() {
    const name = params.get("name") || STREAM.name;
    const game = currentGame();
    fill("[data-name]", name);
    fill("[data-brand]", STREAM.brand);
    fill("[data-game]", game);
    document.querySelectorAll("[data-game]").forEach((el) => {
      el.hidden = !game;
    });
    fill("[data-tagline]", taglineText());
    fill("[data-handle]", STREAM.handle);
    fill("[data-brb]", STREAM.brbMessage);
    fill("[data-ending]", STREAM.endingMessage);
    fill("[data-chatting-title]", STREAM.chattingTitle);
    fill("[data-desk-title]", STREAM.deskTitle);
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
    document.querySelectorAll(".brand").forEach((el) => {
      const brand = String(STREAM.brand || "").trim();
      const handle = String(STREAM.handle || "").trim();
      el.classList.toggle("is-empty", !brand && !handle);
      const mark = el.querySelector("[data-brand]");
      if (mark) mark.hidden = !brand;
    });
  }

  function socialHandle(value) {
    if (!value) return "";
    let s = String(value).trim();
    s = s.replace(/^https?:\/\//i, "");
    s = s.replace(/^www\./i, "");
    s = s.replace(/^(youtube\.com\/@|youtube\.com\/c\/|youtube\.com\/channel\/|youtube\.com\/|twitch\.tv\/|tiktok\.com\/@|tiktok\.com\/|kick\.com\/|instagram\.com\/|facebook\.com\/|x\.com\/|twitter\.com\/|discord\.gg\/|discord\.com\/invite\/|discord\.com\/users\/)/i, "");
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

  function overlayPrefix() {
    const script = document.querySelector('script[src*="overlay.js"]');
    const src = (script && script.getAttribute("src")) || "";
    if (src.indexOf("../") !== -1 || document.body.classList.contains("vertical")) {
      return "../";
    }
    return "";
  }

  function resolveOverlayPath(path) {
    if (!path) return "";
    const p = String(path).trim();
    if (!p) return "";
    if (/^https?:\/\//i.test(p) || p.startsWith("/") || p.startsWith("../") || p.startsWith("./")) {
      return p;
    }
    return overlayPrefix() + p;
  }

  function backdrop() {
    const body = document.body;
    const scene = body.classList.contains("scene-starting")
      ? "starting"
      : body.classList.contains("scene-brb")
        ? "brb"
        : body.classList.contains("scene-ending")
          ? "ending"
          : null;
    if (!scene) return;

    const vertical = body.classList.contains("vertical");
    const cfg = STREAM.backdrops || {};
    const wide = resolveOverlayPath(cfg[scene] || `shared/backdrops/${scene}.jpg`);
    const vert = resolveOverlayPath(
      cfg[`${scene}Vertical`] || `shared/backdrops/${scene}-vertical.jpg`
    );

    let img = document.querySelector(".backdrop-photo");
    if (!img) {
      img = document.createElement("img");
      img.className = "backdrop-photo";
      img.setAttribute("data-backdrop", scene);
      body.insertBefore(img, body.firstChild);
    }
    img.alt = "";
    img.setAttribute("aria-hidden", "true");

    const seen = new Set();
    const list = [];
    [vertical ? vert : "", wide].forEach((src) => {
      if (src && !seen.has(src)) {
        seen.add(src);
        list.push(src);
      }
    });

    let i = 0;
    let settled = false;
    const fail = () => {
      if (settled) return;
      settled = true;
      body.classList.remove("has-backdrop");
    };
    const tryNext = () => {
      if (settled) return;
      if (i >= list.length) {
        fail();
        return;
      }
      img.src = list[i];
      i += 1;
    };
    img.addEventListener("load", () => {
      if (settled) return;
      if (!img.naturalWidth) {
        tryNext();
        return;
      }
      settled = true;
      body.classList.add("has-backdrop");
    });
    img.addEventListener("error", tryNext);
    tryNext();
  }

  function dust() {
    const canvas = document.getElementById("dust");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const particles = [];
    const count = 58;
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
        const grit = Math.random();
        particles.push({
          x: Math.random() * W,
          y: Math.random() * H,
          r: grit > 0.82 ? Math.random() * 4.5 + 1.4 : Math.random() * 2.1 + 0.35,
          s: Math.random() * 0.55 + 0.08,
          a: Math.random() * 0.4 + 0.06,
          drift: Math.random() * 0.42 + 0.04,
          moss: grit > 0.7,
        });
      }
    }

    function frame() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.y -= p.s;
        p.x += Math.sin(p.y / 38) * p.drift;
        if (p.y < -6) {
          p.y = H + 6;
          p.x = Math.random() * W;
        }
        ctx.beginPath();
        ctx.fillStyle = p.moss
          ? `rgba(122, 154, 92, ${p.a * 0.75})`
          : `rgba(196, 168, 118, ${p.a})`;
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
  backdrop();
  dust();
  window.addEventListener("resize", applyCanvas);
})();
