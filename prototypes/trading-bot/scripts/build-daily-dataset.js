// Converts the raw Yahoo Finance daily chart-API response into a clean OHLCV CSV.
// Source: data/spy_1d_raw.json (preserved as downloaded, untouched).
const fs = require('fs');
const path = require('path');

const RAW_PATH = path.join(__dirname, '..', 'data', 'spy_1d_raw.json');
const OUT_PATH = path.join(__dirname, '..', 'data', 'spy_1d.csv');

const raw = JSON.parse(fs.readFileSync(RAW_PATH, 'utf8'));
const result = raw.chart.result[0];
const ts = result.timestamp;
const q = result.indicators.quote[0];

const rows = [];
for (let i = 0; i < ts.length; i++) {
  const o = q.open[i], h = q.high[i], l = q.low[i], c = q.close[i], v = q.volume[i];
  if (o == null || h == null || l == null || c == null) continue;
  const utcIso = new Date(ts[i] * 1000).toISOString();
  const dateOnly = utcIso.slice(0, 10); // daily bars: the calendar date is what matters, not the intraday timestamp
  rows.push({ epoch: ts[i], date: dateOnly, open: o, high: h, low: l, close: c, volume: v ?? 0 });
}

// The most recent bar can be today's still-in-progress session (fetched intraday,
// same issue as the 5m dataset's trailing partial candle) - drop it if so, since
// trading on an incomplete/uncommitted daily bar would be a look-ahead risk.
const todayUtc = new Date().toISOString().slice(0, 10);
if (rows.length && rows[rows.length - 1].date === todayUtc) {
  rows.pop();
}

const header = 'epoch,date,open,high,low,close,volume';
const lines = rows.map(r => `${r.epoch},${r.date},${r.open},${r.high},${r.low},${r.close},${r.volume}`);
fs.writeFileSync(OUT_PATH, header + '\n' + lines.join('\n') + '\n');

console.log(`Wrote ${rows.length} clean daily bars to ${OUT_PATH}`);
console.log(`Range: ${rows[0].date} -> ${rows[rows.length - 1].date}`);
console.log(`Dropped ${ts.length - rows.length} bars with null OHLC fields.`);
