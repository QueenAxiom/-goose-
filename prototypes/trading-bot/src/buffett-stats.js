function round2(x) { return Math.round(x * 100) / 100; }

function yearsBetween(dateA, dateB) {
  return (new Date(dateB) - new Date(dateA)) / (365.25 * 24 * 3600 * 1000);
}

function buildDashboard(result, bars, baseline) {
  const { buys, equityCurve, finalState, config } = result;
  const startingEquity = config.startingEquity;
  const endingEquity = equityCurve[equityCurve.length - 1].equity;
  const netPnl = endingEquity - startingEquity;
  const returnPct = (netPnl / startingEquity) * 100;
  const years = yearsBetween(bars[0].time, bars[bars.length - 1].time);
  const cagrPct = years > 0 ? (Math.pow(endingEquity / startingEquity, 1 / years) - 1) * 100 : 0;

  const dipBuys = buys.filter(b => b.kind === 'dip');
  const deepestBand = dipBuys.length ? Math.max(...dipBuys.map(b => b.band)) : 0;

  const baselineReturnPct = ((baseline.finalEquity - startingEquity) / startingEquity) * 100;
  const baselineCagrPct = years > 0 ? (Math.pow(baseline.finalEquity / startingEquity, 1 / years) - 1) * 100 : 0;

  return {
    dataRange: `${bars[0].time} -> ${bars[bars.length - 1].time}`,
    years: round2(years),
    startingEquity: round2(startingEquity),
    endingEquity: round2(endingEquity),
    netPnl: round2(netPnl),
    returnPct: round2(returnPct),
    cagrPct: round2(cagrPct),
    maxDrawdownPct: round2(finalState.maxDrawdownPct),
    numBuys: buys.length,
    initialBuys: buys.filter(b => b.kind === 'initial').length,
    dipBuys: dipBuys.length,
    deepestDrawdownBandHit: deepestBand,
    finalShares: finalState.shares,
    avgCostBasis: finalState.avgCost,
    finalCashPct: startingEquity > 0 ? round2((finalState.cash / startingEquity) * 100) : 0,
    deployedPct: finalState.deployedPct,
    dividendsCollected: finalState.totalDividendsCollected || 0,
    numDividendPayments: (result.dividendPayments || []).length,
    baseline: {
      description: config.collectDividends
        ? '100% lump-sum on day 1, no dip-buying ladder, but collects the same real dividends (fair comparison - isolates the ladder\'s edge)'
        : '100% lump-sum on day 1, no dip-buying, no cash reserve, no dividends',
      finalEquity: round2(baseline.finalEquity),
      returnPct: round2(baselineReturnPct),
      cagrPct: round2(baselineCagrPct),
      maxDrawdownPct: round2(baseline.maxDrawdownPct),
      dividendsCollected: baseline.totalDividendsCollected || 0,
    },
    vsBaselinePct: round2(returnPct - baselineReturnPct),
    config,
  };
}

module.exports = { buildDashboard };
