"use strict";
// Mission Control front end. All data is rendered with textContent / DOM nodes, never innerHTML.

const TOKEN = window.MC_TOKEN;
const STATUS_REFRESH_MS = 60000;
const PANES = ["next", "sites", "council", "posts", "sales", "voice", "system"];
const $ = (id) => document.getElementById(id);

const state = { sites: {}, names: [], current: 0, view: "staging", system: null, pane: "next", mode: "text", undoSeconds: 300, councilDraft: "" };

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node[k] = v;
  }
  node.append(...children.filter((c) => c !== null && c !== undefined));
  return node;
}

async function api(path, body) {
  const opts = { headers: { "X-MC-Token": TOKEN } };
  if (body !== undefined) {
    opts.method = "POST";
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function setBadge(id, text, cls) {
  const b = $(id);
  b.textContent = text;
  b.className = "badge " + (cls || "");
}

// ---------- navigation ----------
function showPane(name) {
  state.pane = name;
  PANES.forEach((p) => $("pane-" + p).classList.toggle("active", p === name));
  document.querySelectorAll("#mainNav button").forEach((b) => b.classList.toggle("active", b.dataset.pane === name));
  if (name === "next") loadNext();
  if (name === "council") loadCouncil();
  if (name === "posts") loadPosts();
  if (name === "sales") loadSales();
  if (name === "voice") renderVoice();
  if (name === "system") loadSystem();
}

function buildNav() {
  PANES.forEach((p) => {
    const b = el("button", { textContent: p[0].toUpperCase() + p.slice(1), onclick: () => showPane(p) });
    b.dataset.pane = p;
    $("mainNav").appendChild(b);
  });
}

// ---------- sites + command box ----------
function currentSite() { return state.sites[state.names[state.current]]; }

function renderSites() {
  const name = state.names[state.current], s = currentSite();
  document.querySelectorAll(".tab").forEach((t, i) => t.classList.toggle("active", i === state.current));
  $("btnLive").classList.toggle("active", state.view === "live");
  $("btnStaging").classList.toggle("active", state.view === "staging");
  $("btnStaging").style.opacity = s.staging ? "1" : "0.35";
  const url = state.view === "staging" ? (s.staging || s.live) : s.live;
  const frameOk = frameAllowed(name, state.view === "staging" && s.staging ? "staging" : "live");
  $("blocked").style.display = frameOk ? "none" : "flex";
  $("frame").src = frameOk ? url : "about:blank";
  $("openSite").href = url;
  $("adminLink").href = url.replace(/\/$/, "") + "/wp-admin";
  const noStaging = state.view === "staging" && !s.staging;
  $("target").textContent = "Target: " + name + " (" + (noStaging ? "no staging" : state.view) + ")";
  $("liveConfirmRow").style.display = state.view === "live" ? "" : "none";
  $("confirmLive").checked = false;
}

function frameAllowed(name, view) {
  const r = state.system && state.system.sites[name] && state.system.sites[name][view];
  return !r || r.frame_ok !== false;
}

function showOut(text, isErr) {
  const out = $("out");
  out.style.display = "block";
  out.className = "out" + (isErr ? " err" : "");
  out.style.display = "block";
  out.textContent = text;
}

async function sendCommand() {
  const name = state.names[state.current], prompt = $("prompt").value.trim();
  if (!prompt) return;
  if (state.view === "staging" && !currentSite().staging) {
    showOut("This site has no staging. Switch to Live and confirm, or pick another site.", true);
    return;
  }
  $("send").disabled = true;
  showOut("Working… this can take a minute.", false);
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: TOKEN, site: name, view: state.view, prompt, confirm_live: $("confirmLive").checked }),
    });
    const data = await res.json();
    showOut(data.reply || data.error || "No response.", !res.ok);
    if (res.ok) speak(data.reply);
    if (res.ok) { $("prompt").value = ""; $("frame").src = $("frame").src; }
  } catch (e) {
    showOut("Could not reach the helper. Is start-mission-control.cmd running?", true);
  } finally {
    $("send").disabled = false;
  }
}

function initSites(data) {
  state.sites = data;
  state.names = Object.keys(data);
  state.names.forEach((n, i) => {
    $("tabs").appendChild(el("button", { class: "tab", textContent: n, onclick: () => { state.current = i; renderSites(); } }));
  });
  $("btnLive").onclick = () => { state.view = "live"; renderSites(); };
  $("btnStaging").onclick = () => { state.view = "staging"; renderSites(); };
  $("send").onclick = sendCommand;
  onEnter($("prompt"), sendCommand);
  attachMic($("prompt"), $("micPrompt"));
  renderSites();
}

// ---------- system status ----------
async function loadSystem() {
  try {
    state.system = await api("/api/status");
  } catch (e) {
    $("systemRoot").replaceChildren(el("div", { class: "empty", textContent: "Status unavailable: " + e.message }));
    return;
  }
  renderBadges();
  renderSystem();
}

function stripeSummary(stripe) {
  const modes = Object.values(stripe || {});
  if (!modes.length) return { text: "Stripe: unknown", cls: "" };
  if (modes.includes("mixed")) return { text: "Stripe: MIXED keys", cls: "bad" };
  if (modes.includes("live")) return { text: "Stripe: LIVE", cls: "bad" };
  if (modes.every((m) => m === "test")) return { text: "Stripe: test mode", cls: "ok" };
  return { text: "Stripe: unknown", cls: "warn" };
}

function renderBadges() {
  const sys = state.system;
  const s = stripeSummary(sys.stripe);
  setBadge("badgeStripe", s.text, s.cls);
  const cells = Object.values(sys.sites).flatMap((v) => Object.values(v));
  const down = cells.filter((c) => !c.up).length;
  setBadge("badgeSites", down ? `Sites: ${down} down` : "Sites: all up", down ? "bad" : "ok");
  setBadge("badgeVoice", sys.voice.running ? "Voice: on" : "Voice: off", sys.voice.running ? "ok" : "");
  if (state.pane === "sites") renderSites();
}

function renderSystem() {
  const sys = state.system, root = $("systemRoot");
  const rows = [];
  for (const [name, views] of Object.entries(sys.sites)) {
    for (const [view, r] of Object.entries(views)) {
      rows.push(el("tr", {},
        el("td", {}, el("span", { class: "dot " + (r.up ? "ok" : "bad") }), name),
        el("td", { textContent: view }),
        el("td", { textContent: r.status === null ? "unreachable" : String(r.status) }),
        el("td", { textContent: r.ms === null ? "—" : r.ms + " ms" }),
        el("td", { textContent: r.frame_ok ? "yes" : "blocked" })));
    }
  }
  const git = sys.git.error ? sys.git.error
    : `${sys.git.branch} · ${sys.git.uncommitted} uncommitted · ${sys.git.unpushed} unpushed · last: ${sys.git.last_commit}`;
  root.replaceChildren(
    el("h2", { textContent: "Sites" }),
    el("table", {}, el("thead", {}, el("tr", {}, ...["Site", "View", "HTTP", "Speed", "Embeddable"].map((h) => el("th", { textContent: h })))),
      el("tbody", {}, ...rows)),
    el("h2", { textContent: "Stripe mode (checkout page)" }),
    el("div", { textContent: Object.entries(sys.stripe || {}).map(([v, m]) => `${v}: ${m}`).join("   ") || "unknown" }),
    el("h2", { textContent: "Repo" }), el("div", { textContent: git }),
    el("h2", { textContent: "Backup log" }), el("div", { textContent: sys.backup.last_line || "no backup log found" }),
    el("div", { class: "row", style: "margin-top:16px" }, el("button", { class: "btn", textContent: "Refresh", onclick: loadSystem })));
}

// ---------- sales ----------
async function loadSales() {
  const root = $("salesRoot");
  try {
    renderSales(await api("/api/sales"));
  } catch (e) {
    root.replaceChildren(el("div", { class: "empty", textContent: "Sales data unavailable: " + e.message }));
  }
}

function card(n, label) {
  return el("div", { class: "card" }, el("div", { class: "n", textContent: String(n) }), el("div", { class: "l", textContent: label }));
}

function renderSales(data) {
  const b = data.scoreboard, root = $("salesRoot");
  const mrr = el("input", { type: "number", min: "0", value: String(b.mrr), size: 8 });
  const cash = el("input", { type: "number", min: "0", value: String(b.cash), size: 8 });
  const saveMoney = () => api("/api/money", { mrr: Number(mrr.value), cash: Number(cash.value) }).then(loadSales).catch((e) => alert(e.message));

  const newLead = { business: el("input", { placeholder: "Business" }), contact: el("input", { placeholder: "Contact" }),
    email: el("input", { placeholder: "Email" }) };
  const addLead = () => api("/api/leads", { action: "add", ...Object.fromEntries(Object.entries(newLead).map(([k, i]) => [k, i.value])) })
    .then(loadSales).catch((e) => alert(e.message));

  const leadRows = data.leads.map((l) => {
    const sel = el("select", { onchange: () => api("/api/leads", { action: "update", id: l.id, status: sel.value }).then(loadSales).catch((e) => alert(e.message)) },
      ...data.statuses.map((s) => el("option", { value: s, textContent: s, selected: s === l.status })));
    return el("tr", {}, el("td", { textContent: l.business }), el("td", { textContent: l.contact }), el("td", { textContent: l.email }),
      el("td", {}, sel),
      el("td", {}, el("button", { class: "btn", textContent: "Delete", onclick: () => confirm("Delete " + l.business + "?") && api("/api/leads", { action: "delete", id: l.id }).then(loadSales) })));
  });

  const templates = data.templates.map((t) => el("div", { class: "tpl" },
    el("strong", { textContent: t.title }),
    el("pre", { textContent: t.body }),
    el("label", {}, el("input", { type: "checkbox", checked: t.approved, onchange: (e) => api("/api/approval", { id: t.id, approved: e.target.checked }).catch((err) => alert(err.message)) }),
      " Alan approves this draft (nothing is sent from here)")));

  root.replaceChildren(
    el("div", { class: "cards" }, card(b.leads, "Leads"), card(b.conversations, "Conversations"), card(b.calls, "Calls booked"),
      card(b.sales, "Sales"), card("$" + b.mrr, "MRR"), card("$" + b.cash, "Cash")),
    el("div", { class: "row" }, "MRR $", mrr, "Cash $", cash, el("button", { class: "btn", textContent: "Save", onclick: saveMoney })),
    el("h2", { textContent: "Leads" }),
    leadRows.length ? el("table", {}, el("thead", {}, el("tr", {}, ...["Business", "Contact", "Email", "Status", ""].map((h) => el("th", { textContent: h })))), el("tbody", {}, ...leadRows))
      : el("div", { class: "empty", textContent: "No leads yet. Add the first one below." }),
    el("div", { class: "row", style: "margin-top:10px" }, newLead.business, newLead.contact, newLead.email,
      el("button", { class: "btn primary", textContent: "Add lead", onclick: addLead })),
    el("h2", { textContent: "Outreach drafts" }),
    ...(templates.length ? templates : [el("div", { class: "empty", textContent: "No drafts found in docs/smb-outreach-drafts.md" })]));
}

// ---------- voice ----------
function renderVoice() {
  const running = state.system && state.system.voice.running;
  const act = (action) => api("/api/voice", { action }).then(() => loadSystem().then(renderVoice)).catch((e) => alert(e.message));
  $("voiceRoot").replaceChildren(
    el("h2", { textContent: "Jarvis voice assistant" }),
    el("div", { textContent: running ? "Running — listening for “Hey Jarvis”." : "Stopped." }),
    el("div", { class: "row", style: "margin-top:12px" },
      el("button", { class: "btn primary", textContent: "Start", disabled: !!running, onclick: () => act("start") }),
      el("button", { class: "btn", textContent: "Stop", disabled: !running, onclick: () => act("stop") })),
    el("h2", { textContent: "Talk to Jarvis by text" }),
    jarvisTextBox(),
    el("h2", { textContent: "Things to say" }),
    el("div", { textContent: "“Hey Jarvis, status” · “Hey Jarvis, run a backup” · “Hey Jarvis, ask Claude …” · anything else goes to the free local model." }),
    el("div", { class: "empty", textContent: "Jarvis opens a microphone window on this PC. Stop it here when you're done." }));
}

// ---------- input mode, mic, speech ----------
const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

function toast(msg, kind) {
  const t = el("div", { class: "toast " + (kind || ""), textContent: msg });
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 6000);
}

function setMode(mode) {
  state.mode = mode;
  document.body.classList.toggle("mode-voice", mode === "voice");
  $("modeToggle").textContent = "Input: " + (mode === "voice" ? "Voice" : "Text");
  try { localStorage.setItem("mc-mode", mode); } catch (e) { /* storage unavailable */ }
  if (mode === "voice" && !SpeechRec) toast("This browser has no speech recognition. Use Chrome or Edge, or stay in Text mode.", "err");
}

function speak(text) {
  if (state.mode !== "voice" || !text || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(text.slice(0, 600)));
}

/** Enter submits, Shift+Enter inserts a newline. */
function onEnter(textarea, submit) {
  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit(); }
  });
}

/** Dictation fills the box only; the human still presses Enter to send or post. */
function attachMic(textarea, button) {
  let rec = null;
  button.addEventListener("click", () => {
    if (!SpeechRec) { toast("Speech recognition isn't available in this browser.", "err"); return; }
    if (rec) { rec.stop(); return; }
    rec = new SpeechRec();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = true;
    const base = textarea.value ? textarea.value.trimEnd() + " " : "";
    rec.onresult = (ev) => {
      textarea.value = base + Array.from(ev.results).map((r) => r[0].transcript).join(" ").trim();
      textarea.dispatchEvent(new Event("input"));
    };
    rec.onend = () => { rec = null; button.classList.remove("listening"); };
    rec.onerror = (ev) => toast("Mic error: " + ev.error, "err");
    button.classList.add("listening");
    rec.start();
  });
}

function jarvisTextBox() {
  const ta = el("textarea", { placeholder: "Type what you'd say, e.g. “status” or “ask Claude …”. Enter sends.", maxLength: 500, rows: 2 });
  const out = el("div", { class: "out" });
  const mic = el("button", { class: "btn mic", textContent: "🎤" });
  const send = async () => {
    const text = ta.value.trim();
    if (!text) return;
    out.style.display = "block"; out.className = "out"; out.textContent = "Thinking… the local model can take a minute.";
    try {
      const data = await api("/api/say", { text });
      out.textContent = data.reply; ta.value = ""; speak(data.reply);
    } catch (e) { out.className = "out err"; out.textContent = e.message; }
  };
  onEnter(ta, send);
  attachMic(ta, mic);
  return el("div", {}, el("div", { class: "row" }, ta, mic, el("button", { class: "btn primary", textContent: "Send", onclick: send })), out);
}

// ---------- posts ----------
async function loadPosts() {
  try { renderPosts(await api("/api/posts")); }
  catch (e) { $("postsRoot").replaceChildren(el("div", { class: "empty", textContent: "Posts unavailable: " + e.message })); }
}

function renderPosts(data) {
  state.undoSeconds = data.undo_seconds;
  const usable = data.platforms.filter((p) => p.available && p.configured);
  let remembered = [];
  try { remembered = JSON.parse(localStorage.getItem("mc-platforms") || "[]"); } catch (e) { /* storage unavailable */ }
  const boxes = data.platforms.map((p) => {
    const ready = p.available && p.configured;
    const preTick = ready && (usable.length === 1 || remembered.includes(p.id));
    const cb = el("input", { type: "checkbox", value: p.id, disabled: !ready, checked: preTick });
    const note = p.available ? (p.configured ? "" : " (not set up)") : " (unavailable)";
    const label = el("label", { class: "pcheck" + (ready ? "" : " off"), title: p.reason || "" }, cb, " " + p.label + note);
    return { id: p.id, cb, label };
  });
  const picked = () => boxes.filter((b) => b.cb.checked).map((b) => b.id);
  boxes.forEach((b) => b.cb.addEventListener("change", () => {
    try { localStorage.setItem("mc-platforms", JSON.stringify(picked())); } catch (e) { /* storage unavailable */ }
  }));
  const ta = el("textarea", { placeholder: "Type your post. Enter publishes immediately. Shift+Enter for a new line.", maxLength: 5000 });
  const flags = el("div", { class: "flags" });
  const mic = el("button", { class: "btn mic", textContent: "🎤 Dictate" });
  const counter = el("span", { class: "empty" });
  let timer = null;

  ta.addEventListener("input", () => {
    counter.textContent = ta.value.length + " chars";
    clearTimeout(timer);
    timer = setTimeout(async () => {
      if (!ta.value.trim()) { flags.textContent = ""; return; }
      try {
        const r = await api("/api/preflight", { platform: picked()[0] || "facebook", text: ta.value });
        flags.textContent = r.flags.length ? "Heads up (won't block): " + r.flags.join(" · ") : "";
      } catch (e) { flags.textContent = ""; }
    }, 400);
  });

  let busy = false;
  const publish = async () => {
    const text = ta.value;
    if (busy || !text.trim()) return;
    const platforms = picked();
    if (!platforms.length) { toast("Tick at least one place to post to.", "err"); return; }
    busy = true;
    try {
      const { results } = await api("/api/post", { platforms, text });
      const ok = results.filter((r) => r.ok).map((r) => r.platform);
      const failed = results.filter((r) => !r.ok);
      if (ok.length) { ta.value = ""; flags.textContent = ""; counter.textContent = ""; }
      if (!failed.length) { toast("Posted ✓ to " + ok.join(", ") + " — you can undo it below for a few minutes.", "ok"); speak("Posted."); }
      else toast((ok.length ? "Posted to " + ok.join(", ") + ". " : "") + "Failed: " + failed.map((r) => `${r.platform} (${r.error})`).join("; "), "err");
      await loadPosts();
    } catch (e) {
      toast(e.message, "err");
    } finally { busy = false; }
  };
  onEnter(ta, publish);
  attachMic(ta, mic);

  const hist = data.posts.length ? data.posts.map((p) => {
    const age = (Date.now() - new Date(p.created).getTime()) / 1000;
    const canUndo = !p.deleted && age < state.undoSeconds;
    return el("div", { class: "item" + (p.deleted ? " deleted" : "") },
      el("div", { class: "meta", textContent: `${p.platform} · ${new Date(p.created).toLocaleString()}${p.deleted ? " · removed" : ""}` }),
      el("div", { textContent: p.text }),
      canUndo ? el("button", { class: "btn", style: "margin-top:6px", textContent: "Undo (remove from " + p.platform + ")",
        onclick: () => confirm("Remove this post from " + p.platform + "?") && api("/api/post/undo", { id: p.id }).then(loadPosts).catch((e) => toast(e.message, "err")) }) : null);
  }) : [el("div", { class: "empty", textContent: "Nothing posted from here yet." })];

  const unavailable = data.platforms.filter((p) => !p.available).map((p) => el("div", { class: "empty", textContent: `${p.label}: ${p.reason}` }));
  const notReady = data.platforms.filter((p) => p.available && !p.configured);

  $("postsRoot").replaceChildren(
    el("h2", { textContent: "Post now" }),
    usable.length ? null : el("div", { class: "flags", textContent: "Posting isn't set up yet: add MC_FB_PAGE_ID and MC_FB_PAGE_TOKEN to mission-control/.env and restart the helper." }),
    el("div", { class: "postbox" }, el("div", { class: "row" }, el("strong", { textContent: "Post to (tick as many as you like):" }), ...boxes.map((b) => b.label)),
      el("div", { class: "row", style: "margin:8px 0" }, mic, counter), ta, flags),
    el("div", { class: "row", style: "margin-top:8px" }, el("button", { class: "btn primary", textContent: "Post", onclick: publish }),
      el("span", { class: "empty", textContent: "Enter also posts. Dictation only fills the box; you still press Enter." })),
    ...notReady.map((p) => el("div", { class: "empty", textContent: p.label + ": credentials not added yet." })),
    ...unavailable,
    el("h2", { textContent: "Posted from here" }),
    el("div", { class: "hist" }, ...hist));
}

// ---------- council ----------
async function loadCouncil() {
  try { renderCouncil(await api("/api/council")); }
  catch (e) { $("councilRoot").replaceChildren(el("div", { class: "empty", textContent: "Council unavailable: " + e.message })); }
}

async function checkCouncilBanner() {
  try {
    const data = await api("/api/council");
    const banner = $("councilBanner");
    if (data.asked_today || data.dismissed_today) { banner.style.display = "none"; return; }
    banner.replaceChildren(
      el("span", { textContent: "Does Axiom or you have a question for the council today?" }),
      el("button", { class: "btn primary", textContent: "Ask now", onclick: () => { banner.style.display = "none"; showPane("council"); } }),
      el("button", { class: "btn", textContent: "Not today", onclick: () => api("/api/council/dismiss", {}).then(() => { banner.style.display = "none"; }) }));
    banner.style.display = "flex";
  } catch (e) { /* banner is optional */ }
}

function copyText(text, okMsg) {
  navigator.clipboard.writeText(text).then(() => toast(okMsg, "ok"), () => toast("Copy failed. Select the text and copy it by hand.", "err"));
}

function renderCouncil(data) {
  const who = el("select", {}, el("option", { value: "Alan", textContent: "Alan asks" }), el("option", { value: "Axiom", textContent: "Axiom asks" }));
  const topic = el("select", {}, ...Object.entries(data.topics).map(([t, skill]) => el("option", { value: t, textContent: `${t} → ${skill}` })));
  const ta = el("textarea", { placeholder: "Your question for the council. Enter submits, Shift+Enter for a new line.", maxLength: 2000, rows: 3 });
  const mic = el("button", { class: "btn mic", textContent: "🎤" });
  const ask = async () => {
    if (!ta.value.trim()) return;
    try {
      await api("/api/council/ask", { question: ta.value, asked_by: who.value, topic: topic.value });
      toast("Question logged for the council.", "ok");
      checkCouncilBanner();
      loadCouncil();
    } catch (e) { toast(e.message, "err"); }
  };
  if (state.councilDraft) { ta.value = state.councilDraft; state.councilDraft = ""; }
  onEnter(ta, ask);
  attachMic(ta, mic);

  const open = data.questions.filter((q) => q.status === "open");
  const done = data.questions.filter((q) => q.status !== "open");

  const questionCard = (q) => {
    const answerBox = el("textarea", { placeholder: "Paste or type the council's answer", rows: 3, maxLength: 8000 });
    const source = el("select", {}, ...["Alan", "ECC", "GPT", "Claude", "DeepSeek", "Kimi", "Other"].map((s) => el("option", { value: s, textContent: s })));
    const save = () => api("/api/council/answer", { id: q.id, answer: answerBox.value, source: source.value }).then(loadCouncil).catch((e) => toast(e.message, "err"));
    return el("div", { class: "tpl" },
      el("div", { class: "meta", textContent: `${q.asked_by} · ${q.topic} · ${new Date(q.created).toLocaleString()} · in-repo reviewer ${q.reviewer}` }),
      el("div", { textContent: q.question }),
      q.status === "open" ? el("div", {},
        el("div", { class: "row", style: "margin:8px 0" },
          el("button", { class: "btn", textContent: "Copy package for other models", onclick: () => copyText(q.package, "Package copied. Paste it into GPT, Claude, DeepSeek or Kimi.") }),
          el("button", { class: "btn primary", textContent: "Ask ECC now",
            onclick: (ev) => { if (!confirm("ECC will answer using your Claude plan. Continue?")) return;
              ev.target.disabled = true; ev.target.textContent = "ECC is thinking…";
              api("/api/council/ecc", { id: q.id }).then(loadCouncil).catch((e) => { toast(e.message, "err"); ev.target.disabled = false; ev.target.textContent = "Ask ECC now"; }); } })),
        el("div", { class: "row" }, answerBox, source, el("button", { class: "btn", textContent: "Record answer", onclick: save })))
        : el("div", {}, el("div", { class: "meta", style: "margin-top:8px", textContent: `Answered by ${q.answer_source}` }), el("pre", { textContent: q.answer })),
      el("button", { class: "btn", style: "margin-top:6px", textContent: "Delete",
        onclick: () => confirm("Delete this question?") && api("/api/council/delete", { id: q.id }).then(loadCouncil) }));
  };

  $("councilRoot").replaceChildren(
    el("h2", { textContent: "Ask the council" }),
    el("div", { class: "row" }, who, topic, mic),
    ta,
    el("div", { class: "row", style: "margin-top:8px" }, el("button", { class: "btn primary", textContent: "Submit question", onclick: ask }),
      el("span", { class: "empty", textContent: "Pick a topic and I'll suggest the matching review skill." })),
    el("h2", { textContent: `Open (${open.length})` }),
    ...(open.length ? open.map(questionCard) : [el("div", { class: "empty", textContent: "No open questions." })]),
    el("h2", { textContent: `Answered (${done.length})` }),
    ...(done.length ? done.map(questionCard) : [el("div", { class: "empty", textContent: "Nothing answered yet." })]));
}

// ---------- next click ----------
async function loadNext() {
  const root = $("nextRoot");
  root.replaceChildren(el("div", { class: "empty", textContent: "Working out your next step…" }));
  try { renderNext(await api("/api/next")); }
  catch (e) { root.replaceChildren(el("div", { class: "empty", textContent: "Couldn't work out the next step: " + e.message })); }
}

function goTo(go) {
  if (go.type === "url") window.open(go.target, "_blank", "noopener");
  else showPane(go.target);
}

function renderNext(plan) {
  const a = plan.now;
  const complete = a.id === "idle";
  const act = (path, extra) => api(path, { id: a.id }).then(loadNext).catch((e) => toast(e.message, extra || "err"));
  const doubt = () => api("/api/next/doubt", { id: a.id })
    .then((r) => { state.councilDraft = r.draft; showPane("council"); toast("Your question is filled in. Press Enter to send it to the council.", "ok"); })
    .catch((e) => toast(e.message, "err"));

  const done = plan.delivered.length + plan.skipped.length;
  const pct = plan.total_stops ? Math.round((done / plan.total_stops) * 100) : 100;
  const header = el("div", { class: "route-head" },
    el("span", { textContent: complete ? "Route complete" : `Stop ${plan.stop_number} of ${plan.total_stops}` }),
    el("span", { class: "empty", textContent: `${plan.delivered.length} delivered${plan.skipped.length ? " · " + plan.skipped.length + " rerouted" : ""}` }));
  const bar = el("div", { class: "bar" }, el("div", { class: "bar-fill", style: `width:${pct}%` }));

  const stopRow = (cls, mark, title) => el("div", { class: "stop " + cls }, el("span", { class: "mark", textContent: mark }), el("span", { textContent: title }));
  const routeList = [
    ...plan.delivered.map((s) => stopRow("delivered", "✓", s.title)),
    ...plan.skipped.map((s) => stopRow("skipped", "↷", s.title)),
    ...(complete ? [] : [stopRow("current", "▶", a.title)]),
    ...plan.upcoming.map((u, i) => stopRow("upcoming", String(plan.stop_number + 1 + i), u.title)),
  ];
  const hidden = plan.route.length - 1 - plan.upcoming.length;
  if (hidden > 0) routeList.push(el("div", { class: "stop upcoming" }, el("span", { class: "mark", textContent: "…" }), el("span", { textContent: `${hidden} more stop(s) on today's route` })));

  $("nextRoot").replaceChildren(
    el("div", { class: "route-wrap" }, header, bar),
    el("div", { class: "next-card" },
      el("div", { class: "next-label", textContent: complete ? "ALL DELIVERED" : "YOUR NEXT STOP" }),
      el("div", { class: "next-title", textContent: a.title }),
      el("div", { class: "next-why", textContent: a.why }),
      el("button", { class: "btn primary go", textContent: a.go.type === "url" ? "GO →  (opens in a new tab)" : "GO →", onclick: () => goTo(a.go) }),
      complete ? null : el("div", { class: "row", style: "margin-top:14px" },
        a.manual ? el("button", { class: "btn", textContent: "✓ Delivered", onclick: () => act("/api/next/done") }) : null,
        el("button", { class: "btn", textContent: "Skip (reroute)", onclick: () => act("/api/next/skip") }),
        el("button", { class: "btn", textContent: "Doesn't seem right → call dispatch (ask the council)", onclick: doubt }))),
    el("div", { class: "route-wrap" }, el("h2", { textContent: "Today's route" }), ...routeList));
}

// ---------- boot ----------
buildNav();
$("modeToggle").onclick = () => setMode(state.mode === "voice" ? "text" : "voice");
try { setMode(localStorage.getItem("mc-mode") === "voice" ? "voice" : "text"); } catch (e) { setMode("text"); }
checkCouncilBanner();
fetch("/sites.json").then((r) => r.json()).then((data) => { initSites(data); showPane("next"); loadSystem(); });
setInterval(() => { if (state.pane !== "system") loadSystem(); }, STATUS_REFRESH_MS);
