const fs = require('fs');
const path = require('path');
const { loadDailyBars, loadDividends } = require('../src/data-loader.js');

const ENGINE_SRC = fs.readFileSync(path.join(__dirname, '..', 'src', 'buffett-engine.js'), 'utf8');
const bars = loadDailyBars(path.join(__dirname, '..', 'data', 'spy_1d.csv'));
const BARS_JSON = JSON.stringify(bars.map(b => ({ t: b.t, time: b.time, o: b.open, h: b.high, l: b.low, c: b.close, v: b.volume })));
const dividends = loadDividends(path.join(__dirname, '..', 'data', 'spy_dividends.csv'));
const DIVIDENDS_JSON = JSON.stringify(dividends);

const html = `<!doctype html>
<title>Axiom Value Lab</title>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,500;0,600;1,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
  --ground: #0a0d12; --surface: #12161f; --surface-raised: #171c28; --border: #232a3a;
  --text: #e8ebf2; --text-dim: #8a93a8; --accent: #3e8fff;
  --green: #29b6a3; --red: #f2555a; --amber: #f0ad3f; --violet: #a980ff;
  --font-ui: 'IBM Plex Sans', -apple-system, Segoe UI, Roboto, sans-serif;
  --font-serif: 'IBM Plex Serif', Georgia, serif;
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
#chartWrap { background:var(--surface); position:relative; padding:10px; overflow:hidden; display:flex; flex-direction:column; }
canvas { display:block; width:100%; }
#quote { font-family: var(--font-serif); font-style:italic; color:var(--text-dim); font-size:12.5px; padding:8px 4px 2px; border-top:1px solid var(--border); margin-top:8px; min-height:34px; line-height:1.5; }
#quote b { color:var(--text); font-style:normal; font-weight:600; }
#sidebar { background:var(--surface); overflow-y:auto; padding:14px; display:flex; flex-direction:column; gap:16px; }
#buysPanel { grid-column: 1 / 3; background:var(--surface); max-height:220px; overflow:auto; padding:10px 14px; }
table { width:100%; border-collapse:collapse; font-size:11px; }
th, td { padding:4px 7px; text-align:right; border-bottom:1px solid var(--border); white-space:nowrap; }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align:left; }
th { color:var(--text-dim); font-weight:500; font-family: var(--font-ui); font-size:10px; text-transform:uppercase; letter-spacing:.06em; position:sticky; top:0; background:var(--surface); }
td.commentary { text-align:left; max-width:360px; white-space:normal; color:var(--text-dim); font-style:italic; }
fieldset { border:1px solid var(--border); border-radius:6px; padding:10px 12px; }
legend { color:var(--text-dim); font-size:10.5px; padding:0 5px; text-transform:uppercase; letter-spacing:.08em; font-weight:600; }
.row { display:flex; align-items:center; justify-content:space-between; gap:8px; margin:6px 0; }
.row label { color:var(--text-dim); }
input[type=number] { width:64px; background:var(--ground); border:1px solid var(--border); color:var(--text); border-radius:4px; padding:4px 6px; font-size:12px; }
input[type=number]:focus, select:focus, button:focus-visible { outline:2px solid var(--accent); outline-offset:1px; }
button { background:var(--surface-raised); color:var(--text); border:1px solid var(--border); border-radius:5px; padding:6px 11px; cursor:pointer; font-family: var(--font-ui); font-size:12px; font-weight:500; }
button:hover { background:#232a44; }
button.primary { background:var(--accent); border-color:var(--accent); color:#04101f; font-weight:700; }
select { background:var(--ground); color:var(--text); border:1px solid var(--border); border-radius:4px; padding:4px 6px; font-family: var(--font-ui); }
.controls-row { display:flex; gap:6px; flex-wrap:wrap; }
#legend { display:flex; gap:14px; font-size:11px; color:var(--text-dim); margin-top:6px; flex-wrap:wrap; }
#legend span { display:flex; align-items:center; gap:4px; }
.dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
.baseline-note { font-size:11px; color:var(--text-dim); line-height:1.5; }
.baseline-note b { color:var(--text); }
</style>
<div id="app">
  <header>
    <h1><span>Axiom</span> Value Lab</h1>
    <div class="stat"><span class="label">Instrument</span><span class="value">SPY · Daily</span></div>
    <div class="stat"><span class="label">Date</span><span class="value" id="statDate">—</span></div>
    <div class="stat"><span class="label">Equity</span><span class="value" id="statEquity">$100,000.00</span></div>
    <div class="stat"><span class="label">Return</span><span class="value" id="statReturn">0.00%</span></div>
    <div class="stat"><span class="label">Shares Held</span><span class="value" id="statShares">0</span></div>
    <div class="stat"><span class="label">Avg Cost</span><span class="value" id="statAvgCost">$0.00</span></div>
    <div class="stat"><span class="label">Cash Reserve</span><span class="value" id="statCash">$100,000.00</span></div>
    <div class="stat"><span class="label">Dividends Collected</span><span class="value" id="statDiv">$0.00</span></div>
    <div class="stat"><span class="label">Drawdown</span><span class="value" id="statDD">0.00%</span></div>
  </header>
  <div id="chartWrap">
    <canvas id="chart" height="440"></canvas>
    <div id="legend">
      <span><span class="dot" style="background:var(--text-dim)"></span> Close</span>
      <span><span class="dot" style="background:var(--amber)"></span> Trailing all-time high</span>
      <span><span class="dot" style="background:var(--green)"></span> Buy</span>
    </div>
    <div id="quote">Press Play. The initial stake goes in on day one — the rest waits.</div>
  </div>
  <div id="sidebar">
    <fieldset>
      <legend>Replay</legend>
      <div class="controls-row">
        <button id="btnPlay" class="primary">▶ Play</button>
        <button id="btnPause">⏸ Pause</button>
        <button id="btnStep">Step ▸</button>
        <button id="btnReset">⟲ Reset</button>
      </div>
      <div class="row">
        <label>Speed</label>
        <select id="speedSel">
          <option value="1">1x</option>
          <option value="5">5x</option>
          <option value="20" selected>20x</option>
          <option value="60">60x</option>
          <option value="120">120x</option>
        </select>
      </div>
    </fieldset>
    <fieldset>
      <legend>Posture</legend>
      <div class="row"><label>Initial deploy %</label><input type="number" id="cfg_initialDeployPct" value="50"></div>
      <div class="row"><label>Dip band width %</label><input type="number" id="cfg_dipBandPct" value="10"></div>
      <div class="row"><label>Add per band %</label><input type="number" id="cfg_dipAddPct" value="10"></div>
      <div class="row"><label>Slippage %</label><input type="number" step="0.001" id="cfg_slippagePct" value="0.01"></div>
      <div class="row"><label>Commission $/fill</label><input type="number" step="0.01" id="cfg_commissionPerFill" value="0"></div>
      <div class="row"><label>Collect real dividends</label><input type="checkbox" id="cfg_collectDividends" checked></div>
      <button id="btnApply" class="primary" style="width:100%; margin-top:6px;">Apply &amp; Reset</button>
    </fieldset>
    <fieldset>
      <legend>vs. lump-sum baseline</legend>
      <div class="baseline-note">100% deployed day one, no reserve, never adds.<br>
        Baseline return: <b id="baseReturn">—</b><br>
        This posture: <b id="thisReturn">—</b><br>
        Edge: <b id="edgeReturn">—</b>
      </div>
    </fieldset>
  </div>
  <div id="buysPanel">
    <table id="buysTable">
      <thead><tr><th>ID</th><th>Kind</th><th>Date</th><th>Price</th><th>Shares</th><th>Cost</th><th>Drawdown</th><th>Cash Left</th><th>Commentary</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>
<script>
${ENGINE_SRC}
</script>
<script>
const BARS = ${BARS_JSON};
const DIVIDENDS = ${DIVIDENDS_JSON};
const STARTING_EQUITY = 100000;

function readConfig() {
  return {
    startingEquity: STARTING_EQUITY,
    initialDeployPct: Number(document.getElementById('cfg_initialDeployPct').value),
    dipBandPct: Number(document.getElementById('cfg_dipBandPct').value),
    dipAddPct: Number(document.getElementById('cfg_dipAddPct').value),
    slippagePct: Number(document.getElementById('cfg_slippagePct').value),
    commissionPerFill: Number(document.getElementById('cfg_commissionPerFill').value),
    collectDividends: document.getElementById('cfg_collectDividends').checked,
    dividends: DIVIDENDS,
  };
}

let sim, idx, playing, timer, buyMarkers, baseline;

function computeBaseline(cfg) {
  return BuffettEngine.runLumpSumBaseline(BARS.map(b => ({ time: b.time, open: b.o, close: b.c })), cfg.startingEquity, cfg.slippagePct, cfg.commissionPerFill, cfg.collectDividends ? cfg.dividends : null);
}

function resetSim() {
  const cfg = readConfig();
  sim = BuffettEngine.createSimulation(cfg);
  baseline = computeBaseline(cfg);
  idx = 0; playing = false; buyMarkers = [];
  document.getElementById('buysTable').querySelector('tbody').innerHTML = '';
  document.getElementById('quote').textContent = 'Press Play. The initial stake goes in on day one — the rest waits.';
  clearInterval(timer);
  const baseReturnPct = ((baseline.finalEquity - cfg.startingEquity) / cfg.startingEquity) * 100;
  document.getElementById('baseReturn').textContent = fmtPct(baseReturnPct);
  document.getElementById('thisReturn').textContent = '—';
  document.getElementById('edgeReturn').textContent = '—';
  render();
}

function fmt$(x) { return (x < 0 ? '-$' : '$') + Math.abs(x).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}); }
function fmtPct(x) { return (x >= 0 ? '+' : '') + x.toFixed(2) + '%'; }

function addBuyRow(b) {
  const tb = document.getElementById('buysTable').querySelector('tbody');
  const tr = document.createElement('tr');
  const dd = b.drawdownPctAtTrigger != null ? b.drawdownPctAtTrigger.toFixed(1) + '%' : '—';
  tr.innerHTML = '<td>'+b.buyId+'</td><td>'+b.kind+(b.band?(' (-'+(b.band*10)+'%)'):'')+'</td><td>'+b.date+'</td>' +
    '<td>'+fmt$(b.price)+'</td><td>'+b.shares+'</td><td>'+fmt$(b.cost)+'</td><td>'+dd+'</td><td>'+fmt$(b.cashRemainingAfter)+'</td>' +
    '<td class="commentary">'+b.commentary+'</td>';
  tb.prepend(tr);
}

function stepOnce() {
  if (idx >= BARS.length) { playing = false; clearInterval(timer); return; }
  const b = BARS[idx];
  const bar = { t: b.t, time: b.time, open: b.o, high: b.h, low: b.l, close: b.c, volume: b.v };
  const beforeBuys = sim.buys.length;
  sim.step(bar);
  if (sim.buys.length > beforeBuys) {
    const buy = sim.buys[sim.buys.length - 1];
    addBuyRow(buy);
    buyMarkers.push({ idx, price: buy.price, kind: buy.kind });
    document.getElementById('quote').innerHTML = '<b>' + buy.date + ':</b> ' + buy.commentary;
  }
  for (let i = sim.events.length - 1; i >= 0 && sim.events[i].index === idx; i--) {
    if (sim.events[i].type === 'new_ath') document.getElementById('quote').innerHTML = '<b>' + sim.events[i].date + ':</b> ' + sim.events[i].commentary;
  }
  idx++;
  render();
}

function render() {
  const state = sim.getState();
  document.getElementById('statDate').textContent = idx > 0 ? BARS[idx - 1].time : '—';
  document.getElementById('statEquity').textContent = fmt$(state.equity);
  const returnPct = ((state.equity - STARTING_EQUITY) / STARTING_EQUITY) * 100;
  const retEl = document.getElementById('statReturn');
  retEl.textContent = fmtPct(returnPct); retEl.className = 'value ' + (returnPct >= 0 ? 'up' : 'down');
  document.getElementById('statShares').textContent = state.shares;
  document.getElementById('statAvgCost').textContent = fmt$(state.avgCost);
  document.getElementById('statCash').textContent = fmt$(state.cash);
  document.getElementById('statDiv').textContent = fmt$(state.totalDividendsCollected || 0);
  document.getElementById('statDD').textContent = state.maxDrawdownPct.toFixed(2) + '%';

  if (idx > 0) {
    const baseEqAt = baseline.equityCurve[idx - 1].equity;
    const baseRetAt = ((baseEqAt - STARTING_EQUITY) / STARTING_EQUITY) * 100;
    document.getElementById('thisReturn').textContent = fmtPct(returnPct);
    document.getElementById('edgeReturn').textContent = fmtPct(returnPct - baseRetAt);
  }
  drawChart(state);
}

function drawChart(state) {
  const canvas = document.getElementById('chart');
  const wrap = document.getElementById('chartWrap');
  const dpr = window.devicePixelRatio || 1;
  const cssW = wrap.clientWidth - 16, cssH = 440;
  canvas.width = cssW * dpr; canvas.height = cssH * dpr;
  canvas.style.width = cssW + 'px'; canvas.style.height = cssH + 'px';
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#12161f'; ctx.fillRect(0, 0, cssW, cssH);
  if (idx < 2) return;

  const visible = BARS.slice(0, idx);
  let lo = Infinity, hi = -Infinity;
  for (const b of visible) { lo = Math.min(lo, b.c); hi = Math.max(hi, b.c); }
  const pad = (hi - lo) * 0.06 || 1;
  lo -= pad; hi += pad;
  const padL = 8, padR = 8, padT = 8, padB = 8;
  const plotW = cssW - padL - padR, plotH = cssH - padT - padB;
  const xAt = i => padL + (i / (BARS.length - 1)) * plotW;
  const yAt = p => padT + (1 - (p - lo) / (hi - lo)) * plotH;

  ctx.strokeStyle = '#8a93a8'; ctx.lineWidth = 1.5; ctx.beginPath();
  visible.forEach((b, i) => { const x = xAt(i), y = yAt(b.c); i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); });
  ctx.stroke();

  let ath = -Infinity;
  ctx.strokeStyle = '#f0ad3f'; ctx.lineWidth = 1; ctx.beginPath();
  visible.forEach((b, i) => { ath = Math.max(ath, b.c); const x = xAt(i), y = yAt(ath); i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); });
  ctx.stroke();

  buyMarkers.forEach(m => {
    const x = xAt(m.idx), y = yAt(m.price);
    ctx.fillStyle = '#29b6a3';
    ctx.beginPath(); ctx.arc(x, y, m.kind === 'initial' ? 5 : 4, 0, Math.PI * 2); ctx.fill();
  });
}

document.getElementById('btnPlay').onclick = () => {
  if (playing) return;
  playing = true;
  const tick = () => {
    if (!playing) return;
    const speed = Number(document.getElementById('speedSel').value);
    for (let i = 0; i < speed; i++) stepOnce();
    if (idx < BARS.length && playing) timer = setTimeout(tick, 60);
  };
  tick();
};
document.getElementById('btnPause').onclick = () => { playing = false; clearInterval(timer); };
document.getElementById('btnStep').onclick = () => { playing = false; clearInterval(timer); stepOnce(); };
document.getElementById('btnReset').onclick = () => resetSim();
document.getElementById('btnApply').onclick = () => resetSim();
window.addEventListener('resize', () => render());

resetSim();
</script>
`;

const OUT = path.join(__dirname, '..', 'ui', 'buffett.html');
fs.writeFileSync(OUT, html);
console.log('Wrote ' + OUT + ' (' + (html.length / 1024).toFixed(0) + ' KB)');
