const fs = require('fs');
const path = require('path');
const { loadBars } = require('../src/data-loader.js');

const ENGINE_SRC = fs.readFileSync(path.join(__dirname, '..', 'src', 'engine.js'), 'utf8');
const bars = loadBars(path.join(__dirname, '..', 'data', 'spy_5m.csv'));
const BARS_JSON = JSON.stringify(bars.map(b => ({
  t: b.t, time: b.time, o: b.open, h: b.high, l: b.low, c: b.close, v: b.volume,
})));

const html = `<!doctype html>
<title>Axiom Replay Lab</title>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
  --ground: #0a0d12; --surface: #12161f; --surface-raised: #171c28; --border: #232a3a;
  --text: #e8ebf2; --text-dim: #8a93a8; --accent: #3e8fff;
  --green: #29b6a3; --red: #f2555a; --amber: #f0ad3f; --violet: #a980ff;
  --font-ui: 'IBM Plex Sans', -apple-system, Segoe UI, Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, 'Cascadia Code', Consolas, monospace;
}
* { box-sizing: border-box; }
body { margin:0; background:var(--ground); color:var(--text); font: 13px/1.45 var(--font-ui); }
.num, header .value, table, input[type=number] { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
#app { display:grid; grid-template-columns: 1fr 320px; grid-template-rows: auto auto 1fr; height:100vh; gap:1px; background:var(--border); }
header { grid-column: 1 / 3; background:var(--surface); padding:12px 18px; display:flex; align-items:center; gap:22px; flex-wrap:wrap; }
header h1 { font-family: var(--font-ui); font-size:14px; margin:0; font-weight:700; letter-spacing:.02em; color:var(--text); white-space:nowrap; }
header h1 span { color:var(--accent); }
header .stat { display:flex; flex-direction:column; gap:3px; }
header .stat .label { color:var(--text-dim); font-size:9.5px; text-transform:uppercase; letter-spacing:.08em; font-weight:500; }
header .stat .value { font-weight:600; font-size:14px; letter-spacing:.01em; }
.up { color:var(--green); } .down { color:var(--red); }
#chartWrap { background:var(--surface); position:relative; padding:10px; overflow:hidden; }
canvas { display:block; width:100%; }
#sidebar { background:var(--surface); overflow-y:auto; padding:14px; display:flex; flex-direction:column; gap:16px; }
#tradesPanel { grid-column: 1 / 3; background:var(--surface); max-height:220px; overflow:auto; padding:10px 14px; }
table { width:100%; border-collapse:collapse; font-size:11px; }
th, td { padding:4px 7px; text-align:right; border-bottom:1px solid var(--border); white-space:nowrap; }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align:left; }
th { color:var(--text-dim); font-weight:500; font-family: var(--font-ui); font-size:10px; text-transform:uppercase; letter-spacing:.06em; position:sticky; top:0; background:var(--surface); }
fieldset { border:1px solid var(--border); border-radius:6px; padding:10px 12px; }
legend { color:var(--text-dim); font-size:10.5px; padding:0 5px; text-transform:uppercase; letter-spacing:.08em; font-weight:600; }
.row { display:flex; align-items:center; justify-content:space-between; gap:8px; margin:6px 0; }
.row label { color:var(--text-dim); }
input[type=number] { width:64px; background:var(--ground); border:1px solid var(--border); color:var(--text); border-radius:4px; padding:4px 6px; font-size:12px; }
input[type=number]:focus, select:focus, button:focus-visible { outline:2px solid var(--accent); outline-offset:1px; }
input[type=checkbox] { accent-color: var(--accent); }
button { background:var(--surface-raised); color:var(--text); border:1px solid var(--border); border-radius:5px; padding:6px 11px; cursor:pointer; font-family: var(--font-ui); font-size:12px; font-weight:500; }
button:hover { background:#232a44; }
button.primary { background:var(--accent); border-color:var(--accent); color:#04101f; font-weight:700; }
button.danger { background:var(--red); border-color:var(--red); color:#1a0505; font-weight:700; }
select { background:var(--ground); color:var(--text); border:1px solid var(--border); border-radius:4px; padding:4px 6px; font-family: var(--font-ui); }
.controls-row { display:flex; gap:6px; flex-wrap:wrap; }
#legend { display:flex; gap:14px; font-size:11px; color:var(--text-dim); margin-top:6px; flex-wrap:wrap; }
#legend span { display:flex; align-items:center; gap:4px; }
.dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
</style>
<div id="app">
  <header>
    <h1><span>Axiom</span> Replay Lab</h1>
    <div class="stat"><span class="label">Instrument</span><span class="value">SPY · 5m</span></div>
    <div class="stat"><span class="label">Bar</span><span class="value" id="statBar">0 / 0</span></div>
    <div class="stat"><span class="label">Time</span><span class="value" id="statTime">—</span></div>
    <div class="stat"><span class="label">Equity</span><span class="value" id="statEquity">$100,000.00</span></div>
    <div class="stat"><span class="label">Realized P&amp;L</span><span class="value" id="statPnl">$0.00</span></div>
    <div class="stat"><span class="label">Open Position</span><span class="value" id="statPos">Flat</span></div>
    <div class="stat"><span class="label">Unrealized P&amp;L</span><span class="value" id="statUpnl">$0.00</span></div>
    <div class="stat"><span class="label">Drawdown</span><span class="value" id="statDD">0.00%</span></div>
  </header>
  <div id="chartWrap">
    <canvas id="chart" height="520"></canvas>
    <div id="legend">
      <span><span class="dot" style="background:var(--accent)"></span> EMA 9</span>
      <span><span class="dot" style="background:var(--amber)"></span> EMA 21</span>
      <span><span class="dot" style="background:var(--green)"></span> Buy / Cover</span>
      <span><span class="dot" style="background:var(--red)"></span> Sell / Short</span>
      <span><span class="dot" style="background:var(--violet)"></span> Scale-in</span>
      <span><span class="dot" style="background:#6b7385"></span> Stop / Target level (active trade)</span>
    </div>
  </div>
  <div id="sidebar">
    <fieldset>
      <legend>Replay</legend>
      <div class="controls-row">
        <button id="btnPlay" class="primary">▶ Play</button>
        <button id="btnPause">⏸ Pause</button>
        <button id="btnStep">Step ▸</button>
        <button id="btnReset">⟲ Reset</button>
        <button id="btnFlatten" class="danger">Flatten</button>
      </div>
      <div class="row">
        <label>Speed</label>
        <select id="speedSel">
          <option value="0.5">0.5x</option>
          <option value="1" selected>1x</option>
          <option value="2">2x</option>
          <option value="3">3x</option>
          <option value="5">5x</option>
          <option value="10">10x</option>
        </select>
      </div>
    </fieldset>
    <fieldset>
      <legend>Strategy Parameters</legend>
      <div class="row"><label>EMA fast</label><input type="number" id="cfg_emaFast" value="9"></div>
      <div class="row"><label>EMA slow</label><input type="number" id="cfg_emaSlow" value="21"></div>
      <div class="row"><label>Initial risk %</label><input type="number" step="0.01" id="cfg_initialRiskPct" value="0.35"></div>
      <div class="row"><label>Stop %</label><input type="number" step="0.01" id="cfg_stopPct" value="0.22"></div>
      <div class="row"><label>Target %</label><input type="number" step="0.01" id="cfg_targetPct" value="0.44"></div>
      <div class="row"><label>Scale #1 %</label><input type="number" step="0.01" id="cfg_scale1Pct" value="0.11"></div>
      <div class="row"><label>Scale #2 %</label><input type="number" step="0.01" id="cfg_scale2Pct" value="0.22"></div>
      <div class="row"><label>Initial position %</label><input type="number" id="cfg_initialPositionPct" value="50"></div>
      <div class="row"><label>Scale #1 position %</label><input type="number" id="cfg_scale1PositionPct" value="25"></div>
      <div class="row"><label>Scale #2 position %</label><input type="number" id="cfg_scale2PositionPct" value="25"></div>
      <div class="row"><label>Slippage %</label><input type="number" step="0.001" id="cfg_slippagePct" value="0.01"></div>
      <div class="row"><label>Commission $/fill</label><input type="number" step="0.01" id="cfg_commissionPerFill" value="0"></div>
      <div class="row"><label>Max drawdown %</label><input type="number" id="cfg_maxDrawdownPct" value="20"></div>
      <div class="row"><label>Long enabled</label><input type="checkbox" id="cfg_longEnabled" checked></div>
      <div class="row"><label>Short enabled</label><input type="checkbox" id="cfg_shortEnabled" checked></div>
      <div class="row"><label>Scaling enabled</label><input type="checkbox" id="cfg_scalingEnabled" checked></div>
      <button id="btnApply" class="primary" style="width:100%; margin-top:6px;">Apply &amp; Reset</button>
    </fieldset>
  </div>
  <div id="tradesPanel">
    <table id="tradesTable">
      <thead><tr>
        <th>ID</th><th>Side</th><th>Entry</th><th>Exit</th><th>Avg Entry</th><th>Exit Px</th>
        <th>Qty</th><th>Reason</th><th>Net P&amp;L</th><th>Equity</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>
<script>
${ENGINE_SRC}
</script>
<script>
const BARS = ${BARS_JSON};
const STARTING_EQUITY = 100000;

function readConfig() {
  return {
    emaFast: Number(document.getElementById('cfg_emaFast').value),
    emaSlow: Number(document.getElementById('cfg_emaSlow').value),
    initialRiskPct: Number(document.getElementById('cfg_initialRiskPct').value),
    stopPct: Number(document.getElementById('cfg_stopPct').value),
    targetPct: Number(document.getElementById('cfg_targetPct').value),
    scale1Pct: Number(document.getElementById('cfg_scale1Pct').value),
    scale2Pct: Number(document.getElementById('cfg_scale2Pct').value),
    initialPositionPct: Number(document.getElementById('cfg_initialPositionPct').value),
    scale1PositionPct: Number(document.getElementById('cfg_scale1PositionPct').value),
    scale2PositionPct: Number(document.getElementById('cfg_scale2PositionPct').value),
    slippagePct: Number(document.getElementById('cfg_slippagePct').value),
    commissionPerFill: Number(document.getElementById('cfg_commissionPerFill').value),
    maxDrawdownPct: Number(document.getElementById('cfg_maxDrawdownPct').value),
    longEnabled: document.getElementById('cfg_longEnabled').checked,
    shortEnabled: document.getElementById('cfg_shortEnabled').checked,
    scalingEnabled: document.getElementById('cfg_scalingEnabled').checked,
    startingEquity: STARTING_EQUITY,
  };
}

let sim, idx, playing, timer, entryMarkers, scaleMarkers, exitMarkers;

function resetSim() {
  sim = AxiomEngine.createSimulation(readConfig());
  idx = 0;
  playing = false;
  entryMarkers = []; scaleMarkers = []; exitMarkers = [];
  document.getElementById('tradesTable').querySelector('tbody').innerHTML = '';
  clearInterval(timer);
  render();
}

function fmt$(x) { return (x < 0 ? '-$' : '$') + Math.abs(x).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}); }
function fmtPct(x) { return x.toFixed(2) + '%'; }

function addTradeRow(t) {
  const tb = document.getElementById('tradesTable').querySelector('tbody');
  const tr = document.createElement('tr');
  const pnlClass = t.netPnl >= 0 ? 'up' : 'down';
  tr.innerHTML = '<td>'+t.tradeId+'</td><td>'+t.side+'</td><td>'+t.entryTime+'</td><td>'+t.exitTime+'</td>' +
    '<td>'+t.avgEntryPrice.toFixed(2)+'</td><td>'+t.exitPrice.toFixed(2)+'</td><td>'+t.finalQty+'</td>' +
    '<td>'+t.exitReason+'</td><td class="'+pnlClass+'">'+fmt$(t.netPnl)+'</td><td>'+fmt$(t.equityAfter)+'</td>';
  tb.prepend(tr);
}

function stepOnce() {
  if (idx >= BARS.length) { playing = false; clearInterval(timer); return; }
  const b = BARS[idx];
  const bar = { t: b.t, time: b.time, open: b.o, high: b.h, low: b.l, close: b.c, volume: b.v };
  const beforeTrades = sim.trades.length;
  const res = sim.step(bar);
  if (sim.trades.length > beforeTrades) {
    const t = sim.trades[sim.trades.length - 1];
    addTradeRow(t);
    exitMarkers.push({ idx, price: t.exitPrice, side: t.side, reason: t.exitReason });
  }
  // detect entry/scale events emitted this bar
  for (let i = sim.events.length - 1; i >= 0 && sim.events[i].index === idx; i--) {
    const ev = sim.events[i];
    if (ev.type === 'entry') entryMarkers.push({ idx, price: ev.price, side: ev.side });
    if (ev.type === 'scale1' || ev.type === 'scale2') scaleMarkers.push({ idx, price: ev.price });
  }
  idx++;
  render();
}

function flattenNow() {
  if (idx === 0) return;
  const b = BARS[idx - 1];
  const bar = { t: b.t, time: b.time, open: b.o, high: b.h, low: b.l, close: b.c, volume: b.v };
  const t = sim.flatten(bar, 'manual_flatten');
  if (t) { addTradeRow(t); exitMarkers.push({ idx: idx - 1, price: t.exitPrice, side: t.side, reason: 'manual_flatten' }); render(); }
}

function render() {
  const state = sim.getState();
  document.getElementById('statBar').textContent = idx + ' / ' + BARS.length;
  document.getElementById('statTime').textContent = idx > 0 ? BARS[idx - 1].time : '—';
  document.getElementById('statEquity').textContent = fmt$(state.equity);
  const realized = state.equity - STARTING_EQUITY;
  const pnlEl = document.getElementById('statPnl');
  pnlEl.textContent = fmt$(realized); pnlEl.className = 'value ' + (realized >= 0 ? 'up' : 'down');
  document.getElementById('statDD').textContent = fmtPct(state.maxDrawdownSeen);

  const posEl = document.getElementById('statPos');
  const upnlEl = document.getElementById('statUpnl');
  if (state.position) {
    const p = state.position;
    const lastClose = idx > 0 ? BARS[idx - 1].c : p.currentAvg;
    const unrealized = p.side === 'long' ? (lastClose - p.currentAvg) * p.filledShares : (p.currentAvg - lastClose) * p.filledShares;
    posEl.textContent = p.side.toUpperCase() + ' ' + p.filledShares + ' @ ' + p.currentAvg.toFixed(2);
    posEl.className = 'value ' + (p.side === 'long' ? 'up' : 'down');
    upnlEl.textContent = fmt$(unrealized);
    upnlEl.className = 'value ' + (unrealized >= 0 ? 'up' : 'down');
  } else {
    posEl.textContent = 'Flat'; posEl.className = 'value';
    upnlEl.textContent = '$0.00'; upnlEl.className = 'value';
  }
  drawChart(state);
}

function drawChart(state) {
  const canvas = document.getElementById('chart');
  const wrap = document.getElementById('chartWrap');
  const dpr = window.devicePixelRatio || 1;
  const cssW = wrap.clientWidth - 16, cssH = 520;
  canvas.width = cssW * dpr; canvas.height = cssH * dpr;
  canvas.style.width = cssW + 'px'; canvas.style.height = cssH + 'px';
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#12161f'; ctx.fillRect(0, 0, cssW, cssH);

  const WINDOW = 180; // visible bars
  const start = Math.max(0, idx - WINDOW);
  const end = Math.max(start + 1, idx);
  const visible = BARS.slice(start, end);
  if (visible.length < 2) return;

  let lo = Infinity, hi = -Infinity;
  for (const b of visible) { lo = Math.min(lo, b.l); hi = Math.max(hi, b.h); }
  if (state.position) { lo = Math.min(lo, state.position.stopPrice); hi = Math.max(hi, state.position.targetPrice); }
  const pad = (hi - lo) * 0.08 || 1;
  lo -= pad; hi += pad;

  const padL = 8, padR = 8, padT = 8, padB = 8;
  const plotW = cssW - padL - padR, plotH = cssH - padT - padB;
  const xAt = i => padL + (i / (WINDOW - 1)) * plotW;
  const yAt = p => padT + (1 - (p - lo) / (hi - lo)) * plotH;

  // candles
  const bw = Math.max(1, plotW / WINDOW * 0.6);
  visible.forEach((b, i) => {
    const x = xAt(i);
    const up = b.c >= b.o;
    ctx.strokeStyle = ctx.fillStyle = up ? '#29b6a3' : '#f2555a';
    ctx.beginPath(); ctx.moveTo(x, yAt(b.h)); ctx.lineTo(x, yAt(b.l)); ctx.stroke();
    const yO = yAt(b.o), yC = yAt(b.c);
    ctx.fillRect(x - bw / 2, Math.min(yO, yC), bw, Math.max(1, Math.abs(yC - yO)));
  });

  // EMAs: recompute over full history closes up to idx (cheap enough at this scale)
  const closesAll = BARS.slice(0, end).map(b => b.c);
  const cfg = sim.config;
  const emaF = AxiomEngine.computeEMA(closesAll, cfg.emaFast);
  const emaS = AxiomEngine.computeEMA(closesAll, cfg.emaSlow);
  function drawLine(arr, color) {
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.beginPath();
    let started = false;
    for (let i = 0; i < visible.length; i++) {
      const v = arr[start + i];
      if (v == null) continue;
      const x = xAt(i), y = yAt(v);
      if (!started) { ctx.moveTo(x, y); started = true; } else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  drawLine(emaF, '#3e8fff');
  drawLine(emaS, '#f0ad3f');

  // active stop/target lines
  if (state.position) {
    ctx.setLineDash([4, 4]); ctx.strokeStyle = '#6b7385';
    ctx.beginPath(); ctx.moveTo(padL, yAt(state.position.stopPrice)); ctx.lineTo(cssW - padR, yAt(state.position.stopPrice)); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(padL, yAt(state.position.targetPrice)); ctx.lineTo(cssW - padR, yAt(state.position.targetPrice)); ctx.stroke();
    ctx.setLineDash([]);
  }

  function marker(i, price, color, symbol) {
    if (i < start || i >= end) return;
    const x = xAt(i - start), y = yAt(price);
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
  }
  entryMarkers.forEach(m => marker(m.idx, m.price, m.side === 'long' ? '#29b6a3' : '#f2555a'));
  scaleMarkers.forEach(m => marker(m.idx, m.price, '#a980ff'));
  exitMarkers.forEach(m => marker(m.idx, m.price, '#e8ebf2'));
}

document.getElementById('btnPlay').onclick = () => {
  if (playing) return;
  playing = true;
  const tick = () => {
    if (!playing) return;
    const speed = Number(document.getElementById('speedSel').value);
    const stepsPerTick = Math.max(1, Math.round(speed));
    for (let i = 0; i < stepsPerTick; i++) stepOnce();
    if (idx < BARS.length && playing) timer = setTimeout(tick, 120 / speed);
  };
  tick();
};
document.getElementById('btnPause').onclick = () => { playing = false; clearInterval(timer); };
document.getElementById('btnStep').onclick = () => { playing = false; clearInterval(timer); stepOnce(); };
document.getElementById('btnReset').onclick = () => resetSim();
document.getElementById('btnFlatten').onclick = () => flattenNow();
document.getElementById('btnApply').onclick = () => resetSim();
window.addEventListener('resize', () => render());

resetSim();
</script>
`;

const OUT = path.join(__dirname, '..', 'ui', 'index.html');
fs.writeFileSync(OUT, html);
console.log('Wrote ' + OUT + ' (' + (html.length / 1024).toFixed(0) + ' KB)');
