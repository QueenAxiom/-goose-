# AXIOM TRADING BOT — HISTORICAL REPLAY LAB — FINAL REPORT

**Instrument**: SPY
**Data period**: 2026-05-29 09:30 → 2026-08-24 15:05 (America/New_York), ~87 calendar days / ~60 trading days
**Timeframe**: 5-minute bars (4,670 bars)
**Data source**: Yahoo Finance chart API (query1.finance.yahoo.com/v8/finance/chart/SPY, interval=5m)

## Primary result — Test A (long + short, scaling enabled)

| | |
|---|---|
| Starting equity | $100,000.00 |
| Ending equity | $93,466.30 |
| Net P&L | -$6,533.70 |
| Return | -6.53% |
| Trades | 180 (90 long, 90 short) |
| Win rate | 24.44% (44W / 136L) |
| Avg winning trade | $954.92 |
| Avg losing trade | -$356.99 |
| Profit factor | 0.87 |
| Max drawdown | 11.30% |
| Sharpe (per-trade, unannualized) | -0.06 |
| Largest winner / loser | $1,118.17 / -$1,071.44 |
| Avg trade duration | 381.6 min (~6.4 hours) |
| Scale-ins filled | 160 |
| % reached target | 21.67% |
| % stopped out | 31.11% |
| % exited by trend reversal | 47.22% |
| Kill switch (20% DD) triggered | No |

## All five configurations

| Test | Description | Trades | Win Rate | Net P&L | Return | Profit Factor | Max DD |
|---|---|---|---|---|---|---|---|
| A | Long + Short, scaling ON | 180 | 24.44% | -$6,533.70 | -6.53% | 0.87 | 11.30% |
| B | Long only, scaling ON | 90 | 16.67% | -$12,275.34 | -12.28% | 0.50 | 12.65% |
| C | Short only, scaling ON | 90 | 32.22% | +$6,531.53 | +6.53% | 1.27 | 2.64% |
| D | Long + Short, scaling OFF | 180 | 30.56% | -$6,772.77 | -6.77% | 0.80 | 9.94% |
| E | Long + Short, scaling ON (duplicate of A per spec) | 180 | 24.44% | -$6,533.70 | -6.53% | 0.87 | 11.30% |

## Assessment

**Poor to mediocre over this sample, and direction-dependent.** The long side
was the whole problem: Test B (long-only) lost 12.3% with a 0.50 profit
factor — the worst result of the five. Test C (short-only) was the only
profitable configuration, +6.5% with a 1.27 profit factor and a much shallower
2.6% drawdown, which mostly just reflects that SPY chopped/drifted rather than
trending cleanly upward during this window — a pure EMA-crossover scalp with
a 2:1 target:stop (0.44%/0.22%) caught more whipsaw on the long side than on
the short side. Combined long+short (Test A) roughly nets the two out to a
small loss. Turning scaling off (Test D) barely moved the needle (-6.77% vs
-6.53%) and actually raised the raw win rate (30.6% vs 24.4%) while leaving
profit factor about the same — the scale-in tranches aren't what's driving the
losses, the long-side signal quality is. Win rate under 25-30% across the
board is being propped up by a favorable win/loss size ratio (roughly 2.7:1
avg-win-to-avg-loss on Test A), which is structurally expected from a 2:1
target:stop, but it's not enough to overcome how often the long side gets
stopped or reversed out.

**Bottom line**: this specific parameter set is not tradeable as-is on the
long side over this sample. The short-side result is promising enough to be
worth isolating and testing over a longer/different period before drawing
real conclusions — 60 trading days and 90 short trades is a thin sample.
Nothing here should be read as validated edge; it's evidence for where to dig
next (test long/short asymmetry over more regimes, and re-examine whether a
fixed-from-initial-entry stop, rather than a trailing one, is leaving edge on
the table on the reversal exits, which account for 47% of all exits).

## Documented assumptions (see README.md for full detail)

- Stop-vs-target same-candle ambiguity resolved conservatively: stop assumed first.
- Trend-reversal exits fill at the confirming candle's close (spec only specifies "next open" for entries).
- Max drawdown kill switch defaulted to 20% (not specified in the brief); configurable.
- Kill switch halts new entries only; an open position is left to its own stop/target/reversal, not force-flattened.
- Scale-in tranches are not separately risk-budgeted — only the initial 50% tranche sizes off the 0.35% risk formula, per the spec's literal wording ("maximum theoretical loss from the initial position").
- A position still open at the end of the dataset is excluded from trade stats (`openPositionAtEnd`), not force-closed.
