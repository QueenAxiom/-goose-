const fs = require('fs');
const path = require('path');
const { loadBars, loadDailyBars, loadDividends } = require('../src/data-loader.js');

const SCALP_ENGINE_SRC = fs.readFileSync(path.join(__dirname, '..', 'src', 'engine.js'), 'utf8');
const VALUE_ENGINE_SRC = fs.readFileSync(path.join(__dirname, '..', 'src', 'buffett-engine.js'), 'utf8');

const scalpBars = loadBars(path.join(__dirname, '..', 'data', 'spy_5m.csv'));
const SCALP_BARS_JSON = JSON.stringify(scalpBars.map(b => ({ t: b.t, time: b.time, o: b.open, h: b.high, l: b.low, c: b.close, v: b.volume })));

const valueBars = loadDailyBars(path.join(__dirname, '..', 'data', 'spy_1d.csv'));
const VALUE_BARS_JSON = JSON.stringify(valueBars.map(b => ({ t: b.t, time: b.time, o: b.open, h: b.high, l: b.low, c: b.close, v: b.volume })));

const dividends = loadDividends(path.join(__dirname, '..', 'data', 'spy_dividends.csv'));
const DIVIDENDS_JSON = JSON.stringify(dividends);

const html = `<!doctype html>
<title>Axiom Backtest Studio</title>
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
.num, .value, table, input[type=number], textarea { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
#topbar { background:var(--surface); border-bottom:1px solid var(--border); padding:10px 18px; display:flex; align-items:center; gap:18px; flex-wrap:wrap; }
#topbar h1 { font-family: var(--font-ui); font-size:15px; margin:0; font-weight:700; letter-spacing:.02em; white-space:nowrap; }
#topbar h1 span { color:var(--accent); }
#tabs { display:flex; gap:4px; background:var(--ground); border:1px solid var(--border); border-radius:7px; padding:3px; }
#tabs button { background:transparent; border:none; color:var(--text-dim); padding:6px 14px; border-radius:5px; cursor:pointer; font-family: var(--font-ui); font-size:12.5px; font-weight:600; }
#tabs button.active { background:var(--accent); color:#04101f; }
#topbar .spacer { flex:1; }
#topbar .filenote { color:var(--text-dim); font-size:11px; }
input[type=file] { display:none; }
label.fileBtn { background:var(--surface-raised); color:var(--text); border:1px solid var(--border); border-radius:5px; padding:6px 11px; cursor:pointer; font-family: var(--font-ui); font-size:12px; font-weight:500; }
label.fileBtn:hover { background:#232a44; }
.mode { display:none; }
.mode.active { display:grid; }
.mode { grid-template-columns: 1fr 320px; grid-template-rows: auto auto 1fr; height:calc(100vh - 49px); gap:1px; background:var(--border); }
header.strip { grid-column: 1 / 3; background:var(--surface); padding:12px 18px; display:flex; align-items:center; gap:22px; flex-wrap:wrap; }
header.strip .stat { display:flex; flex-direction:column; gap:3px; }
header.strip .stat .label { color:var(--text-dim); font-size:9.5px; text-transform:uppercase; letter-spacing:.08em; font-weight:500; }
header.strip .stat .value { font-weight:600; font-size:14px; letter-spacing:.01em; }
.up { color:var(--green); } .down { color:var(--red); }
.chartWrap { background:var(--surface); position:relative; padding:10px; overflow:hidden; display:flex; flex-direction:column; }
canvas { display:block; width:100%; }
#valQuote { font-family: 'IBM Plex Serif', Georgia, serif; font-style:italic; color:var(--text-dim); font-size:12.5px; padding:8px 4px 2px; border-top:1px solid var(--border); margin-top:8px; min-height:34px; line-height:1.5; }
#valQuote b { color:var(--text); font-style:normal; font-weight:600; }
.sidebar { background:var(--surface); overflow-y:auto; padding:14px; display:flex; flex-direction:column; gap:16px; }
.tapePanel { grid-column: 1 / 3; background:var(--surface); max-height:200px; overflow:auto; padding:10px 14px; }
table { width:100%; border-collapse:collapse; font-size:11px; }
th, td { padding:4px 7px; text-align:right; border-bottom:1px solid var(--border); white-space:nowrap; }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align:left; }
th { color:var(--text-dim); font-weight:500; font-family: var(--font-ui); font-size:10px; text-transform:uppercase; letter-spacing:.06em; position:sticky; top:0; background:var(--surface); }
td.commentary { text-align:left; max-width:340px; white-space:normal; color:var(--text-dim); font-style:italic; }
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
#scalpLegend, #valLegend { display:flex; gap:14px; font-size:11px; color:var(--text-dim); margin-top:6px; flex-wrap:wrap; }
#scalpLegend span, #valLegend span { display:flex; align-items:center; gap:4px; }
.dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
.exportBox { width:100%; height:70px; background:var(--ground); border:1px solid var(--border); color:var(--text-dim); font-size:10px; border-radius:5px; padding:6px; resize:vertical; }
.exportNote { font-size:10.5px; color:var(--text-dim); margin:4px 0 0; }
.disclaimer { font-size:10.5px; color:var(--text-dim); line-height:1.5; }
</style>
<div id="topbar">
  <h1><span>Axiom</span> Backtest Studio</h1>
  <div id="tabs">
    <button id="tabScalp" class="active">Momentum Scalp</button>
    <button id="tabValue">Value Ladder</button>
  </div>
  <div class="spacer"></div>
  <label class="fileBtn">Load your own CSV<input type="file" id="csvInput" accept=".csv"></label>
  <span class="filenote" id="fileStatus">Using bundled SPY sample data</span>
</div>

<div id="app" class="mode active" data-mode="scalp">
  <header class="strip">
    <div class="stat"><span class="label">Instrument</span><span class="value" id="scalpInstrument">SPY · 5m</span></div>
    <div class="stat"><span class="label">Bar</span><span class="value" id="statBar">0 / 0</span></div>
    <div class="stat"><span class="label">Time</span><span class="value" id="statTime">—</span></div>
    <div class="stat"><span class="label">Equity</span><span class="value" id="statEquity">$100,000.00</span></div>
    <div class="stat"><span class="label">Realized P&amp;L</span><span class="value" id="statPnl">$0.00</span></div>
    <div class="stat"><span class="label">Open Position</span><span class="value" id="statPos">Flat</span></div>
    <div class="stat"><span class="label">Unrealized P&amp;L</span><span class="value" id="statUpnl">$0.00</span></div>
    <div class="stat"><span class="label">Drawdown</span><span class="value" id="statDD">0.00%</span></div>
  </header>
  <div class="chartWrap">
    <canvas id="chart" height="440"></canvas>
    <div id="scalpLegend">
      <span><span class="dot" style="background:var(--accent)"></span> EMA 9</span>
      <span><span class="dot" style="background:var(--amber)"></span> EMA 21</span>
      <span><span class="dot" style="background:var(--green)"></span> Buy / Cover</span>
      <span><span class="dot" style="background:var(--red)"></span> Sell / Short</span>
      <span><span class="dot" style="background:var(--violet)"></span> Scale-in</span>
      <span><span class="dot" style="background:#6b7385"></span> Stop / Target level (active trade)</span>
    </div>
  </div>
  <div class="sidebar">
    <fieldset>
      <legend>Replay</legend>
      <div class="controls-row">
        <button id="btnPlay" class="primary">▶ Play</button>
        <button id="btnPause">⏸ Pause</button>
        <button id="btnStep">Step ▸</button>
        <button id="btnReset">⟲ Reset</button>
        <button id="btnFlatten" class="danger">Flatten</button>
      </div>
      <div class="row"><label>Speed</label>
        <select id="speedSel">
          <option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="2">2x</option>
          <option value="3">3x</option><option value="5">5x</option><option value="10">10x</option>
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
    <fieldset>
      <legend>Export</legend>
      <textarea class="exportBox" id="scalpExport" readonly placeholder="Trade log CSV appears here as trades close - select all &amp; copy."></textarea>
      <p class="exportNote">Click inside, Ctrl/Cmd+A, Ctrl/Cmd+C.</p>
    </fieldset>
  </div>
  <div class="tapePanel">
    <table id="tradesTable">
      <thead><tr><th>ID</th><th>Side</th><th>Entry</th><th>Exit</th><th>Avg Entry</th><th>Exit Px</th><th>Qty</th><th>Reason</th><th>Net P&amp;L</th><th>Equity</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div id="valApp" class="mode" data-mode="value">
  <header class="strip">
    <div class="stat"><span class="label">Instrument</span><span class="value" id="valInstrument">SPY · Daily</span></div>
    <div class="stat"><span class="label">Date</span><span class="value" id="valStatDate">—</span></div>
    <div class="stat"><span class="label">Equity</span><span class="value" id="valStatEquity">$100,000.00</span></div>
    <div class="stat"><span class="label">Return</span><span class="value" id="valStatReturn">0.00%</span></div>
    <div class="stat"><span class="label">Shares Held</span><span class="value" id="valStatShares">0</span></div>
    <div class="stat"><span class="label">Avg Cost</span><span class="value" id="valStatAvgCost">$0.00</span></div>
    <div class="stat"><span class="label">Cash Reserve</span><span class="value" id="valStatCash">$100,000.00</span></div>
    <div class="stat"><span class="label">Dividends</span><span class="value" id="valStatDiv">$0.00</span></div>
    <div class="stat"><span class="label">Drawdown</span><span class="value" id="valStatDD">0.00%</span></div>
  </header>
  <div class="chartWrap">
    <canvas id="valChart" height="440"></canvas>
    <div id="valLegend">
      <span><span class="dot" style="background:var(--text-dim)"></span> Close</span>
      <span><span class="dot" style="background:var(--amber)"></span> Trailing all-time high</span>
      <span><span class="dot" style="background:var(--green)"></span> Buy</span>
    </div>
    <div id="valQuote">Press Play. The initial stake goes in on day one — the rest waits.</div>
  </div>
  <div class="sidebar">
    <fieldset>
      <legend>Replay</legend>
      <div class="controls-row">
        <button id="valBtnPlay" class="primary">▶ Play</button>
        <button id="valBtnPause">⏸ Pause</button>
        <button id="valBtnStep">Step ▸</button>
        <button id="valBtnReset">⟲ Reset</button>
      </div>
      <div class="row"><label>Speed</label>
        <select id="valSpeedSel">
          <option value="1">1x</option><option value="5">5x</option><option value="20" selected>20x</option>
          <option value="60">60x</option><option value="120">120x</option>
        </select>
      </div>
    </fieldset>
    <fieldset>
      <legend>Posture</legend>
      <div class="row"><label>Initial deploy %</label><input type="number" id="vcfg_initialDeployPct" value="50"></div>
      <div class="row"><label>Dip band width %</label><input type="number" id="vcfg_dipBandPct" value="10"></div>
      <div class="row"><label>Add per band %</label><input type="number" id="vcfg_dipAddPct" value="10"></div>
      <div class="row"><label>Slippage %</label><input type="number" step="0.001" id="vcfg_slippagePct" value="0.01"></div>
      <div class="row"><label>Commission $/fill</label><input type="number" step="0.01" id="vcfg_commissionPerFill" value="0"></div>
      <div class="row"><label>Collect real dividends</label><input type="checkbox" id="vcfg_collectDividends" checked></div>
      <button id="valBtnApply" class="primary" style="width:100%; margin-top:6px;">Apply &amp; Reset</button>
    </fieldset>
    <fieldset>
      <legend>vs. lump-sum baseline</legend>
      <div class="disclaimer">Same posture, no reserve, never adds (collects the same dividends when enabled, for a fair comparison).<br>
        Baseline return: <b id="valBaseReturn">—</b><br>
        This posture: <b id="valThisReturn">—</b><br>
        Edge: <b id="valEdgeReturn">—</b>
      </div>
    </fieldset>
    <fieldset>
      <legend>Export</legend>
      <textarea class="exportBox" id="valExport" readonly placeholder="Buy log CSV appears here as buys fire - select all &amp; copy."></textarea>
      <p class="exportNote">Click inside, Ctrl/Cmd+A, Ctrl/Cmd+C.</p>
    </fieldset>
  </div>
  <div class="tapePanel">
    <table id="buysTable">
      <thead><tr><th>ID</th><th>Kind</th><th>Date</th><th>Price</th><th>Shares</th><th>Cost</th><th>Drawdown</th><th>Cash Left</th><th>Commentary</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>
<div style="padding:10px 18px; background:var(--surface); border-top:1px solid var(--border);" class="disclaimer">
  Simulation and historical-data research tool only. Not investment advice, not a recommendation to buy or sell any security, and not a signal service. Past backtested performance does not predict future results. See the bundled README/LICENSE for full terms.
</div>

<script>
${SCALP_ENGINE_SRC}
</script>
<script>
${VALUE_ENGINE_SRC}
</script>
<script>
// ---------- shared: tabs + CSV upload ----------
const tabScalp = document.getElementById('tabScalp'), tabValue = document.getElementById('tabValue');
const appScalp = document.getElementById('app'), appValue = document.getElementById('valApp');
function showMode(mode) {
  if (mode === 'scalp') {
    tabScalp.classList.add('active'); tabValue.classList.remove('active');
    appScalp.classList.add('active'); appValue.classList.remove('active');
    scalpPlaying = false; clearInterval(scalpTimer);
    setTimeout(scalpRender, 0);
  } else {
    tabValue.classList.add('active'); tabScalp.classList.remove('active');
    appValue.classList.add('active'); appScalp.classList.remove('active');
    valPlaying = false; clearInterval(valTimer);
    setTimeout(valRender, 0);
  }
}
tabScalp.onclick = () => showMode('scalp');
tabValue.onclick = () => showMode('value');

function parseCsv(text) {
  const lines = text.trim().split(/\\r?\\n/).filter(l => l.trim());
  const header = lines[0].split(',').map(h => h.trim().toLowerCase());
  const find = (...names) => { for (const n of names) { const i = header.indexOf(n); if (i >= 0) return i; } return -1; };
  const iDate = find('date', 'time'), iOpen = find('open'), iHigh = find('high'), iLow = find('low'), iClose = find('close'), iVol = find('volume');
  if (iDate < 0 || iOpen < 0 || iHigh < 0 || iLow < 0 || iClose < 0) throw new Error('CSV needs date/time, open, high, low, close columns');
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(',');
    rows.push({ t: i, time: cols[iDate], o: Number(cols[iOpen]), h: Number(cols[iHigh]), l: Number(cols[iLow]), c: Number(cols[iClose]), v: iVol >= 0 ? Number(cols[iVol]) : 0 });
  }
  return rows;
}

document.getElementById('csvInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const rows = parseCsv(reader.result);
      const activeMode = appScalp.classList.contains('active') ? 'scalp' : 'value';
      if (activeMode === 'scalp') {
        SCALP_BARS = rows;
        document.getElementById('scalpInstrument').textContent = file.name;
        scalpResetSim();
      } else {
        VALUE_BARS = rows;
        document.getElementById('vcfg_collectDividends').checked = false;
        document.getElementById('vcfg_collectDividends').disabled = true;
        document.getElementById('valInstrument').textContent = file.name;
        valResetSim();
      }
      document.getElementById('fileStatus').textContent = 'Loaded ' + file.name + ' (' + rows.length + ' bars)';
    } catch (err) {
      document.getElementById('fileStatus').textContent = 'CSV error: ' + err.message;
    }
  };
  reader.readAsText(file);
});

// ================= SCALP MODE =================
let SCALP_BARS = ${SCALP_BARS_JSON};
const SCALP_STARTING_EQUITY = 100000;

function scalpReadConfig() {
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
    startingEquity: SCALP_STARTING_EQUITY,
  };
}

let scalpSim, scalpIdx, scalpPlaying, scalpTimer, scalpEntryMarkers, scalpScaleMarkers, scalpExitMarkers;
const SCALP_CSV_COLS = ['tradeId','symbol','side','entryTime','exitTime','initialEntryPrice','scale1Price','scale2Price','avgEntryPrice','exitPrice','initialQty','scale1Qty','scale2Qty','finalQty','stopPrice','targetPrice','exitReason','grossPnl','commission','slippage','netPnl','equityAfter','mfePct','maePct'];

function scalpResetSim() {
  scalpSim = AxiomEngine.createSimulation(scalpReadConfig());
  scalpIdx = 0; scalpPlaying = false;
  scalpEntryMarkers = []; scalpScaleMarkers = []; scalpExitMarkers = [];
  document.getElementById('tradesTable').querySelector('tbody').innerHTML = '';
  document.getElementById('scalpExport').value = SCALP_CSV_COLS.join(',') + '\\n';
  clearInterval(scalpTimer);
  scalpRender();
}

function fmt$(x) { return (x < 0 ? '-$' : '$') + Math.abs(x).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}); }
function fmtPct(x) { return x.toFixed(2) + '%'; }

function scalpAddTradeRow(t) {
  const tb = document.getElementById('tradesTable').querySelector('tbody');
  const tr = document.createElement('tr');
  const pnlClass = t.netPnl >= 0 ? 'up' : 'down';
  tr.innerHTML = '<td>'+t.tradeId+'</td><td>'+t.side+'</td><td>'+t.entryTime+'</td><td>'+t.exitTime+'</td>' +
    '<td>'+t.avgEntryPrice.toFixed(2)+'</td><td>'+t.exitPrice.toFixed(2)+'</td><td>'+t.finalQty+'</td>' +
    '<td>'+t.exitReason+'</td><td class="'+pnlClass+'">'+fmt$(t.netPnl)+'</td><td>'+fmt$(t.equityAfter)+'</td>';
  tb.prepend(tr);
  const exportEl = document.getElementById('scalpExport');
  exportEl.value += SCALP_CSV_COLS.map(c => t[c]).join(',') + '\\n';
}

function scalpStepOnce() {
  if (scalpIdx >= SCALP_BARS.length) { scalpPlaying = false; clearInterval(scalpTimer); return; }
  const b = SCALP_BARS[scalpIdx];
  const bar = { t: b.t, time: b.time, open: b.o, high: b.h, low: b.l, close: b.c, volume: b.v };
  const beforeTrades = scalpSim.trades.length;
  scalpSim.step(bar);
  if (scalpSim.trades.length > beforeTrades) {
    const t = scalpSim.trades[scalpSim.trades.length - 1];
    scalpAddTradeRow(t);
    scalpExitMarkers.push({ idx: scalpIdx, price: t.exitPrice, side: t.side, reason: t.exitReason });
  }
  for (let i = scalpSim.events.length - 1; i >= 0 && scalpSim.events[i].index === scalpIdx; i--) {
    const ev = scalpSim.events[i];
    if (ev.type === 'entry') scalpEntryMarkers.push({ idx: scalpIdx, price: ev.price, side: ev.side });
    if (ev.type === 'scale1' || ev.type === 'scale2') scalpScaleMarkers.push({ idx: scalpIdx, price: ev.price });
  }
  scalpIdx++;
  scalpRender();
}

function scalpFlattenNow() {
  if (scalpIdx === 0) return;
  const b = SCALP_BARS[scalpIdx - 1];
  const bar = { t: b.t, time: b.time, open: b.o, high: b.h, low: b.l, close: b.c, volume: b.v };
  const t = scalpSim.flatten(bar, 'manual_flatten');
  if (t) { scalpAddTradeRow(t); scalpExitMarkers.push({ idx: scalpIdx - 1, price: t.exitPrice, side: t.side, reason: 'manual_flatten' }); scalpRender(); }
}

function scalpRender() {
  const state = scalpSim.getState();
  document.getElementById('statBar').textContent = scalpIdx + ' / ' + SCALP_BARS.length;
  document.getElementById('statTime').textContent = scalpIdx > 0 ? SCALP_BARS[scalpIdx - 1].time : '—';
  document.getElementById('statEquity').textContent = fmt$(state.equity);
  const realized = state.equity - SCALP_STARTING_EQUITY;
  const pnlEl = document.getElementById('statPnl');
  pnlEl.textContent = fmt$(realized); pnlEl.className = 'value ' + (realized >= 0 ? 'up' : 'down');
  document.getElementById('statDD').textContent = fmtPct(state.maxDrawdownSeen);

  const posEl = document.getElementById('statPos');
  const upnlEl = document.getElementById('statUpnl');
  if (state.position) {
    const p = state.position;
    const lastClose = scalpIdx > 0 ? SCALP_BARS[scalpIdx - 1].c : p.currentAvg;
    const unrealized = p.side === 'long' ? (lastClose - p.currentAvg) * p.filledShares : (p.currentAvg - lastClose) * p.filledShares;
    posEl.textContent = p.side.toUpperCase() + ' ' + p.filledShares + ' @ ' + p.currentAvg.toFixed(2);
    posEl.className = 'value ' + (p.side === 'long' ? 'up' : 'down');
    upnlEl.textContent = fmt$(unrealized);
    upnlEl.className = 'value ' + (unrealized >= 0 ? 'up' : 'down');
  } else {
    posEl.textContent = 'Flat'; posEl.className = 'value';
    upnlEl.textContent = '$0.00'; upnlEl.className = 'value';
  }
  scalpDrawChart(state);
}

function scalpDrawChart(state) {
  const canvas = document.getElementById('chart');
  const wrap = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const cssW = wrap.clientWidth - 16, cssH = 440;
  canvas.width = cssW * dpr; canvas.height = cssH * dpr;
  canvas.style.width = cssW + 'px'; canvas.style.height = cssH + 'px';
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#12161f'; ctx.fillRect(0, 0, cssW, cssH);

  const WINDOW = 180;
  const start = Math.max(0, scalpIdx - WINDOW);
  const end = Math.max(start + 1, scalpIdx);
  const visible = SCALP_BARS.slice(start, end);
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

  const bw = Math.max(1, plotW / WINDOW * 0.6);
  visible.forEach((b, i) => {
    const x = xAt(i);
    const up = b.c >= b.o;
    ctx.strokeStyle = ctx.fillStyle = up ? '#29b6a3' : '#f2555a';
    ctx.beginPath(); ctx.moveTo(x, yAt(b.h)); ctx.lineTo(x, yAt(b.l)); ctx.stroke();
    const yO = yAt(b.o), yC = yAt(b.c);
    ctx.fillRect(x - bw / 2, Math.min(yO, yC), bw, Math.max(1, Math.abs(yC - yO)));
  });

  const closesAll = SCALP_BARS.slice(0, end).map(b => b.c);
  const cfg = scalpSim.config;
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

  if (state.position) {
    ctx.setLineDash([4, 4]); ctx.strokeStyle = '#6b7385';
    ctx.beginPath(); ctx.moveTo(padL, yAt(state.position.stopPrice)); ctx.lineTo(cssW - padR, yAt(state.position.stopPrice)); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(padL, yAt(state.position.targetPrice)); ctx.lineTo(cssW - padR, yAt(state.position.targetPrice)); ctx.stroke();
    ctx.setLineDash([]);
  }

  function marker(i, price, color) {
    if (i < start || i >= end) return;
    const x = xAt(i - start), y = yAt(price);
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
  }
  scalpEntryMarkers.forEach(m => marker(m.idx, m.price, m.side === 'long' ? '#29b6a3' : '#f2555a'));
  scalpScaleMarkers.forEach(m => marker(m.idx, m.price, '#a980ff'));
  scalpExitMarkers.forEach(m => marker(m.idx, m.price, '#e8ebf2'));
}

document.getElementById('btnPlay').onclick = () => {
  if (scalpPlaying) return;
  scalpPlaying = true;
  const tick = () => {
    if (!scalpPlaying) return;
    const speed = Number(document.getElementById('speedSel').value);
    const steps = Math.max(1, Math.round(speed));
    for (let i = 0; i < steps; i++) scalpStepOnce();
    if (scalpIdx < SCALP_BARS.length && scalpPlaying) scalpTimer = setTimeout(tick, 120 / speed);
  };
  tick();
};
document.getElementById('btnPause').onclick = () => { scalpPlaying = false; clearInterval(scalpTimer); };
document.getElementById('btnStep').onclick = () => { scalpPlaying = false; clearInterval(scalpTimer); scalpStepOnce(); };
document.getElementById('btnReset').onclick = () => scalpResetSim();
document.getElementById('btnFlatten').onclick = () => scalpFlattenNow();
document.getElementById('btnApply').onclick = () => scalpResetSim();

// ================= VALUE MODE =================
let VALUE_BARS = ${VALUE_BARS_JSON};
const DIVIDENDS = ${DIVIDENDS_JSON};
const VAL_STARTING_EQUITY = 100000;
const VAL_CSV_COLS = ['buyId','kind','band','date','price','shares','cost','cashRemainingAfter','sharesAfter','avgCostAfter','athAtTrigger','drawdownPctAtTrigger','commentary'];

function valReadConfig() {
  return {
    startingEquity: VAL_STARTING_EQUITY,
    initialDeployPct: Number(document.getElementById('vcfg_initialDeployPct').value),
    dipBandPct: Number(document.getElementById('vcfg_dipBandPct').value),
    dipAddPct: Number(document.getElementById('vcfg_dipAddPct').value),
    slippagePct: Number(document.getElementById('vcfg_slippagePct').value),
    commissionPerFill: Number(document.getElementById('vcfg_commissionPerFill').value),
    collectDividends: document.getElementById('vcfg_collectDividends').checked,
    dividends: DIVIDENDS,
  };
}

let valSim, valIdx, valPlaying, valTimer, valBuyMarkers, valBaseline;

function valComputeBaseline(cfg) {
  return BuffettEngine.runLumpSumBaseline(VALUE_BARS.map(b => ({ time: b.time, open: b.o, close: b.c })), cfg.startingEquity, cfg.slippagePct, cfg.commissionPerFill, cfg.collectDividends ? cfg.dividends : null);
}

function valResetSim() {
  const cfg = valReadConfig();
  valSim = BuffettEngine.createSimulation(cfg);
  valBaseline = valComputeBaseline(cfg);
  valIdx = 0; valPlaying = false; valBuyMarkers = [];
  document.getElementById('buysTable').querySelector('tbody').innerHTML = '';
  document.getElementById('valExport').value = VAL_CSV_COLS.join(',') + '\\n';
  document.getElementById('valQuote').textContent = 'Press Play. The initial stake goes in on day one — the rest waits.';
  clearInterval(valTimer);
  const baseReturnPct = ((valBaseline.finalEquity - cfg.startingEquity) / cfg.startingEquity) * 100;
  document.getElementById('valBaseReturn').textContent = fmtSignedPct(baseReturnPct);
  document.getElementById('valThisReturn').textContent = '—';
  document.getElementById('valEdgeReturn').textContent = '—';
  valRender();
}

function fmtSignedPct(x) { return (x >= 0 ? '+' : '') + x.toFixed(2) + '%'; }

function valAddBuyRow(b) {
  const tb = document.getElementById('buysTable').querySelector('tbody');
  const tr = document.createElement('tr');
  const dd = b.drawdownPctAtTrigger != null ? b.drawdownPctAtTrigger.toFixed(1) + '%' : '—';
  tr.innerHTML = '<td>'+b.buyId+'</td><td>'+b.kind+(b.band?(' (-'+(b.band*10)+'%)'):'')+'</td><td>'+b.date+'</td>' +
    '<td>'+fmt$(b.price)+'</td><td>'+b.shares+'</td><td>'+fmt$(b.cost)+'</td><td>'+dd+'</td><td>'+fmt$(b.cashRemainingAfter)+'</td>' +
    '<td class="commentary">'+b.commentary+'</td>';
  tb.prepend(tr);
  const exportEl = document.getElementById('valExport');
  exportEl.value += VAL_CSV_COLS.map(c => b[c]).join(',') + '\\n';
}

function valStepOnce() {
  if (valIdx >= VALUE_BARS.length) { valPlaying = false; clearInterval(valTimer); return; }
  const b = VALUE_BARS[valIdx];
  const bar = { t: b.t, time: b.time, open: b.o, high: b.h, low: b.l, close: b.c, volume: b.v };
  const beforeBuys = valSim.buys.length;
  valSim.step(bar);
  if (valSim.buys.length > beforeBuys) {
    const buy = valSim.buys[valSim.buys.length - 1];
    valAddBuyRow(buy);
    valBuyMarkers.push({ idx: valIdx, price: buy.price, kind: buy.kind });
    document.getElementById('valQuote').innerHTML = '<b>' + buy.date + ':</b> ' + buy.commentary;
  }
  for (let i = valSim.events.length - 1; i >= 0 && valSim.events[i].index === valIdx; i--) {
    if (valSim.events[i].type === 'new_ath') document.getElementById('valQuote').innerHTML = '<b>' + valSim.events[i].date + ':</b> ' + valSim.events[i].commentary;
  }
  valIdx++;
  valRender();
}

function valRender() {
  const state = valSim.getState();
  document.getElementById('valStatDate').textContent = valIdx > 0 ? VALUE_BARS[valIdx - 1].time : '—';
  document.getElementById('valStatEquity').textContent = fmt$(state.equity);
  const returnPct = ((state.equity - VAL_STARTING_EQUITY) / VAL_STARTING_EQUITY) * 100;
  const retEl = document.getElementById('valStatReturn');
  retEl.textContent = fmtSignedPct(returnPct); retEl.className = 'value ' + (returnPct >= 0 ? 'up' : 'down');
  document.getElementById('valStatShares').textContent = state.shares;
  document.getElementById('valStatAvgCost').textContent = fmt$(state.avgCost);
  document.getElementById('valStatCash').textContent = fmt$(state.cash);
  document.getElementById('valStatDiv').textContent = fmt$(state.totalDividendsCollected || 0);
  document.getElementById('valStatDD').textContent = state.maxDrawdownPct.toFixed(2) + '%';

  if (valIdx > 0 && valBaseline.equityCurve[valIdx - 1]) {
    const baseEqAt = valBaseline.equityCurve[valIdx - 1].equity;
    const baseRetAt = ((baseEqAt - VAL_STARTING_EQUITY) / VAL_STARTING_EQUITY) * 100;
    document.getElementById('valThisReturn').textContent = fmtSignedPct(returnPct);
    document.getElementById('valEdgeReturn').textContent = fmtSignedPct(returnPct - baseRetAt);
  }
  valDrawChart(state);
}

function valDrawChart(state) {
  const canvas = document.getElementById('valChart');
  const wrap = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const cssW = wrap.clientWidth - 16, cssH = 440;
  canvas.width = cssW * dpr; canvas.height = cssH * dpr;
  canvas.style.width = cssW + 'px'; canvas.style.height = cssH + 'px';
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#12161f'; ctx.fillRect(0, 0, cssW, cssH);
  if (valIdx < 2) return;

  const visible = VALUE_BARS.slice(0, valIdx);
  let lo = Infinity, hi = -Infinity;
  for (const b of visible) { lo = Math.min(lo, b.c); hi = Math.max(hi, b.c); }
  const pad = (hi - lo) * 0.06 || 1;
  lo -= pad; hi += pad;
  const padL = 8, padR = 8, padT = 8, padB = 8;
  const plotW = cssW - padL - padR, plotH = cssH - padT - padB;
  const xAt = i => padL + (i / (VALUE_BARS.length - 1)) * plotW;
  const yAt = p => padT + (1 - (p - lo) / (hi - lo)) * plotH;

  ctx.strokeStyle = '#8a93a8'; ctx.lineWidth = 1.5; ctx.beginPath();
  visible.forEach((b, i) => { const x = xAt(i), y = yAt(b.c); i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); });
  ctx.stroke();

  let ath = -Infinity;
  ctx.strokeStyle = '#f0ad3f'; ctx.lineWidth = 1; ctx.beginPath();
  visible.forEach((b, i) => { ath = Math.max(ath, b.c); const x = xAt(i), y = yAt(ath); i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); });
  ctx.stroke();

  valBuyMarkers.forEach(m => {
    const x = xAt(m.idx), y = yAt(m.price);
    ctx.fillStyle = '#29b6a3';
    ctx.beginPath(); ctx.arc(x, y, m.kind === 'initial' ? 5 : 4, 0, Math.PI * 2); ctx.fill();
  });
}

document.getElementById('valBtnPlay').onclick = () => {
  if (valPlaying) return;
  valPlaying = true;
  const tick = () => {
    if (!valPlaying) return;
    const speed = Number(document.getElementById('valSpeedSel').value);
    for (let i = 0; i < speed; i++) valStepOnce();
    if (valIdx < VALUE_BARS.length && valPlaying) valTimer = setTimeout(tick, 60);
  };
  tick();
};
document.getElementById('valBtnPause').onclick = () => { valPlaying = false; clearInterval(valTimer); };
document.getElementById('valBtnStep').onclick = () => { valPlaying = false; clearInterval(valTimer); valStepOnce(); };
document.getElementById('valBtnReset').onclick = () => valResetSim();
document.getElementById('valBtnApply').onclick = () => valResetSim();

window.addEventListener('resize', () => { scalpRender(); valRender(); });

scalpResetSim();
valResetSim();
</script>
`;

const OUT = path.join(__dirname, '..', 'ui', 'studio.html');
fs.writeFileSync(OUT, html);
console.log('Wrote ' + OUT + ' (' + (html.length / 1024).toFixed(0) + ' KB)');
