function round2(x) { return Math.round(x * 100) / 100; }

// local exchange-time ISO strings (no 'Z') - fine to parse as-is for duration diffs,
// since both entry and exit come from the same consistent local clock.
function durationMinutes(entryTime, exitTime) {
  const a = new Date(entryTime).getTime();
  const b = new Date(exitTime).getTime();
  return (b - a) / 60000;
}

function buildDashboard(result, startingEquity) {
  const { trades, equityCurve, config } = result;
  const n = trades.length;
  const wins = trades.filter(t => t.netPnl > 0);
  const losses = trades.filter(t => t.netPnl <= 0);
  const endingEquity = n > 0 ? trades[n - 1].equityAfter : startingEquity;
  const netPnl = endingEquity - startingEquity;
  const returnPct = (netPnl / startingEquity) * 100;

  const grossWin = wins.reduce((s, t) => s + t.netPnl, 0);
  const grossLoss = Math.abs(losses.reduce((s, t) => s + t.netPnl, 0));
  const profitFactor = grossLoss > 0 ? grossWin / grossLoss : (grossWin > 0 ? Infinity : 0);

  const avgWin = wins.length ? grossWin / wins.length : 0;
  const avgLoss = losses.length ? -grossLoss / losses.length : 0;
  const avgTrade = n ? trades.reduce((s, t) => s + t.netPnl, 0) / n : 0;

  const maxDrawdownPct = equityCurve.length ? Math.max(...equityCurve.map(e => e.drawdownPct)) : 0;

  // Trade-based Sharpe: mean/stdev of per-trade % return on equity-at-entry, unannualized.
  // Only reported when n >= 10 (documented threshold for "statistically meaningful").
  let sharpe = null;
  if (n >= 10) {
    const rets = trades.map(t => {
      const equityBefore = t.equityAfter - t.netPnl;
      return equityBefore > 0 ? (t.netPnl / equityBefore) * 100 : 0;
    });
    const mean = rets.reduce((a, b) => a + b, 0) / rets.length;
    const variance = rets.reduce((s, r) => s + (r - mean) ** 2, 0) / (rets.length - 1);
    const stdev = Math.sqrt(variance);
    sharpe = stdev > 0 ? mean / stdev : null;
  }

  const largestWinner = wins.length ? Math.max(...wins.map(t => t.netPnl)) : 0;
  const largestLoser = losses.length ? Math.min(...losses.map(t => t.netPnl)) : 0;

  const longTrades = trades.filter(t => t.side === 'long').length;
  const shortTrades = trades.filter(t => t.side === 'short').length;

  const durations = trades.map(t => durationMinutes(t.entryTime, t.exitTime));
  const avgDurationMin = durations.length ? durations.reduce((a, b) => a + b, 0) / durations.length : 0;

  const scaleIns = trades.reduce((s, t) => s + (t.scale1Qty > 0 ? 1 : 0) + (t.scale2Qty > 0 ? 1 : 0), 0);

  const targetExits = trades.filter(t => t.exitReason === 'target').length;
  const stopExits = trades.filter(t => t.exitReason === 'stop').length;
  const reversalExits = trades.filter(t => t.exitReason === 'trend_reversal').length;
  const manualExits = trades.filter(t => t.exitReason === 'manual_flatten').length;

  return {
    startingEquity: round2(startingEquity),
    endingEquity: round2(endingEquity),
    netPnl: round2(netPnl),
    returnPct: round2(returnPct),
    numTrades: n,
    winningTrades: wins.length,
    losingTrades: losses.length,
    winRatePct: n ? round2((wins.length / n) * 100) : 0,
    avgWinningTrade: round2(avgWin),
    avgLosingTrade: round2(avgLoss),
    avgTrade: round2(avgTrade),
    profitFactor: isFinite(profitFactor) ? round2(profitFactor) : 'Infinity',
    maxDrawdownPct: round2(maxDrawdownPct),
    sharpeRatioPerTrade: sharpe !== null ? round2(sharpe) : null,
    sharpeNote: 'Per-trade Sharpe (mean/stdev of trade % returns), NOT annualized. Only computed for n>=10 trades.',
    largestWinner: round2(largestWinner),
    largestLoser: round2(largestLoser),
    longTrades,
    shortTrades,
    avgTradeDurationMin: round2(avgDurationMin),
    numScaleIns: scaleIns,
    pctReachedTarget: n ? round2((targetExits / n) * 100) : 0,
    pctStoppedOut: n ? round2((stopExits / n) * 100) : 0,
    pctExitedByReversal: n ? round2((reversalExits / n) * 100) : 0,
    pctExitedManually: n ? round2((manualExits / n) * 100) : 0,
    killSwitchTriggered: result.finalState.killSwitchActive,
    openPositionAtEnd: !!result.openPositionAtEnd,
    config,
  };
}

module.exports = { buildDashboard };
