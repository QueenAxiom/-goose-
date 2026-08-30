"""
Axiom IPO Intelligence Scoring Engine
Evaluates IPOs using point-in-time data and historical cohort analysis.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ScoreGrade(Enum):
    EXCELLENT = "Excellent"
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"
    POOR = "Poor"


@dataclass
class IPOData:
    """Company data at IPO decision date"""
    company_name: str
    ipo_date: str
    profitable: bool
    annual_revenue: float  # in millions
    price_to_sales: float
    company_age_years: int
    management_berkshire_history: bool
    market_conditions: str  # "hot", "warm", "cold"
    expected_volatility: str  # "high", "medium", "low"
    public_float_pct: float  # percentage of shares public


@dataclass
class ScoreFactors:
    """Individual factor scores"""
    profitability_score: float
    revenue_scale_score: float
    valuation_score: float
    company_history_score: float
    management_score: float
    capital_structure_score: float
    market_conditions_score: float


@dataclass
class AnalysisResult:
    """Complete scoring result with analysis"""
    company_name: str
    ipo_date: str
    ipo_trade_score: int
    ipo_trade_grade: ScoreGrade
    buffett_score: int
    buffett_grade: ScoreGrade
    factors: ScoreFactors
    historical_analogue: Dict[str, Any]
    summary: str
    risks: list[str]


class IPOScorer:
    """Core scoring engine for Axiom IPO Intelligence"""

    def __init__(self):
        self.historical_cohorts = self._load_historical_data()

    def _load_historical_data(self) -> Dict[str, Any]:
        """Historical IPO return data by cohort"""
        return {
            "all_ipos": {"count": 9253, "day_return": 18.9, "three_year_return": 19.1},
            "profitable": {"count": 5327, "day_return": 13.3, "three_year_return": 33.6},
            "unprofitable": {"count": 3926, "day_return": 26.5, "three_year_return": -0.5},
            "profitable_large": {"count": 3064, "day_return": 11.6, "three_year_return": 39.9},
            "large_cheap": {"count": 3384, "day_return": 8.9, "three_year_return": 41.3},
            "large_expensive": {"count": 46, "day_return": 93.6, "three_year_return": -44.8},
            "company_age": {
                "0_1": {"return": 5.34},
                "2_4": {"return": 15.69},
                "5_9": {"return": 28.47},
                "10_19": {"return": 40.74},
                "20_plus": {"return": 91.81},
            }
        }

    def score_ipo(self, data: IPOData) -> AnalysisResult:
        """Generate complete IPO analysis and scores"""

        factors = self._calculate_factors(data)
        ipo_trade_score = self._calculate_ipo_trade_score(data, factors)
        buffett_score = self._calculate_buffett_score(data, factors)

        historical_analogue = self._find_historical_analogue(data)
        summary = self._generate_summary(data, ipo_trade_score, buffett_score)
        risks = self._identify_risks(data, factors)

        return AnalysisResult(
            company_name=data.company_name,
            ipo_date=data.ipo_date,
            ipo_trade_score=ipo_trade_score,
            ipo_trade_grade=self._score_to_grade(ipo_trade_score),
            buffett_score=buffett_score,
            buffett_grade=self._score_to_grade(buffett_score),
            factors=factors,
            historical_analogue=historical_analogue,
            summary=summary,
            risks=risks
        )

    def _calculate_factors(self, data: IPOData) -> ScoreFactors:
        """Calculate individual factor scores (0-100)"""

        # Profitability: profitable companies score higher for long-term
        profitability_score = 80 if data.profitable else 30

        # Revenue scale: larger revenue bases are more stable
        if data.annual_revenue >= 500:
            revenue_scale_score = 90
        elif data.annual_revenue >= 100:
            revenue_scale_score = 75
        elif data.annual_revenue >= 50:
            revenue_scale_score = 60
        elif data.annual_revenue >= 10:
            revenue_scale_score = 45
        else:
            revenue_scale_score = 25

        # Valuation: lower P/S is better for long-term, but extreme P/S gets trade points
        if data.price_to_sales < 2:
            valuation_score = 85
        elif data.price_to_sales < 5:
            valuation_score = 70
        elif data.price_to_sales < 20:
            valuation_score = 45
        elif data.price_to_sales < 40:
            valuation_score = 25
        else:
            valuation_score = 10

        # Company history: older businesses have more proven track records
        company_history_score = self._score_company_age(data.company_age_years)

        # Management: Berkshire backing is a positive signal
        management_score = 85 if data.management_berkshire_history else 50

        # Capital structure: higher float is better for liquidity
        if data.public_float_pct >= 25:
            capital_structure_score = 75
        else:
            capital_structure_score = 50

        # Market conditions: hot markets inflate short-term returns
        if data.market_conditions == "hot":
            market_conditions_score = 85  # good for trade, not for investment
        elif data.market_conditions == "warm":
            market_conditions_score = 60
        else:
            market_conditions_score = 35

        return ScoreFactors(
            profitability_score=profitability_score,
            revenue_scale_score=revenue_scale_score,
            valuation_score=valuation_score,
            company_history_score=company_history_score,
            management_score=management_score,
            capital_structure_score=capital_structure_score,
            market_conditions_score=market_conditions_score
        )

    def _score_company_age(self, years: int) -> float:
        """Score based on company history at IPO"""
        if years < 1:
            return 15
        elif years < 2:
            return 25
        elif years < 5:
            return 40
        elif years < 10:
            return 60
        elif years < 20:
            return 80
        else:
            return 95

    def _calculate_ipo_trade_score(self, data: IPOData, factors: ScoreFactors) -> int:
        """Score for short-horizon trading opportunity (0-100)"""
        # IPO trade score focuses on volatility, attention, momentum

        # Market conditions and volatility are primary drivers
        trade_score = (
            factors.market_conditions_score * 0.40 +  # hot market = higher score
            factors.valuation_score * 0.25 +  # extreme P/S attracts traders
            factors.capital_structure_score * 0.20 +  # liquidity matters
            factors.revenue_scale_score * 0.15  # larger revenue base = more stable
        )

        # Volatility adjustment
        if data.expected_volatility == "high":
            trade_score = min(100, trade_score * 1.1)
        elif data.expected_volatility == "low":
            trade_score = max(0, trade_score * 0.85)

        return int(trade_score)

    def _calculate_buffett_score(self, data: IPOData, factors: ScoreFactors) -> int:
        """Score for long-horizon investment quality (0-100)"""
        # Buffett score focuses on quality, valuation, track record

        buffett_score = (
            factors.profitability_score * 0.30 +  # profitability is paramount
            factors.company_history_score * 0.25 +  # proven track record
            factors.valuation_score * 0.20 +  # reasonable entry price
            factors.revenue_scale_score * 0.15 +  # meaningful scale
            factors.management_score * 0.10  # trusted management
        )

        return int(buffett_score)

    def _find_historical_analogue(self, data: IPOData) -> Dict[str, Any]:
        """Find most similar historical cohort"""

        cohorts = []

        # Check profitability + revenue
        if data.profitable and data.annual_revenue >= 100:
            cohorts.append({
                "name": "Profitable + $100M+ Revenue",
                "historical_3yr_return": 39.9,
                "characteristics": "Strong long-term cohort"
            })
        elif not data.profitable:
            cohorts.append({
                "name": "Unprofitable at IPO",
                "historical_3yr_return": -0.5,
                "characteristics": "Weak long-term cohort"
            })

        # Check valuation
        if data.price_to_sales < 5 and data.annual_revenue >= 100:
            cohorts.append({
                "name": "Large Cap + P/S <5",
                "historical_3yr_return": 41.3,
                "characteristics": "Excellent historical returns"
            })
        elif data.price_to_sales > 40:
            cohorts.append({
                "name": "Extreme Valuation (P/S >40)",
                "historical_3yr_return": -44.8,
                "characteristics": "Poor long-term cohort"
            })

        # Best analogue
        best = max(cohorts, key=lambda x: x["historical_3yr_return"]) if cohorts else {
            "name": "All IPOs Average",
            "historical_3yr_return": 19.1,
            "characteristics": "Market average"
        }

        return best

    def _score_to_grade(self, score: int) -> ScoreGrade:
        """Convert numeric score to letter grade"""
        if score >= 80:
            return ScoreGrade.EXCELLENT
        elif score >= 65:
            return ScoreGrade.STRONG
        elif score >= 50:
            return ScoreGrade.MODERATE
        elif score >= 35:
            return ScoreGrade.WEAK
        else:
            return ScoreGrade.POOR

    def _generate_summary(self, data: IPOData, trade_score: int, buffett_score: int) -> str:
        """Generate plain-English summary of analysis"""

        if trade_score > 75 and buffett_score > 75:
            return "Strong candidate for both short-term trading and long-term ownership."
        elif trade_score > 75 and buffett_score <= 50:
            return "High speculative momentum; weak fundamentals for long-term ownership."
        elif trade_score <= 50 and buffett_score > 75:
            return "Limited short-term excitement; strong candidate for patient capital."
        elif trade_score > 60 and buffett_score > 60:
            return "Balanced opportunity with reasonable fundamentals."
        else:
            return "Limited opportunity for both trading and long-term investment at current valuation."

    def _identify_risks(self, data: IPOData, factors: ScoreFactors) -> list[str]:
        """Identify key risks and contradictions"""

        risks = []

        # Profitability risk
        if not data.profitable:
            risks.append("Company is unprofitable at IPO; historical unprofitable cohort averaged -0.5% over 3 years")

        # Valuation risk
        if data.price_to_sales > 40:
            risks.append(f"Extreme valuation (P/S {data.price_to_sales}); historical extreme-valuation cohort averaged -44.8% over 3 years")
        elif data.price_to_sales > 20:
            risks.append(f"High valuation multiple (P/S {data.price_to_sales}) limits margin of safety")

        # Revenue scale risk
        if data.annual_revenue < 10:
            risks.append("Limited revenue scale; unproven ability to sustain or grow operations at scale")

        # Company history risk
        if data.company_age_years < 2:
            risks.append("Very early-stage company at IPO; limited operating history to evaluate")

        # Market timing risk
        if data.market_conditions == "hot":
            risks.append("IPO launched in hot market; heightened speculative demand may not persist")

        # Management risk
        if not data.management_berkshire_history:
            risks.append("No evidence of management team being trusted by experienced investors (e.g., Berkshire)")

        return risks
