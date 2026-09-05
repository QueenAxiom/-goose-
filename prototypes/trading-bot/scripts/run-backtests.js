const fs = require('fs');
const path = require('path');
const { runBacktest, DEFAULT_CONFIG } = require('../src/engine.js');
const { loadBars } = require('../src/data-loader.js');
const { buildDashboard } = require('../src/stats.js');

const DATA_PATH = path.join(__dirname, '..', 'data', 'spy_5m.csv');
const RESULTS_DIR = path.join(__dirname, '..', 'results');

const bars = loadBars(DATA_PATH);

const TESTS = {
  A: { label: 'Long + Short enabled, scaling enabled', overrides: { longEnabled: true, shortEnabled: true, scalingEnabled: true } },
  B: { label: 'Long only, scaling enabled', overrides: { longEnabled: true, shortEnabled: false, scalingEnabled: true } },
  C: { label: 'Short only, scaling enabled', overrides: { longEnabled: false, shortEnabled: true, scalingEnabled: true } },
  D: { label: 'Long + Short enabled, scaling DISABLED', overrides: { longEnabled: true, shortEnabled: true, scalingEnabled: false } },
  E: { label: 'Long + Short enabled, scaling enabled (duplicate of A, listed separately per spec)', overrides: { longEnabled: true, shortEnabled: true, scalingEnabled: true } },
};

function csvEscape(v) {
  if (v === null || v === undefined) return '';
  const s = String(v);
  return /[,"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function writeTradeLogCsv(trades, outPath) {
  const cols = ['tradeId', 'symbol', 'side', 'entryTime', 'exitTime', 'initialEntryPrice', 'scale1Price',
    'scale2Price', 'avgEntryPrice', 'exitPrice', 'initialQty', 'scale1Qty', 'scale2Qty', 'finalQty',
    'stopPrice', 'targetPrice', 'exitReason', 'grossPnl', 'commission', 'slippage', 'netPnl',
    'equityAfter', 'mfePct', 'maePct'];
  const lines = [cols.join(',')];
  for (const t of trades) lines.push(cols.map(c => csvEscape(t[c])).join(','));
  fs.writeFileSync(outPath, lines.join('\n') + '\n');
}

function writeEquityCurveCsv(equityCurve, outPath) {
  const lines = ['tradeIndex,time,equity,drawdownPct,tradeId'];
  equityCurve.forEach((e, i) => lines.push([i + 1, e.time, e.equity, e.drawdownPct, e.tradeId].join(',')));
  fs.writeFileSync(outPath, lines.join('\n') + '\n');
}

const summary = {};

for (const [key, testDef] of Object.entries(TESTS)) {
  const config = Object.assign({}, DEFAULT_CONFIG, testDef.overrides);
  const result = runBacktest(bars, config);
  const dashboard = buildDashboard(result, config.startingEquity);

  const dir = path.join(RESULTS_DIR, `test${key}`);
  fs.mkdirSync(dir, { recursive: true });
  writeTradeLogCsv(result.trades, path.join(dir, 'trade_log.csv'));
  writeEquityCurveCsv(result.equityCurve, path.join(dir, 'equity_curve.csv'));
  fs.writeFileSync(path.join(dir, 'dashboard.json'), JSON.stringify(dashboard, null, 2));
  fs.writeFileSync(path.join(dir, 'events.json'), JSON.stringify(result.events, null, 2));
  fs.writeFileSync(path.join(dir, 'config.json'), JSON.stringify({
    testLabel: testDef.label,
    dataSource: 'Yahoo Finance chart API (query1.finance.yahoo.com/v8/finance/chart/SPY), interval=5m',
    dateRangeLocal: `${bars[0].time} -> ${bars[bars.length - 1].time} (America/New_York)`,
    barCount: bars.length,
    config,
  }, null, 2));

  summary[key] = { label: testDef.label, dashboard };
  console.log(`Test ${key}: ${testDef.label}`);
  console.log(`  Trades: ${dashboard.numTrades}  WinRate: ${dashboard.winRatePct}%  NetPnL: $${dashboard.netPnl}  Return: ${dashboard.returnPct}%  MaxDD: ${dashboard.maxDrawdownPct}%  ProfitFactor: ${dashboard.profitFactor}`);
}

fs.writeFileSync(path.join(RESULTS_DIR, 'comparison.json'), JSON.stringify(summary, null, 2));

// Markdown comparison table
const rows = Object.entries(summary).map(([k, v]) => {
  const d = v.dashboard;
  return `| ${k} | ${v.label} | ${d.numTrades} | ${d.winRatePct}% | $${d.netPnl} | ${d.returnPct}% | ${d.profitFactor} | ${d.maxDrawdownPct}% | ${d.longTrades} | ${d.shortTrades} | ${d.numScaleIns} |`;
});
const md = `# Backtest Comparison — SPY 5m, ${bars[0].time} to ${bars[bars.length - 1].time}

| Test | Description | Trades | Win Rate | Net P&L | Return | Profit Factor | Max DD | Long | Short | Scale-ins |
|---|---|---|---|---|---|---|---|---|---|---|
${rows.join('\n')}
`;
fs.writeFileSync(path.join(RESULTS_DIR, 'comparison.md'), md);

console.log('\nWrote results/comparison.json and results/comparison.md');
