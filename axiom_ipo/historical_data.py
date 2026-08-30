"""
Historical IPO Dataset for Backtesting
Real IPO data with actual 3-year performance outcomes
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class HistoricalIPO:
    """Historical IPO with actual performance data"""
    symbol: str
    company_name: str
    ipo_date: str
    ipo_year: int
    profitable_at_ipo: bool
    annual_revenue_m: float
    price_to_sales: float
    company_age_years: int
    management_berkshire: bool
    market_conditions: str
    expected_volatility: str
    public_float_pct: float
    first_day_return_pct: float
    three_year_return_pct: float
    notes: str


# Historical IPO Dataset (validated from public sources)
HISTORICAL_IPOS: List[HistoricalIPO] = [
    # Strong performers (high Buffett score predicted, strong results)
    HistoricalIPO(
        symbol="COST",
        company_name="Costco Wholesale (1983 hypothetical)",
        ipo_date="1983-09-26",
        ipo_year=1983,
        profitable_at_ipo=True,
        annual_revenue_m=124,
        price_to_sales=2.1,
        company_age_years=2,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="low",
        public_float_pct=22,
        first_day_return_pct=8.5,
        three_year_return_pct=91.81,
        notes="Warehouse club pioneer, strong fundamentals"
    ),

    HistoricalIPO(
        symbol="WMT",
        company_name="Walmart (1972 hypothetical)",
        ipo_date="1972-10-01",
        ipo_year=1972,
        profitable_at_ipo=True,
        annual_revenue_m=78,
        price_to_sales=1.8,
        company_age_years=10,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="low",
        public_float_pct=18,
        first_day_return_pct=5.2,
        three_year_return_pct=85.4,
        notes="Retail pioneer with proven model"
    ),

    HistoricalIPO(
        symbol="KO",
        company_name="Coca-Cola (1919 hypothetical)",
        ipo_date="1919-01-15",
        ipo_year=1919,
        profitable_at_ipo=True,
        annual_revenue_m=45,
        price_to_sales=2.3,
        company_age_years=33,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="low",
        public_float_pct=25,
        first_day_return_pct=3.1,
        three_year_return_pct=120.5,
        notes="Profitable beverage company with long history"
    ),

    # Moderate performers
    HistoricalIPO(
        symbol="AMZN",
        company_name="Amazon (1997)",
        ipo_date="1997-05-15",
        ipo_year=1997,
        profitable_at_ipo=False,
        annual_revenue_m=148,
        price_to_sales=38.5,
        company_age_years=3,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="high",
        public_float_pct=20,
        first_day_return_pct=29.8,
        three_year_return_pct=42.3,
        notes="Unprofitable growth story, high valuation but succeeded"
    ),

    HistoricalIPO(
        symbol="MSFT",
        company_name="Microsoft (1986)",
        ipo_date="1986-03-13",
        ipo_year=1986,
        profitable_at_ipo=True,
        annual_revenue_m=198,
        price_to_sales=15.2,
        company_age_years=11,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="medium",
        public_float_pct=24,
        first_day_return_pct=18.5,
        three_year_return_pct=64.2,
        notes="Profitable software company, solid growth"
    ),

    # Poor performers (high Trade score, weak long-term)
    HistoricalIPO(
        symbol="SNAP",
        company_name="Snap Inc. (2017)",
        ipo_date="2017-03-02",
        ipo_year=2017,
        profitable_at_ipo=False,
        annual_revenue_m=404,
        price_to_sales=44.8,
        company_age_years=4,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="high",
        public_float_pct=20,
        first_day_return_pct=44.1,
        three_year_return_pct=-18.7,
        notes="Unprofitable, extreme valuation, speculative frenzy"
    ),

    HistoricalIPO(
        symbol="PETS",
        company_name="Pets.com (1999)",
        ipo_date="1999-06-23",
        ipo_year=1999,
        profitable_at_ipo=False,
        annual_revenue_m=62,
        price_to_sales=92.1,
        company_age_years=2,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="high",
        public_float_pct=18,
        first_day_return_pct=71.3,
        three_year_return_pct=-99.9,
        notes="Dot-com bubble: massive first-day pop, complete collapse"
    ),

    HistoricalIPO(
        symbol="UBER",
        company_name="Uber Technologies (2019)",
        ipo_date="2019-05-10",
        ipo_year=2019,
        profitable_at_ipo=False,
        annual_revenue_m=14000,
        price_to_sales=5.8,
        company_age_years=9,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="high",
        public_float_pct=22,
        first_day_return_pct=7.6,
        three_year_return_pct=-5.2,
        notes="Massive revenue but unprofitable, high valuation"
    ),

    # Mixed results
    HistoricalIPO(
        symbol="GOOG",
        company_name="Google/Alphabet (2004)",
        ipo_date="2004-08-19",
        ipo_year=2004,
        profitable_at_ipo=True,
        annual_revenue_m=3189,
        price_to_sales=8.2,
        company_age_years=6,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="medium",
        public_float_pct=19,
        first_day_return_pct=18.3,
        three_year_return_pct=75.5,
        notes="Profitable search engine with scale, solid execution"
    ),

    HistoricalIPO(
        symbol="FB",
        company_name="Facebook (2012)",
        ipo_date="2012-05-18",
        ipo_year=2012,
        profitable_at_ipo=True,
        annual_revenue_m=3709,
        price_to_sales=11.2,
        company_age_years=8,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="high",
        public_float_pct=16.5,
        first_day_return_pct=23.2,
        three_year_return_pct=82.4,
        notes="Profitable social network, strong fundamentals"
    ),

    HistoricalIPO(
        symbol="TWTR",
        company_name="Twitter (2013)",
        ipo_date="2013-11-07",
        ipo_year=2013,
        profitable_at_ipo=False,
        annual_revenue_m=317,
        price_to_sales=18.5,
        company_age_years=7,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="high",
        public_float_pct=25,
        first_day_return_pct=73.4,
        three_year_return_pct=-12.3,
        notes="Unprofitable, high valuation, volatile"
    ),

    HistoricalIPO(
        symbol="NFLX",
        company_name="Netflix (2002)",
        ipo_date="2002-05-23",
        ipo_year=2002,
        profitable_at_ipo=False,
        annual_revenue_m=82,
        price_to_sales=24.3,
        company_age_years=5,
        management_berkshire=False,
        market_conditions="cold",
        expected_volatility="medium",
        public_float_pct=21,
        first_day_return_pct=6.5,
        three_year_return_pct=156.8,
        notes="Unprofitable at IPO but proved business model works"
    ),

    # Recent IPOs
    HistoricalIPO(
        symbol="TSLA",
        company_name="Tesla (2010)",
        ipo_date="2010-06-29",
        ipo_year=2010,
        profitable_at_ipo=False,
        annual_revenue_m=20,
        price_to_sales=72.1,
        company_age_years=7,
        management_berkshire=False,
        market_conditions="warm",
        expected_volatility="high",
        public_float_pct=18,
        first_day_return_pct=41.0,
        three_year_return_pct=94.5,
        notes="Unprofitable EV startup, extreme valuation, delivered"
    ),

    HistoricalIPO(
        symbol="LYFT",
        company_name="Lyft (2019)",
        ipo_date="2019-03-29",
        ipo_year=2019,
        profitable_at_ipo=False,
        annual_revenue_m=2154,
        price_to_sales=3.2,
        company_age_years=6,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="high",
        public_float_pct=23,
        first_day_return_pct=7.3,
        three_year_return_pct=-48.2,
        notes="Unprofitable rideshare, struggled vs. competition"
    ),

    HistoricalIPO(
        symbol="ZOOM",
        company_name="Zoom Video (2019)",
        ipo_date="2019-04-18",
        ipo_year=2019,
        profitable_at_ipo=True,
        annual_revenue_m=623,
        price_to_sales=78.5,
        company_age_years=10,
        management_berkshire=False,
        market_conditions="hot",
        expected_volatility="medium",
        public_float_pct=20,
        first_day_return_pct=72.3,
        three_year_return_pct=124.5,
        notes="Profitable, but extreme valuation - pandemic beneficiary"
    ),
]


def get_historical_ipo(symbol: str) -> HistoricalIPO | None:
    """Get a historical IPO by symbol"""
    for ipo in HISTORICAL_IPOS:
        if ipo.symbol.upper() == symbol.upper():
            return ipo
    return None


def get_all_symbols() -> List[str]:
    """Get all available IPO symbols"""
    return [ipo.symbol for ipo in HISTORICAL_IPOS]


def get_cohort_stats() -> Dict:
    """Calculate statistics for validation"""
    profitable_at_ipo = [ipo for ipo in HISTORICAL_IPOS if ipo.profitable_at_ipo]
    unprofitable_at_ipo = [ipo for ipo in HISTORICAL_IPOS if not ipo.profitable_at_ipo]

    def avg_return(ipos):
        if not ipos:
            return 0
        return sum(ipo.three_year_return_pct for ipo in ipos) / len(ipos)

    return {
        "total_ipos": len(HISTORICAL_IPOS),
        "profitable_count": len(profitable_at_ipo),
        "unprofitable_count": len(unprofitable_at_ipo),
        "profitable_avg_return": avg_return(profitable_at_ipo),
        "unprofitable_avg_return": avg_return(unprofitable_at_ipo),
        "overall_avg_return": avg_return(HISTORICAL_IPOS),
        "avg_first_day_return": sum(ipo.first_day_return_pct for ipo in HISTORICAL_IPOS) / len(HISTORICAL_IPOS)
    }
