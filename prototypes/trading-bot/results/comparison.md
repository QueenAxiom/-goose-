# Backtest Comparison — SPY 5m, 2026-05-29T09:30:00.000 to 2026-08-24T15:05:00.000

| Test | Description | Trades | Win Rate | Net P&L | Return | Profit Factor | Max DD | Long | Short | Scale-ins |
|---|---|---|---|---|---|---|---|---|---|---|
| A | Long + Short enabled, scaling enabled | 180 | 24.44% | $-6533.7 | -6.53% | 0.87 | 11.3% | 90 | 90 | 160 |
| B | Long only, scaling enabled | 90 | 16.67% | $-12275.34 | -12.28% | 0.5 | 12.65% | 90 | 0 | 67 |
| C | Short only, scaling enabled | 90 | 32.22% | $6531.53 | 6.53% | 1.27 | 2.64% | 0 | 90 | 93 |
| D | Long + Short enabled, scaling DISABLED | 180 | 30.56% | $-6772.77 | -6.77% | 0.8 | 9.94% | 90 | 90 | 0 |
| E | Long + Short enabled, scaling enabled (duplicate of A, listed separately per spec) | 180 | 24.44% | $-6533.7 | -6.53% | 0.87 | 11.3% | 90 | 90 | 160 |
