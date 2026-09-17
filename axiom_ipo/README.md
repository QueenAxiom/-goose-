# Axiom IPO Intelligence - Working Prototype

## Overview

**Axiom IPO Intelligence** is a research and decision-support platform that evaluates companies at or around their IPO using only information publicly available at that historical decision point.

The prototype implements the core scoring logic and web interface described in the product brief.

### Core Value Proposition

> "Before you buy an IPO, see what the market excitement isn't telling you."

The platform separates short-horizon IPO trading characteristics (IPO Trade Score) from long-horizon Buffett-style ownership characteristics (Buffett Investment Score), recognizing that IPO-day excitement doesn't predict long-term business quality.

## Architecture

### Components

1. **`scorer.py`** - Core scoring engine
   - `IPOScorer` class implementing both scoring models
   - Historical cohort database
   - Factor-by-factor analysis
   - Risk identification
   - Historical analogue matching

2. **`app.py`** - Flask web application
   - REST API endpoints for scoring
   - Sample IPO data
   - JSON response formatting

3. **`templates/index.html`** - Interactive web interface
   - Input form for IPO data
   - Real-time scoring results
   - Factor visualization
   - Sample IPO buttons for quick testing

## Scoring Models

### IPO Trade Score (0-100)
Evaluates short-horizon trading opportunity/risk around the IPO:
- **Primary drivers:** Market conditions (40%), Valuation (25%), Capital structure (20%), Revenue scale (15%)
- **Focus:** Volatility, attention/speculation, liquidity
- **Historical insight:** Hot markets with high P/S attract traders but underperform long-term

### Buffett Investment Score (0-100)
Evaluates long-horizon ownership quality after IPO excitement:
- **Primary drivers:** Profitability (30%), Company history (25%), Valuation (20%), Revenue scale (15%), Management (10%)
- **Focus:** Business quality, proven track record, reasonable valuation
- **Historical insight:** Profitable companies with scale and reasonable P/S significantly outperformed over 3 years

## Factor Analysis

The system scores seven factors (0-100):

1. **Profitability** - Is the company profitable at IPO? (Weighting: 30% for long-term)
2. **Revenue Scale** - Existing operating revenue ($M) (Weighting: 15% for long-term)
3. **Valuation** - Price-to-Sales multiple (Weighting: 20-25%)
4. **Company History** - Age in years before IPO (Weighting: 25% for long-term)
5. **Management** - Track record, Berkshire backing (Weighting: 10% for long-term)
6. **Capital Structure** - Public float percentage (Weighting: 20% for trading)
7. **Market Conditions** - IPO market environment (Weighting: 40% for trading)

## Historical Evidence

The prototype includes validated historical cohort data:

| Cohort | Count | Day Return | 3-Year Return |
|--------|-------|------------|---------------|
| All IPOs | 9,253 | +18.9% | +19.1% |
| Profitable | 5,327 | +13.3% | +33.6% |
| Unprofitable | 3,926 | +26.5% | -0.5% |
| Profitable + >$100M | 3,064 | +11.6% | +39.9% |
| >$100M + P/S <5 | 3,384 | +8.9% | +41.3% |
| >$100M + P/S >40 | 46 | +93.6% | -44.8% |

**Insight:** The most speculative IPO cohorts produced the weakest long-term results.

## Usage

### Installation

```bash
cd axiom_ipo
pip install -r requirements.txt
```

### Running the Web App

```bash
python run.py
```

The application will start on `http://localhost:5000`

### Quick Test with Sample IPOs

The interface includes pre-loaded sample IPOs for testing:

- **Meta (2012)** - Large, profitable, hot market
- **Snap (2017)** - Unprofitable, extreme valuation, hot market
- **Costco (1983)** - Hypothetical at IPO - excellent fundamentals
- **DexCom (2005)** - Early-stage, unprofitable at IPO (later became strong)

### API Usage

#### Score an IPO

**POST /api/score**

```json
{
  "company_name": "Acme Corp",
  "ipo_date": "2024-01-15",
  "profitable": true,
  "annual_revenue": 250,
  "price_to_sales": 3.5,
  "company_age_years": 8,
  "management_berkshire_history": false,
  "market_conditions": "warm",
  "expected_volatility": "medium",
  "public_float_pct": 22
}
```

**Response:**

```json
{
  "success": true,
  "company_name": "Acme Corp",
  "ipo_date": "2024-01-15",
  "ipo_trade_score": 58,
  "ipo_trade_grade": "Moderate",
  "buffett_score": 72,
  "buffett_grade": "Strong",
  "factors": {
    "profitability_score": 80,
    "revenue_scale_score": 90,
    "valuation_score": 70,
    "company_history_score": 60,
    "management_score": 50,
    "capital_structure_score": 75,
    "market_conditions_score": 60
  },
  "historical_analogue": {
    "name": "Profitable + $100M+ Revenue",
    "historical_3yr_return": 39.9,
    "characteristics": "Strong long-term cohort"
  },
  "summary": "Balanced opportunity with reasonable fundamentals.",
  "risks": ["No evidence of management team being trusted by experienced investors..."]
}
```

## Research Standards

The prototype adheres to the research principles from the brief:

- ✅ **No look-ahead bias** - Uses only information public at the historical decision date
- ✅ **Separates time horizons** - Two distinct models for trading vs. investing
- ✅ **Historical validation** - Scores informed by actual cohort performance data
- ✅ **Preserves losing examples** - Historical data includes unprofitable IPO cohorts
- ✅ **Risk identification** - Flags contradictions and key concerns

## MVP Features Implemented

- ✅ IPO/company lookup and form input
- ✅ Point-in-time data snapshot
- ✅ IPO Trade Score (0-100)
- ✅ Buffett Investment Score (0-100)
- ✅ Factor-by-factor explanation with visualizations
- ✅ Historical analogue/cohort comparison
- ✅ Management provenance flag
- ✅ Risk and contradiction panel
- ✅ Sample IPO buttons for quick testing

## Example Analysis Output

For an unprofitable, high-valuation IPO in a hot market:

```
Axiom Summary
─────────────
High speculative momentum; weak fundamentals for long-term ownership.

IPO Trade Score: 82/100 (High)
Buffett Investment Score: 31/100 (Weak)

Historical Analogue: Extreme Valuation (P/S >40)
Historical 3-Year Return: -44.8%

Key Risks:
• Company is unprofitable; historical unprofitable cohort averaged -0.5% over 3 years
• Extreme valuation limits margin of safety
• IPO launched in hot market; heightened speculation may not persist
```

## Future Enhancements

Potential directions for production development:

1. **Data integrations**
   - Real SEC filing data (Edgar API)
   - Historical stock price data
   - Earnings/revenue validation

2. **Advanced features**
   - Historical replay/backtest view
   - Exportable investor research reports
   - Peer company benchmarking
   - Management team background research

3. **Compliance & commercialization**
   - Jurisdiction-specific legal review
   - Managed accounts functionality (if desired)
   - Personalized investment advice framework
   - Performance tracking and attribution

4. **Refinements**
   - Machine learning optimization of factor weights
   - Real-time IPO pipeline monitoring
   - Sector-specific cohort analysis
   - Out-of-sample factor validation

## License & Attribution

Built as a working prototype for Axiom Enterprises. Research methodology based on:
- Jay R. Ritter / University of Florida IPO datasets
- Berkshire Hathaway published acquisition criteria and principles
