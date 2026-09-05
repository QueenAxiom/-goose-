# AXIOM TRADING BOT — "BUFFETT" SYSTEMATIC PROXY — FINAL REPORT

**Instrument**: SPY
**Data period**: 2001-08-27 → 2026-08-21 (24.98 years, 6,283 daily bars)
**Data source**: Yahoo Finance chart API (query1.finance.yahoo.com/v8/finance/chart/SPY, interval=1d, events=div)
**Strategy**: long-only, buy-and-hold, no leverage, no shorting, no stop-loss. Initial stake deployed
day one; remaining cash reserved and deployed in tranches as price falls into progressively deeper
10%-wide bands below its trailing all-time high, ratcheting back to zero on every new high.

## What this is (and isn't)

This is a **systematic, price-only proxy** for a Buffett-style posture — patient, long-only, no
leverage, "be greedy when others are fearful" expressed mechanically as buying deeper drawdown
bands. It is explicitly **not** real fundamental analysis: the engine never sees earnings, moats,
management quality, or intrinsic value, because none of that is in an OHLCV feed. Read the results
as "what a disciplined, cash-reserving, never-sell buy-and-hold posture would have done on SPY,"
not as "what Warren Buffett would have done."

## Two variants, same posture

The first pass (below as "without dividends") assumed the account's cash reserve was a one-time,
never-replenished pool — the biggest limitation flagged in that run: the reserve ran dry during the
2008 crisis and had nothing left for 2020 or 2022. The obvious next question is whether real
"winnings" — SPY's actual dividend payments, collected as cash rather than reinvested via a
synthetic adjusted price — would have kept the reserve funded. **They would have, substantially.**
This uses SPY's real historical dividend payment history (101 payments, 2001–2026, from the same
Yahoo Finance feed), not an assumed yield.

| | Without dividends | With dividends (real payments) |
|---|---|---|
| Ending equity | $689,915.84 | **$986,884.62** |
| Total return | +589.92% | **+886.88%** |
| CAGR | 8.04% | **9.60%** |
| Max drawdown | 55.21% | **52.35%** (lower — idle cash cushions the equity curve) |
| Total buys | 8 | **17** |
| Dividends collected | $0 (not modeled) | **$108,313.18** |
| Cash remaining at end | 0% | **27.44%** (~$270k still in reserve) |

**Difference: +$296,968.78, or +296.96 percentage points of return, from doing nothing more than
letting real dividend income refill the reserve instead of ignoring it.**

### Isolating the real edge (fair baseline)

That +296.96-point figure mixes two effects: dividends help *any* SPY holder, not just this
strategy. To isolate what the dip-buying ladder itself is worth, the baseline needs to collect the
same real dividends too — a lump-sum buy-and-hold that gets the same income but never buys a dip:

| | Dip-buying ladder (with dividends) | Fair baseline (lump-sum, same dividends, no ladder) |
|---|---|---|
| Return | +886.88% | +631.65% |
| Dividends collected | $108,313.18 | $84,573.52 (fewer shares held on average, so less income) |

**The ladder's true edge, once both sides get the same dividend income, is +255.23 percentage
points** — still a large, genuine edge from buying real drawdowns, just not inflated by dividends
that a passive holder would have gotten anyway.

## What the extra cash actually bought

With dividends flowing in, the ladder caught crises the original run couldn't reach:

- **2015** (-11%), **2018** (two separate corrections, Feb and Dec, bands 1–2)
- **2020 COVID crash**: band 1 on Feb 28, then **band 3 (-32%) on March 23, 2020 — essentially the
  exact bottom of that crash**
- **2022 bear market**: bands 1 and 2 (-10%, -21.5%)
- **2025**: another band-1 dip in March

None of these fired in the original (no-dividend) run — the reserve was already at $2.14 by October
2008 and stayed there. This is the direct, empirical answer to "could he have taken some of his
winnings and put that back in and still been ahead": **yes — dividend income alone, with no new
outside contributions, was enough to keep buying real crises for another 17 years, and it ended up
ahead by a wide margin, with a shallower drawdown, not just a bigger one.**

## Assessment

**Meaningfully better than the original proxy, and closer to how a real long-term holder actually
behaves.** The core finding from the first pass still holds directionally — a genuinely *static*
account can run out of dry powder — but that first pass understated the strategy by ignoring the
one source of "new money" every SPY holder actually gets without selling anything: dividends. Feed
that back in, and the reserve survives three more real crises and ends the period with over a
quarter of the account still in cash, ready for whatever's next.

**Bottom line**: buying fear beat not buying fear in both variants, but the dividend-funded version
is the more honest picture of what continuous reinvestment of real income — not market-timing
skill — actually buys a patient, cash-disciplined investor over 25 years.

## Documented assumptions

- **Dividend crediting**: real historical per-share payments (source: Yahoo's `events=div` field on
  the same SPY feed) are credited as cash on the payment date, based on shares held going into that
  date (must have owned the shares before the ex-dividend date to receive the payment). No dividend
  reinvestment plan (DRIP) auto-buying is modeled — the cash simply joins the reserve and is
  available for the next dip-band trigger, same mechanism as the original cash pool.
- **Trade prices remain real, unadjusted OHLC** — not Yahoo's back-adjusted `adjclose` series —
  so a real historical dollar price is what gets traded. Total return still comes from the actual
  dividend cash amounts, not a synthetic adjustment.
- No new contributions are ever added beyond dividends actually paid on shares already held — this
  still isn't modeling a saver with ongoing outside income, just a more complete picture of what the
  position itself throws off.
- No selling, ever, at any point — by design (buy-and-hold), not a bug.
- The account never re-levers or borrows against the position — no margin, matching "no leverage."
- The most recent daily bar (2026-08-24, mid-session at fetch time) was dropped as an
  incomplete/uncommitted candle, same look-ahead-avoidance rule used throughout this project. Price
  data ends 2026-08-21.
- Slippage 0.01%/fill, $0 commission/fill — same defaults as the scalping lab, both configurable.

## Files

- `results/buffett/no-dividends/` — original variant: `buys_log.csv`, `equity_curve.csv`, `dashboard.json`, `config.json`
- `results/buffett/with-dividends/` — dividend-funded variant: same files plus `dividend_payments.csv` (all 101 real payments credited)
- `results/buffett/comparison.json` — both dashboards side by side
- `data/spy_dividends.csv` — the raw dividend history used, preserved as-fetched
