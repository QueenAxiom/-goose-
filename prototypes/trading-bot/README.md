# Axiom Trading Bot — Historical Replay Lab

Two working historical-data backtests for SPY, both simulation only — no
brokerage connection, no real orders. Built in Node.js (no Python available
on this machine; both engines are plain, dependency-free JavaScript).

1. **Scalping Lab** (`ui/index.html`) — EMA 9/21 crossover, long+short,
   scaling, 5-minute bars. See the sections below.
2. **Value Lab** (`ui/buffett.html`) — a long-only, buy-and-hold, no-leverage
   "Buffett" systematic proxy on 25 years of daily SPY. See
   `results/buffett/REPORT.md` for the full writeup. Summary: **+589.92%
   return / 8.04% CAGR** over 2001–2026, beating a plain lump-sum buy-and-hold
   by +42.8 points — but it's a price-only technical proxy for a "buy fear"
   posture, not real fundamental analysis (the engine never sees a business,
   only a price series), and its one-time cash reserve ran out during the
   2008 crisis, leaving nothing left to buy the 2020 or 2022 drawdowns. Full
   assumptions and the real finding are in the report.

## What's here

```
data/
  spy_5m_raw.json      raw Yahoo Finance 5m chart-API response, as downloaded (preserved)
  spy_5m.csv            cleaned 5-minute OHLCV, used by the scalping lab
  spy_1d_raw.json       raw Yahoo Finance daily chart-API response, as downloaded (preserved)
  spy_1d.csv             cleaned daily OHLCV (2001-2026), used by the value lab
src/
  engine.js             scalping engine (indicators, signals, sizing, scaling, exits, equity)
  buffett-engine.js      value engine (buy-and-hold, drawdown-band dip buys, mark-to-market equity)
  data-loader.js         CSV -> bar objects (both 5m and daily)
  stats.js               scalping trade log -> performance dashboard
  buffett-stats.js       value engine buys/equity -> performance dashboard + baseline comparison
scripts/
  build-dataset.js       raw 5m JSON -> clean CSV
  build-daily-dataset.js raw daily JSON -> clean CSV
  run-backtests.js       runs scalping Tests A-E, writes results/
  run-buffett-backtest.js runs the value lab, writes results/buffett/
  build-ui.js             generates ui/index.html (scalping lab, self-contained)
  build-buffett-ui.js     generates ui/buffett.html (value lab, self-contained)
results/
  testA .. testE/        trade_log.csv, equity_curve.csv, dashboard.json, events.json, config.json per test
  buffett/                REPORT.md, buys_log.csv, equity_curve.csv, dashboard.json, config.json
  comparison.md / .json  side-by-side test comparison
ui/
  index.html             interactive replay UI - open directly in a browser, no server needed
```

## Data

- **Source**: Yahoo Finance chart API (`query1.finance.yahoo.com/v8/finance/chart/SPY`), `interval=5m`.
- **Range used**: 2026-05-29 09:30 through 2026-08-24 15:05, America/New_York — 4,670 bars.
- Two bars were dropped: one with null OHLC fields, one trailing partial/live candle
  (irregular timestamp, zero volume — the still-forming "current" bar at fetch time).
- The fetch window sits entirely within EDT (no DST transition), so a single fixed
  UTC offset from the API's `meta.gmtoffset` is valid for the whole dataset.
- No synthetic or fabricated prices anywhere in the dataset.
- To re-fetch and rebuild: re-run the curl command documented at the top of
  `scripts/build-dataset.js`'s companion fetch (see below), then `node scripts/build-dataset.js`.

Reproduce the fetch:
```
curl "https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=5m&range=60d&includePrePost=false" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36" \
  -o data/spy_5m_raw.json
node scripts/build-dataset.js
```
(Yahoo returned ~87 calendar days of 5m history at fetch time, more than the
nominal 60-day cap — used as-is.)

## Strategy

EMA 9 / EMA 21 crossover, both long and short, entering on the next candle's
open after a completed-candle cross (never the same bar the cross is detected
on — no look-ahead).

**Sizing**: risk-budget based. The initial (50%) tranche is sized so that if
price reaches the stop (0.22% from the initial entry reference), the loss on
*that tranche alone* equals 0.35% of current equity. The two scale-in tranches
(25% + 25%) fill on top of that as price moves 0.11% / 0.22% further in the
trade's favor, using the same total share count — they are size add-ons, not
separately risk-budgeted. **Consequence worth flagging**: because the stop/
target stay pinned to the *initial* entry price rather than the average price,
a fully-scaled position carries more than 0.35% of equity at risk if it
reverses all the way back to the stop, and the risk-budget formula for a 0.22%
stop against 100k equity implies real notional exposure well above 1x equity
(SPY at ~$757, ~$100k account -> ~$318k notional at full size, roughly
3x leverage). This is the literal, mechanical consequence of the parameters
given in the spec, not a bug — flagging it here rather than unilaterally
resizing it down.

**Exits**, checked in this order every bar a position is open: scale-ins first,
then stop, then target, then trend-reversal (EMA re-cross). If a single candle's
high/low would touch both the stop and the target, the conservative assumption
is used: **the stop is treated as having happened first**, since OHLC data
alone cannot prove intrabar sequencing. Trend-reversal exits use that bar's
close (the reversal is only confirmed once the candle completes, same as
entries — but unlike entries there's no "next candle" instruction for exits
in the spec, so the exit is taken immediately at the confirming candle's close
rather than waiting a further bar).

**Kill switch**: default max drawdown 20% (not specified in the brief — chosen
as a reasonable default, exposed as a configurable parameter in both the CLI
config and the UI). Once tripped, no new positions are opened; a position
already open at that point is left to hit its own stop/target/reversal rather
than being force-flattened at an arbitrary price.

**Costs**: slippage 0.01% per side (applied to every fill: initial, both
scale-ins, and the exit), commission $0/fill by default. Both configurable.

**Gross vs. net P&L in the trade log**: Gross P&L is computed off the
*theoretical* (unslipped) entry/exit price levels — it's what the strategy's
signal logic would have produced in a frictionless market. Slippage and
commission are then itemized separately and subtracted to get Net P&L.

## Anti-look-ahead

- Indicators are calculated causally — bar `i`'s EMA only ever uses closes
  `<= i`.
- A cross is only actable on the *next* bar's open, never the bar it's
  detected on.
- Scale-in and exit checks each bar use only that bar's own OHLC.
- A position still open on the last bar of the dataset is left open and
  excluded from the trade log / dashboard stats (`openPositionAtEnd: true`)
  rather than force-closed with a synthetic exit.

## Running it

```
node scripts/build-dataset.js     # only needed if data/spy_5m_raw.json changes
node scripts/run-backtests.js     # runs Tests A-E, writes results/
node scripts/build-ui.js          # regenerates ui/index.html
```

Then open `ui/index.html` directly in a browser (no server required — the
engine, the full 4,670-bar dataset, and the UI are all inlined into one file).
Controls: Play / Pause / Step / Reset / Flatten, speed 0.5x-10x, and a live
parameter panel (Apply & Reset re-runs the simulation from bar 0 with the new
parameters). The chart shows candles, EMA 9 (blue) / EMA 21 (amber), entry
markers (green=long/cover, red=short), scale-in markers (purple), exit
markers, and the active stop/target lines while a trade is open.

**Testing note**: browser automation was unavailable in this environment when
this UI was built (sandboxed out by this session's tooling policy), so it was
verified statically — JS syntax-checked cleanly, and the state/render logic
was read through line-by-line, including one real bug caught and fixed this
way (`getState()` wasn't attaching `currentAvg` to the position object, which
would have shown NaN in the position P&L readout). It has not been visually
confirmed running in an actual browser — open it and sanity-check before
relying on it.

## Reproducibility

Every test run's `results/test*/config.json` records the exact parameter set,
data source, date range, and bar count used, so any result can be reproduced
by re-running `run-backtests.js` against the same `data/spy_5m.csv`.
