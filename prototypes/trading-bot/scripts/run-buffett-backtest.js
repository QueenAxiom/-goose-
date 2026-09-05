const fs = require('fs');
const path = require('path');
const { runBacktest, runLumpSumBaseline, DEFAULT_CONFIG } = require('../src/buffett-engine.js');
const { loadDailyBars, loadDividends } = require('../src/data-loader.js');
const { buildDashboard } = require('../src/buffett-stats.js');

const DATA_PATH = path.join(__dirname, '..', 'data', 'spy_1d.csv');
const DIV_PATH = path.join(__dirname, '..', 'data', 'spy_dividends.csv');
const RESULTS_DIR = path.join(__dirname, '..', 'results', 'buffett');

const bars = loadDailyBars(DATA_PATH);
const dividends = loadDividends(DIV_PATH);
fs.mkdirSync(RESULTS_DIR, { recursive: true });

function csvEscape(v) {
  if (v === null || v === undefined) return '';
  const s = String(v);
  return /[,"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function writeVariant(name, config) {
  const dir = path.join(RESULTS_DIR, name);
  fs.mkdirSync(dir, { recursive: true });
  const result = runBacktest(bars, config);
  // Fair comparison: the baseline collects the same real dividends when the variant does,
  // so "vs baseline" isolates the dip-buying ladder's edge, not just "dividends exist."
  const baseline = runLumpSumBaseline(bars, config.startingEquity, config.slippagePct, config.commissionPerFill, config.collectDividends ? config.dividends : null);
  const dashboard = buildDashboard(result, bars, baseline);

  const buyCols = ['buyId', 'kind', 'band', 'date', 'price', 'shares', 'cost', 'cashRemainingAfter',
    'sharesAfter', 'avgCostAfter', 'athAtTrigger', 'drawdownPctAtTrigger', 'commentary'];
  const buyLines = [buyCols.join(',')];
  for (const b of result.buys) buyLines.push(buyCols.map(c => csvEscape(b[c])).join(','));
  fs.writeFileSync(path.join(dir, 'buys_log.csv'), buyLines.join('\n') + '\n');

  const eqLines = ['date,equity,cash,shares,close,drawdownPct'];
  for (const e of result.equityCurve) eqLines.push([e.date, e.equity, e.cash, e.shares, e.close, e.drawdownPct].join(','));
  fs.writeFileSync(path.join(dir, 'equity_curve.csv'), eqLines.join('\n') + '\n');

  if (result.dividendPayments && result.dividendPayments.length) {
    const divLines = ['date,perShare,shares,amount'];
    for (const d of result.dividendPayments) divLines.push([d.date, d.perShare, d.shares, d.amount].join(','));
    fs.writeFileSync(path.join(dir, 'dividend_payments.csv'), divLines.join('\n') + '\n');
  }

  fs.writeFileSync(path.join(dir, 'dashboard.json'), JSON.stringify(dashboard, null, 2));
  fs.writeFileSync(path.join(dir, 'config.json'), JSON.stringify({
    dataSource: 'Yahoo Finance chart API (query1.finance.yahoo.com/v8/finance/chart/SPY), interval=1d, events=div',
    dateRange: `${bars[0].time} -> ${bars[bars.length - 1].time}`,
    barCount: bars.length,
    config: Object.assign({}, config, { dividends: config.dividends ? `${config.dividends.length} real historical payments, see dividend_payments.csv` : undefined }),
  }, null, 2));
  return dashboard;
}

const baseConfig = Object.assign({}, DEFAULT_CONFIG);
const dividendConfig = Object.assign({}, DEFAULT_CONFIG, { collectDividends: true, dividends });

const noDiv = writeVariant('no-dividends', baseConfig);
const withDiv = writeVariant('with-dividends', dividendConfig);

fs.writeFileSync(path.join(RESULTS_DIR, 'comparison.json'), JSON.stringify({ noDividends: noDiv, withDividends: withDiv }, null, 2));

console.log('AXIOM TRADING BOT - "Buffett" systematic proxy');
console.log(`Data: SPY daily, ${noDiv.dataRange} (${noDiv.years} years, ${bars.length} bars)`);
console.log('');
console.log('=== WITHOUT dividend reinvestment (original) ===');
console.log(`Ending equity: $${noDiv.endingEquity}  Return: ${noDiv.returnPct}%  CAGR: ${noDiv.cagrPct}%  MaxDD: ${noDiv.maxDrawdownPct}%`);
console.log(`Buys: ${noDiv.numBuys}  Final cash: ${noDiv.finalCashPct}%`);
console.log('');
console.log('=== WITH dividend reinvestment (real SPY dividend history) ===');
console.log(`Ending equity: $${withDiv.endingEquity}  Return: ${withDiv.returnPct}%  CAGR: ${withDiv.cagrPct}%  MaxDD: ${withDiv.maxDrawdownPct}%`);
console.log(`Buys: ${withDiv.numBuys}  Final cash: ${withDiv.finalCashPct}%  Dividends collected: $${withDiv.dividendsCollected} (${withDiv.numDividendPayments} payments)`);
console.log('');
console.log(`Difference: $${(withDiv.endingEquity - noDiv.endingEquity).toFixed(2)}  (${(withDiv.returnPct - noDiv.returnPct).toFixed(2)} points of return)`);
