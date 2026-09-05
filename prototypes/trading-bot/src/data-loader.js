const fs = require('fs');

// Loads the clean OHLCV CSV into an array of bar objects consumable by the engine.
function loadBars(csvPath) {
  const text = fs.readFileSync(csvPath, 'utf8').trim();
  const lines = text.split('\n');
  const bars = [];
  for (let i = 1; i < lines.length; i++) {
    const [epoch, utc, local, open, high, low, close, volume] = lines[i].split(',');
    bars.push({
      t: Number(epoch),
      time: local, // exchange-local ISO time, used as the canonical display/log time
      utc,
      open: Number(open), high: Number(high), low: Number(low), close: Number(close),
      volume: Number(volume),
    });
  }
  return bars;
}

// Loads the clean daily OHLCV CSV (date, not intraday time) into bar objects.
function loadDailyBars(csvPath) {
  const text = fs.readFileSync(csvPath, 'utf8').trim();
  const lines = text.split('\n');
  const bars = [];
  for (let i = 1; i < lines.length; i++) {
    const [epoch, date, open, high, low, close, volume] = lines[i].split(',');
    bars.push({
      t: Number(epoch),
      time: date, // calendar date string, used as the canonical display/log time
      open: Number(open), high: Number(high), low: Number(low), close: Number(close),
      volume: Number(volume),
    });
  }
  return bars;
}

// Loads real historical dividend payments (date, amountPerShare).
function loadDividends(csvPath) {
  const text = fs.readFileSync(csvPath, 'utf8').trim();
  const lines = text.split('\n');
  const divs = [];
  for (let i = 1; i < lines.length; i++) {
    const [date, amountPerShare] = lines[i].split(',');
    divs.push({ date, amountPerShare: Number(amountPerShare) });
  }
  return divs;
}

module.exports = { loadBars, loadDailyBars, loadDividends };
