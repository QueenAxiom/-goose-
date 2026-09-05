// Axiom Trading Bot - "Buffett" systematic proxy engine.
// Long-only, buy-and-hold, no leverage, no shorting, no stop-loss. Deploys an
// initial stake, then keeps a cash reserve to add on drawdowns from the
// trailing all-time high, ratcheting to deeper bands as a decline worsens
// (a systematic, honestly-mechanical stand-in for "buy more when others are
// fearful" - not real fundamental analysis, since this engine only ever sees
// price, not a business).
// Bar-by-bar, causal only (no look-ahead). Shared between the Node CLI runner
// and the browser replay UI, same pattern as engine.js.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.BuffettEngine = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {

  const DEFAULT_CONFIG = {
    startingEquity: 100000,
    initialDeployPct: 50,   // % of starting equity deployed on day 1
    dipBandPct: 10,         // band width: each additional 10% below the trailing ATH is a new buy trigger
    dipAddPct: 10,          // % of STARTING equity deployed per band crossed
    slippagePct: 0.01,      // % per fill
    commissionPerFill: 0,   // $ flat per fill
    collectDividends: false, // if true, credit real historical dividend payments to cash as they're paid
    dividends: [],           // [{date, amountPerShare}] - required when collectDividends is true
  };

  function round2(x) { return Math.round(x * 100) / 100; }

  const PERSONA_LINES = {
    initial: "Opening stake. Time in the market, not timing it - the rest of the cash stays ready for when it's needed.",
    band1: "First real pullback. This is exactly the kind of dip a patient buyer waits for - adding here, not panicking.",
    band2: "Deeper now. Prices this far below the highs are a gift for anyone still holding cash, not a reason to run.",
    band3: "This is a real correction. Others are fearful - that's precisely the setup a disciplined buyer wants.",
    band4: "A genuine crisis-level drawdown. Uncomfortable, but this is when the best long-term prices get made.",
    band5: "Extreme dislocation. Deploying further reserves on the view that this washes out, as it always has.",
    bandN: "Another leg down, another tranche. Staying mechanical about it rather than guessing the exact bottom.",
    newATH: "New high-water mark. No selling - the plan was never to time an exit, just to keep buying weakness.",
  };

  function personaLine(bandIndex) {
    if (bandIndex === 1) return PERSONA_LINES.band1;
    if (bandIndex === 2) return PERSONA_LINES.band2;
    if (bandIndex === 3) return PERSONA_LINES.band3;
    if (bandIndex === 4) return PERSONA_LINES.band4;
    if (bandIndex >= 5) return PERSONA_LINES.band5;
    return PERSONA_LINES.bandN;
  }

  function createSimulation(config) {
    const cfg = Object.assign({}, DEFAULT_CONFIG, config || {});
    const dividendByDate = new Map((cfg.dividends || []).map(d => [d.date, d.amountPerShare]));
    let totalDividendsCollected = 0;

    let cash = cfg.startingEquity;
    let shares = 0;
    let costBasis = 0; // cumulative $ actually spent (for avg cost reporting)
    let ath = -Infinity;
    let deepestBandFilled = 0; // ratchets up as price makes new lows since the last ATH; resets on a new ATH
    let peakEquity = cfg.startingEquity;
    let maxDrawdownPct = 0;
    let buyCounter = 0;
    let barIndex = -1;
    let initialDeployed = false;
    let pendingBuy = null; // { kind, band, readyIndex } - fills on bar[readyIndex].open

    const buys = [];        // every buy event (initial + dip adds)
    const dividendPayments = []; // every dividend credit event, if collectDividends is on
    const equityCurve = [];  // mark-to-market every bar: {index, date, equity, cash, shares, drawdownPct}
    const events = [];

    function fillPrice(rawPrice) {
      return rawPrice * (1 + cfg.slippagePct / 100); // buying only, always pay up on slippage
    }

    function executeBuy(kind, band, rawPrice, date, idx, athAtTrigger, drawdownPctAtTrigger) {
      const dollarBudget = kind === 'initial'
        ? cfg.startingEquity * (cfg.initialDeployPct / 100)
        : cfg.startingEquity * (cfg.dipAddPct / 100);
      const budget = Math.min(dollarBudget, cash);
      if (budget <= cfg.commissionPerFill) return null; // not enough cash to bother
      const px = fillPrice(rawPrice);
      const spendable = budget - cfg.commissionPerFill;
      const qty = Math.floor(spendable / px);
      if (qty <= 0) return null;
      const cost = qty * px + cfg.commissionPerFill;
      cash -= cost;
      shares += qty;
      costBasis += cost;
      buyCounter++;
      const buy = {
        buyId: 'B' + String(buyCounter).padStart(3, '0'),
        kind, band: band || 0,
        date, price: round2(px), shares: qty, cost: round2(cost),
        cashRemainingAfter: round2(cash), sharesAfter: shares,
        avgCostAfter: round2(costBasis / shares),
        athAtTrigger: athAtTrigger != null ? round2(athAtTrigger) : null,
        drawdownPctAtTrigger: drawdownPctAtTrigger != null ? round2(drawdownPctAtTrigger) : null,
        commentary: kind === 'initial' ? PERSONA_LINES.initial : personaLine(band),
      };
      buys.push(buy);
      events.push({ index: idx, date, type: 'buy', buyId: buy.buyId, kind, price: buy.price, shares: qty });
      return buy;
    }

    function step(bar) {
      barIndex++;
      const idx = barIndex;
      const date = bar.time;

      // 0. Credit any dividend payable on this date, using shares held BEFORE
      //    today's buy fills (you must have held the shares going into the
      //    ex-dividend date to receive the payment).
      if (cfg.collectDividends && shares > 0) {
        const perShare = dividendByDate.get(date);
        if (perShare) {
          const amount = round2(perShare * shares);
          cash += amount;
          totalDividendsCollected += amount;
          const payment = { date, perShare, shares, amount };
          dividendPayments.push(payment);
          events.push({ index: idx, date, type: 'dividend', amount, perShare, shares });
        }
      }

      // 1. Execute any buy armed on the previous bar's close, at THIS bar's open.
      if (pendingBuy && pendingBuy.readyIndex === idx) {
        executeBuy(pendingBuy.kind, pendingBuy.band, bar.open, date, idx, pendingBuy.athAtTrigger, pendingBuy.drawdownPctAtTrigger);
        pendingBuy = null;
      }

      // 2. Arm the one-time initial deployment on bar 0 (fills on bar 1's open).
      if (!initialDeployed) {
        initialDeployed = true;
        if (idx + 1 < Infinity) pendingBuy = { kind: 'initial', band: 0, readyIndex: idx + 1 };
      }

      // 3. Update trailing all-time-high using this bar's completed close (causal).
      const priorAth = ath;
      if (bar.close > ath) {
        ath = bar.close;
        if (deepestBandFilled > 0) events.push({ index: idx, date, type: 'new_ath', price: bar.close, commentary: PERSONA_LINES.newATH });
        deepestBandFilled = 0; // a fresh high resets the drawdown ladder
      }

      // 4. Detect how many dip-bands below the (now-updated) ATH this close sits at,
      //    and arm the next-bar-open buy for the deepest NEW band reached.
      if (isFinite(ath) && ath > 0) {
        const drawdownPct = ((ath - bar.close) / ath) * 100;
        const bandReached = Math.floor(drawdownPct / cfg.dipBandPct);
        if (bandReached > deepestBandFilled && !pendingBuy) {
          deepestBandFilled = bandReached;
          pendingBuy = { kind: 'dip', band: bandReached, readyIndex: idx + 1, athAtTrigger: ath, drawdownPctAtTrigger: drawdownPct };
        }
      }

      // 5. Mark-to-market equity every bar.
      const equity = cash + shares * bar.close;
      peakEquity = Math.max(peakEquity, equity);
      const ddPct = peakEquity > 0 ? ((peakEquity - equity) / peakEquity) * 100 : 0;
      maxDrawdownPct = Math.max(maxDrawdownPct, ddPct);
      equityCurve.push({ index: idx, date, equity: round2(equity), cash: round2(cash), shares, close: bar.close, drawdownPct: round2(ddPct) });

      return { index: idx, equity: round2(equity), cash: round2(cash), shares, ath: isFinite(ath) ? round2(ath) : null };
    }

    function getState() {
      const lastEq = equityCurve.length ? equityCurve[equityCurve.length - 1].equity : cfg.startingEquity;
      return {
        barIndex, equity: round2(lastEq), cash: round2(cash), shares,
        avgCost: shares > 0 ? round2(costBasis / shares) : 0,
        ath: isFinite(ath) ? round2(ath) : null,
        maxDrawdownPct: round2(maxDrawdownPct),
        deployedPct: round2(((cfg.startingEquity - cash) / cfg.startingEquity) * 100),
        totalDividendsCollected: round2(totalDividendsCollected),
      };
    }

    return { step, getState, buys, dividendPayments, equityCurve, events, config: cfg };
  }

  function runBacktest(bars, config) {
    const sim = createSimulation(config);
    for (const bar of bars) sim.step(bar);
    return {
      buys: sim.buys, dividendPayments: sim.dividendPayments, equityCurve: sim.equityCurve,
      events: sim.events, finalState: sim.getState(), config: sim.config,
    };
  }

  // Baseline comparison: 100% deployed on day 1, pure lump-sum buy-and-hold, no dip adds.
  // Pass `dividends` to make this a fair comparison against the dividend-collecting variant:
  // the same real dividend cash accrues here too (held as idle cash, no reserve strategy to
  // deploy it), isolating the dip-buying ladder's true edge from "dividends help everyone."
  function runLumpSumBaseline(bars, startingEquity, slippagePct, commissionPerFill, dividends) {
    const px = bars[1] ? bars[1].open : bars[0].open; // same next-bar-open entry convention
    const fillPx = px * (1 + slippagePct / 100);
    const spendable = startingEquity - commissionPerFill;
    const qty = Math.floor(spendable / fillPx);
    let cash = startingEquity - (qty * fillPx + commissionPerFill);
    const dividendByDate = new Map((dividends || []).map(d => [d.date, d.amountPerShare]));
    let totalDividendsCollected = 0;
    const curve = bars.map((b, i) => {
      const perShare = dividendByDate.get(b.time);
      if (perShare && qty > 0) { const amt = perShare * qty; cash += amt; totalDividendsCollected += amt; }
      const equity = cash + qty * b.close;
      return { index: i, date: b.time, equity: round2(equity) };
    });
    let peak = startingEquity, maxDd = 0;
    for (const p of curve) { peak = Math.max(peak, p.equity); maxDd = Math.max(maxDd, ((peak - p.equity) / peak) * 100); }
    return {
      shares: qty, entryPrice: round2(fillPx), equityCurve: curve, maxDrawdownPct: round2(maxDd),
      finalEquity: curve[curve.length - 1].equity, totalDividendsCollected: round2(totalDividendsCollected),
    };
  }

  return { DEFAULT_CONFIG, createSimulation, runBacktest, runLumpSumBaseline, PERSONA_LINES };
});
