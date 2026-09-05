// Axiom Trading Bot - Historical Replay Lab
// Core simulation engine. Bar-by-bar, causal only (no look-ahead).
// Shared verbatim between the Node CLI backtest runner and the browser replay UI
// (UMD-style export below) so both surfaces run the identical logic.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AxiomEngine = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {

  const DEFAULT_CONFIG = {
    emaFast: 9,
    emaSlow: 21,
    initialRiskPct: 0.35,   // % of current equity risked on the initial tranche
    stopPct: 0.22,          // % from initial entry reference
    targetPct: 0.44,        // % from initial entry reference
    scale1Pct: 0.11,        // % from initial entry reference
    scale2Pct: 0.22,        // % from initial entry reference
    initialPositionPct: 50, // % of calculated trade size
    scale1PositionPct: 25,
    scale2PositionPct: 25,
    slippagePct: 0.01,      // % per side
    commissionPerFill: 0,   // $ flat per fill (entry tranche or exit)
    maxDrawdownPct: 20,     // kill switch: % drawdown from equity peak
    longEnabled: true,
    shortEnabled: true,
    scalingEnabled: true,
    startingEquity: 100000,
  };

  // Causal EMA: first (period-1) values are null (insufficient data), seed = SMA(period).
  function computeEMA(closes, period) {
    const out = new Array(closes.length).fill(null);
    const k = 2 / (period + 1);
    let sum = 0;
    for (let i = 0; i < closes.length; i++) {
      if (i < period - 1) { sum += closes[i]; continue; }
      if (i === period - 1) {
        sum += closes[i];
        out[i] = sum / period;
        continue;
      }
      out[i] = closes[i] * k + out[i - 1] * (1 - k);
    }
    return out;
  }

  function round2(x) { return Math.round(x * 100) / 100; }

  function makeTradeId(counter) { return 'T' + String(counter).padStart(4, '0'); }

  // Creates a fresh, independent simulation runner. Call step(bar) once per bar in order.
  function createSimulation(config) {
    const cfg = Object.assign({}, DEFAULT_CONFIG, config || {});
    const closes = [];
    const emaFastArr = [];
    const emaSlowArr = [];

    let equity = cfg.startingEquity;
    let peakEquity = cfg.startingEquity;
    let maxDrawdownSeen = 0;
    let killSwitchActive = false;

    let position = null;      // active position object, or null
    let pendingSignal = null; // { side, readyIndex } - enter on bar[readyIndex].open
    let tradeCounter = 0;

    const trades = [];        // closed trades
    const equityCurve = [];   // [{index, time, equity, drawdownPct}] appended on every closed trade
    const events = [];        // human-readable event log (entries, scales, exits, signals)
    let barIndex = -1;

    function emaK(period) { return 2 / (period + 1); }

    function updateEma(arr, price, period) {
      const n = arr.length; // number of closes seen so far, before this one is pushed
      if (n < period - 1) { arr.push(null); return; }
      if (n === period - 1) {
        // seed with SMA using the last `period` closes (this one included)
        const seed = (closes.slice(n - period + 1).reduce((a, b) => a + b, 0) + price) / period;
        arr.push(seed);
        return;
      }
      const prev = arr[n - 1];
      arr.push(price * emaK(period) + prev * (1 - emaK(period)));
    }

    function priceWithSlippage(price, side, action) {
      // side: 'long' | 'short'; action: 'entry' | 'exit'
      const s = cfg.slippagePct / 100;
      const buying = (side === 'long' && action === 'entry') || (side === 'short' && action === 'exit');
      return buying ? price * (1 + s) : price * (1 - s);
    }

    function computeTradeSize(entryRefPrice) {
      const riskBudget = equity * (cfg.initialRiskPct / 100);
      const stopDistancePerShare = entryRefPrice * (cfg.stopPct / 100);
      const initialFraction = cfg.initialPositionPct / 100;
      // initialFraction * totalShares * stopDistancePerShare = riskBudget
      const totalShares = riskBudget / (initialFraction * stopDistancePerShare);
      return Math.max(0, Math.floor(totalShares));
    }

    function openPosition(side, refPrice, time, idx) {
      const totalShares = computeTradeSize(refPrice);
      if (totalShares <= 0) return null;
      const initialShares = Math.floor(totalShares * (cfg.initialPositionPct / 100));
      if (initialShares <= 0) return null;
      const fillPrice = priceWithSlippage(refPrice, side, 'entry');
      tradeCounter++;
      const stopPrice = side === 'long'
        ? refPrice * (1 - cfg.stopPct / 100)
        : refPrice * (1 + cfg.stopPct / 100);
      const targetPrice = side === 'long'
        ? refPrice * (1 + cfg.targetPct / 100)
        : refPrice * (1 - cfg.targetPct / 100);
      const scale1Price = side === 'long'
        ? refPrice * (1 + cfg.scale1Pct / 100)
        : refPrice * (1 - cfg.scale1Pct / 100);
      const scale2Price = side === 'long'
        ? refPrice * (1 + cfg.scale2Pct / 100)
        : refPrice * (1 - cfg.scale2Pct / 100);

      const pos = {
        tradeId: makeTradeId(tradeCounter),
        side,
        entryTime: time,
        entryIndex: idx,
        initialEntryRef: refPrice,
        totalPlannedShares: totalShares,
        stopPrice, targetPrice, scale1Price, scale2Price,
        scale1Filled: false, scale2Filled: false,
        // rawPrice = theoretical level price (no slippage); price = actual filled price (with slippage)
        tranches: [{ stage: 'initial', rawPrice: refPrice, price: fillPrice, shares: initialShares, time }],
        filledShares: initialShares,
        commissionPaid: cfg.commissionPerFill,
        mfe: 0, mae: 0, // favorable/adverse excursion in %, tracked from avg entry
      };
      return pos;
    }

    function avgEntryPrice(pos) {
      const totalCost = pos.tranches.reduce((s, t) => s + t.price * t.shares, 0);
      return totalCost / pos.filledShares;
    }

    function avgRawEntryPrice(pos) {
      const totalCost = pos.tranches.reduce((s, t) => s + t.rawPrice * t.shares, 0);
      return totalCost / pos.filledShares;
    }

    function tryScaleIn(pos, bar, time) {
      if (!cfg.scalingEnabled) return;
      const remainingCapacity = pos.totalPlannedShares - pos.filledShares;
      if (remainingCapacity <= 0) return;
      const scale1Shares = Math.floor(pos.totalPlannedShares * (cfg.scale1PositionPct / 100));
      const scale2Shares = Math.floor(pos.totalPlannedShares * (cfg.scale2PositionPct / 100));

      if (!pos.scale1Filled) {
        const touched = pos.side === 'long' ? bar.high >= pos.scale1Price : bar.low <= pos.scale1Price;
        if (touched && scale1Shares > 0) {
          const fillPrice = priceWithSlippage(pos.scale1Price, pos.side, 'entry');
          pos.tranches.push({ stage: 'scale1', rawPrice: pos.scale1Price, price: fillPrice, shares: scale1Shares, time });
          pos.filledShares += scale1Shares;
          pos.scale1Filled = true;
          pos.commissionPaid += cfg.commissionPerFill;
          events.push({ index: barIndex, time, type: 'scale1', tradeId: pos.tradeId, price: fillPrice, shares: scale1Shares });
        }
      }
      if (!pos.scale2Filled) {
        const touched = pos.side === 'long' ? bar.high >= pos.scale2Price : bar.low <= pos.scale2Price;
        if (touched && scale2Shares > 0) {
          const fillPrice = priceWithSlippage(pos.scale2Price, pos.side, 'entry');
          pos.tranches.push({ stage: 'scale2', rawPrice: pos.scale2Price, price: fillPrice, shares: scale2Shares, time });
          pos.filledShares += scale2Shares;
          pos.scale2Filled = true;
          pos.commissionPaid += cfg.commissionPerFill;
          events.push({ index: barIndex, time, type: 'scale2', tradeId: pos.tradeId, price: fillPrice, shares: scale2Shares });
        }
      }
    }

    function updateExcursion(pos, bar) {
      const avg = avgEntryPrice(pos);
      const favHigh = pos.side === 'long' ? bar.high : bar.low;
      const advLow = pos.side === 'long' ? bar.low : bar.high;
      const favPct = pos.side === 'long' ? (favHigh - avg) / avg * 100 : (avg - favHigh) / avg * 100;
      const advPct = pos.side === 'long' ? (avg - advLow) / avg * 100 : (advLow - avg) / avg * 100;
      pos.mfe = Math.max(pos.mfe, favPct);
      pos.mae = Math.max(pos.mae, advPct);
    }

    function closePosition(pos, exitPrice, exitReason, time, idx) {
      const fillPrice = priceWithSlippage(exitPrice, pos.side, 'exit');
      const avg = avgEntryPrice(pos);       // actual (slipped) average entry, used for MFE/MAE and reporting
      const avgRaw = avgRawEntryPrice(pos); // theoretical (unslipped) average entry, used for gross P&L

      // Gross P&L: theoretical result at ideal (unslipped) levels - what the strategy's
      // edge produced before trading costs.
      const grossPnl = pos.side === 'long'
        ? (exitPrice - avgRaw) * pos.filledShares
        : (avgRaw - exitPrice) * pos.filledShares;

      // Slippage $ cost: sum of |filled - raw| * shares across every entry fill, plus the exit fill.
      const entrySlippageCost = pos.tranches.reduce((s, t) => s + Math.abs(t.price - t.rawPrice) * t.shares, 0);
      const exitSlippageCost = Math.abs(fillPrice - exitPrice) * pos.filledShares;
      const totalSlippageCost = entrySlippageCost + exitSlippageCost;

      const exitCommission = cfg.commissionPerFill;
      const totalCommission = pos.commissionPaid + exitCommission;

      const netPnl = grossPnl - totalCommission - totalSlippageCost;

      equity += netPnl;
      peakEquity = Math.max(peakEquity, equity);
      const drawdownPct = peakEquity > 0 ? ((peakEquity - equity) / peakEquity) * 100 : 0;
      maxDrawdownSeen = Math.max(maxDrawdownSeen, drawdownPct);
      if (!killSwitchActive && maxDrawdownSeen >= cfg.maxDrawdownPct) {
        killSwitchActive = true;
        events.push({ index: idx, time, type: 'kill_switch', drawdownPct: round2(maxDrawdownSeen) });
      }

      const scale1 = pos.tranches.find(t => t.stage === 'scale1');
      const scale2 = pos.tranches.find(t => t.stage === 'scale2');
      const initial = pos.tranches.find(t => t.stage === 'initial');

      const trade = {
        tradeId: pos.tradeId,
        symbol: 'SPY',
        side: pos.side,
        entryTime: pos.entryTime,
        exitTime: time,
        initialEntryPrice: round2(initial.price),
        scale1Price: scale1 ? round2(scale1.price) : null,
        scale2Price: scale2 ? round2(scale2.price) : null,
        avgEntryPrice: round2(avg),
        exitPrice: round2(fillPrice),
        initialQty: initial.shares,
        scale1Qty: scale1 ? scale1.shares : 0,
        scale2Qty: scale2 ? scale2.shares : 0,
        finalQty: pos.filledShares,
        stopPrice: round2(pos.stopPrice),
        targetPrice: round2(pos.targetPrice),
        exitReason,
        grossPnl: round2(grossPnl),
        commission: round2(totalCommission),
        slippage: round2(totalSlippageCost),
        netPnl: round2(netPnl),
        equityAfter: round2(equity),
        mfePct: round2(pos.mfe),
        maePct: round2(pos.mae),
      };
      trades.push(trade);
      equityCurve.push({ index: idx, time, equity: round2(equity), drawdownPct: round2(drawdownPct), tradeId: pos.tradeId });
      events.push({ index: idx, time, type: 'exit', tradeId: pos.tradeId, reason: exitReason, price: round2(fillPrice), netPnl: round2(netPnl) });
      return trade;
    }

    function checkExit(pos, bar, time, idx) {
      const stopTouched = pos.side === 'long' ? bar.low <= pos.stopPrice : bar.high >= pos.stopPrice;
      const targetTouched = pos.side === 'long' ? bar.high >= pos.targetPrice : bar.low <= pos.targetPrice;
      // Conservative assumption (documented): if both stop and target are touched
      // within the same candle and OHLC data cannot prove intrabar order, assume
      // the stop occurred first.
      if (stopTouched) return closePosition(pos, pos.stopPrice, 'stop', time, idx);
      if (targetTouched) return closePosition(pos, pos.targetPrice, 'target', time, idx);
      // Trend reversal: detected on this bar's completed EMA cross, exits at this bar's close.
      const n = closes.length; // closes array already has this bar's close pushed by the time this runs
      if (n >= 2 && emaFastArr[n - 1] != null && emaSlowArr[n - 1] != null && emaFastArr[n - 2] != null && emaSlowArr[n - 2] != null) {
        const crossedDown = emaFastArr[n - 2] >= emaSlowArr[n - 2] && emaFastArr[n - 1] < emaSlowArr[n - 1];
        const crossedUp = emaFastArr[n - 2] <= emaSlowArr[n - 2] && emaFastArr[n - 1] > emaSlowArr[n - 1];
        if (pos.side === 'long' && crossedDown) return closePosition(pos, bar.close, 'trend_reversal', time, idx);
        if (pos.side === 'short' && crossedUp) return closePosition(pos, bar.close, 'trend_reversal', time, idx);
      }
      return null;
    }

    // Process exactly one new bar. bar = {t, time, open, high, low, close, volume}.
    // Returns a small summary of what happened on this bar.
    function step(bar) {
      barIndex++;
      const idx = barIndex;
      const time = bar.time;

      // 1. Entry on this bar's OPEN if a signal was armed on the prior bar's close.
      if (!position && pendingSignal && pendingSignal.readyIndex === idx) {
        const side = pendingSignal.side;
        const allowed = (side === 'long' && cfg.longEnabled) || (side === 'short' && cfg.shortEnabled);
        if (allowed && !killSwitchActive) {
          const p = openPosition(side, bar.open, time, idx);
          if (p) {
            position = p;
            events.push({ index: idx, time, type: 'entry', tradeId: p.tradeId, side, price: bar.open, shares: p.tranches[0].shares });
          }
        }
        pendingSignal = null;
      }

      // 2. Update indicators using this bar's CLOSE (causal, no look-ahead).
      closes.push(bar.close);
      updateEma(emaFastArr, bar.close, cfg.emaFast);
      updateEma(emaSlowArr, bar.close, cfg.emaSlow);
      const n = closes.length;

      // 3. If a position is open: scale-ins first, then stop/target/reversal.
      if (position) {
        updateExcursion(position, bar);
        tryScaleIn(position, bar, time);
        const closed = checkExit(position, bar, time, idx);
        if (closed) position = null;
      }

      // 4. Detect a fresh signal on this bar's completed candle (arms entry for next bar).
      if (!position && !pendingSignal && n >= 2 && emaFastArr[n - 1] != null && emaSlowArr[n - 1] != null && emaFastArr[n - 2] != null && emaSlowArr[n - 2] != null) {
        const crossedUp = emaFastArr[n - 2] <= emaSlowArr[n - 2] && emaFastArr[n - 1] > emaSlowArr[n - 1];
        const crossedDown = emaFastArr[n - 2] >= emaSlowArr[n - 2] && emaFastArr[n - 1] < emaSlowArr[n - 1];
        if (crossedUp && cfg.longEnabled && !killSwitchActive) {
          pendingSignal = { side: 'long', readyIndex: idx + 1 };
          events.push({ index: idx, time, type: 'signal', side: 'long' });
        } else if (crossedDown && cfg.shortEnabled && !killSwitchActive) {
          pendingSignal = { side: 'short', readyIndex: idx + 1 };
          events.push({ index: idx, time, type: 'signal', side: 'short' });
        }
      }

      return {
        index: idx,
        emaFast: emaFastArr[n - 1],
        emaSlow: emaSlowArr[n - 1],
        position: position ? Object.assign({}, position, { currentAvg: avgEntryPrice(position) }) : null,
        equity: round2(equity),
        killSwitchActive,
      };
    }

    // Force-close any open position at the given bar's close (manual "flatten").
    function flatten(bar, reason) {
      if (!position) return null;
      const t = closePosition(position, bar.close, reason || 'manual_flatten', bar.time, barIndex);
      position = null;
      return t;
    }

    function getState() {
      return {
        barIndex, equity: round2(equity), peakEquity: round2(peakEquity),
        maxDrawdownSeen: round2(maxDrawdownSeen), killSwitchActive,
        position: position ? Object.assign({}, position, { currentAvg: avgEntryPrice(position) }) : null,
        pendingSignal,
        emaFast: emaFastArr[emaFastArr.length - 1], emaSlow: emaSlowArr[emaSlowArr.length - 1],
      };
    }

    return { step, flatten, getState, trades, equityCurve, events, config: cfg };
  }

  // Convenience: run a full backtest over an array of bars in one shot (Node CLI usage).
  function runBacktest(bars, config) {
    const sim = createSimulation(config);
    for (const bar of bars) sim.step(bar);
    // Do not auto-flatten a still-open position at the end: leaving it open and
    // unrealized is more honest than inventing a synthetic exit price. It is
    // reported separately as "openPositionAtEnd" and excluded from trade stats.
    const state = sim.getState();
    return {
      trades: sim.trades,
      equityCurve: sim.equityCurve,
      events: sim.events,
      finalState: state,
      config: sim.config,
      openPositionAtEnd: state.position,
    };
  }

  return { DEFAULT_CONFIG, computeEMA, createSimulation, runBacktest };
});
