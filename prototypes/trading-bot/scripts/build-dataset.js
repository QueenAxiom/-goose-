// Converts the raw Yahoo Finance chart-API response into a clean OHLCV CSV.
// Source: data/spy_5m_raw.json (preserved as downloaded, untouched).
const fs = require('fs');
const path = require('path');

const RAW_PATH = path.join(__dirname, '..', 'data', 'spy_5m_raw.json');
const OUT_PATH = path.join(__dirname, '..', 'data', 'spy_5m.csv');

const raw = JSON.parse(fs.readFileSync(RAW_PATH, 'utf8'));
const result = raw.chart.result[0];
const ts = result.timestamp;
const q = result.indicators.quote[0];
const meta = result.meta;

// meta.gmtoffset is seconds offset from UTC for the exchange timezone at fetch time.
// Fetch window (2026-05-29 .. 2026-08-24) sits entirely inside EDT (no DST transition),
// so a single fixed offset is valid for the whole dataset. Documented assumption.
const gmtOffsetSec = meta.gmtoffset;

const rows = [];
for (let i = 0; i < ts.length; i++) {
  const o = q.open[i], h = q.high[i], l = q.low[i], c = q.close[i], v = q.volume[i];
  // Drop bars with any null OHLC field (Yahoo returns sparse nulls, e.g. halts/gaps).
  if (o == null || h == null || l == null || c == null) continue;
  // Drop bars not aligned to the 5-minute grid: Yahoo's final row is often a live,
  // still-forming partial candle (irregular timestamp, volume=0). Using it would be
  // trading on an incomplete/uncommitted bar, so it is excluded.
  if (ts[i] % 300 !== 0) continue;
  const utcIso = new Date(ts[i] * 1000).toISOString();
  const localMs = (ts[i] + gmtOffsetSec) * 1000;
  const localIso = new Date(localMs).toISOString().replace('Z', '');
  rows.push({ epoch: ts[i], utc: utcIso, local: localIso, open: o, high: h, low: l, close: c, volume: v ?? 0 });
}

const header = 'epoch,utc_time,local_time_America_New_York,open,high,low,close,volume';
const lines = rows.map(r => `${r.epoch},${r.utc},${r.local},${r.open},${r.high},${r.low},${r.close},${r.volume}`);
fs.writeFileSync(OUT_PATH, header + '\n' + lines.join('\n') + '\n');

console.log(`Wrote ${rows.length} clean bars to ${OUT_PATH}`);
console.log(`Range: ${rows[0].local} -> ${rows[rows.length - 1].local} (local exchange time)`);
console.log(`Dropped ${ts.length - rows.length} bars with null OHLC fields.`);
