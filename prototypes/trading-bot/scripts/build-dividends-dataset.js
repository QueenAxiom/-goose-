// Extracts SPY's real historical dividend payments from the same Yahoo Finance
// chart-API response (fetched with events=div) used for the daily price data.
// Source: data/spy_1d_div_raw.json (preserved as downloaded, untouched).
const fs = require('fs');
const path = require('path');

const RAW_PATH = path.join(__dirname, '..', 'data', 'spy_1d_div_raw.json');
const OUT_PATH = path.join(__dirname, '..', 'data', 'spy_dividends.csv');

const raw = JSON.parse(fs.readFileSync(RAW_PATH, 'utf8'));
const result = raw.chart.result[0];
const divEvents = result.events && result.events.dividends ? Object.values(result.events.dividends) : [];
divEvents.sort((a, b) => a.date - b.date);

const rows = divEvents.map(e => ({
  date: new Date(e.date * 1000).toISOString().slice(0, 10),
  amountPerShare: e.amount,
}));

fs.writeFileSync(OUT_PATH, 'date,amountPerShare\n' + rows.map(r => `${r.date},${r.amountPerShare}`).join('\n') + '\n');
console.log(`Wrote ${rows.length} dividend payments to ${OUT_PATH}`);
console.log(`Range: ${rows[0].date} -> ${rows[rows.length - 1].date}`);
console.log(`Total per share over period: $${rows.reduce((s, r) => s + r.amountPerShare, 0).toFixed(2)}`);
