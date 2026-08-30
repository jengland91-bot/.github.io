/**
 * Redirects a Meld Browser layer to Social Stream Ninja or Lumia.
 * Session / Lumia URL come from overlays/shared/config.js so you only paste them once.
 */
(function () {
  const STREAM = window.STREAM || {};
  const params = new URLSearchParams(location.search);
  const kind = document.body.getAttribute("data-kind") || "chat";

  function wait(title, lines) {
    const wrap = document.createElement("div");
    wrap.className = "wait";
    wrap.innerHTML =
      '<div class="kicker">' +
      title +
      "</div>" +
      lines.map((line) => "<p>" + line + "</p>").join("");
    document.body.innerHTML = "";
    document.body.appendChild(wrap);
  }

  function go(url) {
    window.location.replace(url);
  }

  if (kind === "lumia") {
    const url = (params.get("url") || (STREAM.lumia && STREAM.lumia.overlayUrl) || "").trim();
    if (!url) {
      wait("LUMIA ALERTS", [
        "Paste your Lumia overlay URL into <code>overlays/shared/config.js</code> under <code>lumia.overlayUrl</code>.",
        "Save, then reload this Browser layer in Meld.",
        "Leave it blank if viewers should not see Lumia — keep chat-for-you on the gaming monitor.",
      ]);
      return;
    }
    go(url);
    return;
  }

  const session = (params.get("session") || (STREAM.ssn && STREAM.ssn.session) || "").trim();
  if (!session) {
    wait("SOCIAL STREAM NINJA", [
      "Copy the session ID from the Social Stream Ninja extension or app.",
      "Paste it into <code>overlays/shared/config.js</code> under <code>ssn.session</code>.",
      "Use that same ID in the dock. Save, then reload this layer in Meld.",
    ]);
    return;
  }

  const page = kind === "featured" ? "featured.html" : "sampleoverlay.html";
  const extra =
    kind === "featured"
      ? "&fade&center&showtime=8000&showsource"
      : "&transparent&darkmode&compact";
  const cssFile = kind === "featured" ? "featured.css" : "chat.css";
  const target =
    "https://socialstream.ninja/" +
    page +
    "?session=" +
    encodeURIComponent(session) +
    extra;

  fetch(cssFile)
    .then(function (res) {
      if (!res.ok) throw new Error("css");
      return res.text();
    })
    .then(function (css) {
      const b64 = btoa(unescape(encodeURIComponent(css)));
      go(target + "&b64css=" + encodeURIComponent(b64));
    })
    .catch(function () {
      go(target);
    });
})();
