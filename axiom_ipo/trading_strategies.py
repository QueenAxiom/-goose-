"""
Trading Strategies & Scalping Module
Integrated trading techniques for IPO opportunity analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class StrategyType(Enum):
    SCALPING = "scalping"
    SCALING = "scaling"
    SWING = "swing_trading"
    POSITION = "position_trading"
    ARBITRAGE = "arbitrage"


@dataclass
class TradingStrategy:
    """Trading strategy with entry/exit rules"""
    name: str
    strategy_type: StrategyType
    description: str
    time_horizon: str
    entry_signals: List[str]
    exit_signals: List[str]
    risk_reward_ratio: str
    best_market_conditions: List[str]
    success_rate_estimate: float


class TradingStrategiesEngine:
    """Evaluates trading strategies for IPO scores"""

    def __init__(self):
        self.strategies = self._load_strategies()

    def _load_strategies(self) -> List[TradingStrategy]:
        """Load trading strategies database"""
        return [
            # SCALPING STRATEGIES
            TradingStrategy(
                name="First-Day Scalping",
                strategy_type=StrategyType.SCALPING,
                description="""Execute multiple small trades during IPO first trading day.
                Entry on opening bell, exit on 3-5% gains. Targets quick momentum.
                High volume, low holding time (minutes to hours).""",
                time_horizon="Minutes to 1-2 hours",
                entry_signals=[
                    "Gap up opening (>5% above offer price)",
                    "Heavy volume surge in first 30 minutes",
                    "Positive first-print momentum",
                    "IPO Trade Score > 70",
                    "Low offer price elasticity (P/S < 5)"
                ],
                exit_signals=[
                    "Target profit hit (3-5% gain)",
                    "Stop loss triggered (-2% from entry)",
                    "Volume spike reversal",
                    "Overhead resistance reached",
                    "First-hour close signal"
                ],
                risk_reward_ratio="1:3 to 1:5",
                best_market_conditions=["hot", "euphoric"],
                success_rate_estimate=0.62
            ),

            TradingStrategy(
                name="Momentum Micro-Trades",
                strategy_type=StrategyType.SCALPING,
                description="""Ride intraday momentum waves using technical levels.
                Targets quick reversals on support/resistance.
                Leverages first-day volatility spikes.""",
                time_horizon="15 minutes to 1 hour",
                entry_signals=[
                    "Price breaks resistance level",
                    "Volume increases 3x 30-day average",
                    "Bullish candlestick patterns form",
                    "First-day open-to-high spread > 10%",
                    "Expected volatility > 40%"
                ],
                exit_signals=[
                    "2-3% profit target hit",
                    "Momentum weakens (volume drops)",
                    "Bearish reversal candle",
                    "Stop loss -1.5% below entry",
                    "Time stop (30 min if no profit)"
                ],
                risk_reward_ratio="1:2 to 1:3",
                best_market_conditions=["hot", "volatile"],
                success_rate_estimate=0.58
            ),

            # SCALING STRATEGIES
            TradingStrategy(
                name="Pyramid Scaling In",
                strategy_type=StrategyType.SCALING,
                description="""Build position over days/weeks as IPO validates.
                Buy more as price confirms uptrend. Reduces risk by averaging in.
                Suits strong fundamentals (Buffett Score 60+).""",
                time_horizon="1-4 weeks",
                entry_signals=[
                    "Buffett Score > 65 (strong fundamentals)",
                    "Stock confirms breakout after IPO day pop",
                    "Price > IPO offer + 15%",
                    "Volume normalizes after first-day spike",
                    "Company posts positive first-month coverage"
                ],
                exit_signals=[
                    "Target price reached (40-50% above offer)",
                    "Fundamental deterioration",
                    "Technical breakdown",
                    "Lock-up expiration risk",
                    "Market rotation out of growth"
                ],
                risk_reward_ratio="1:4 to 1:6",
                best_market_conditions=["warm", "bullish"],
                success_rate_estimate=0.71
            ),

            TradingStrategy(
                name="Dollar-Cost Averaging",
                strategy_type=StrategyType.SCALING,
                description="""Buy fixed dollar amount at regular intervals.
                Removes emotion from entry timing. Works well for quality companies.
                Reduces first-day pop timing risk.""",
                time_horizon="4-12 weeks",
                entry_signals=[
                    "Buffett Score > 60",
                    "Profitable company at IPO",
                    "Revenue > $100M",
                    "Plan to hold 3+ months",
                    "Conviction in long-term thesis"
                ],
                exit_signals=[
                    "3-month hold complete",
                    "Target allocation reached",
                    "Fundamental thesis broken",
                    "Better opportunity identified",
                    "Portfolio rebalancing needed"
                ],
                risk_reward_ratio="1:3 to 1:5",
                best_market_conditions=["warm", "neutral"],
                success_rate_estimate=0.68
            ),

            # SWING TRADING
            TradingStrategy(
                name="Post-IPO Bounce Trade",
                strategy_type=StrategyType.SWING,
                description="""Trade bounces after initial pop exhaustion.
                Buy dips on Day 2-5 pullbacks, sell rallies. Captures mean reversion.
                Targets 10-20% moves over 1-2 weeks.""",
                time_horizon="3-10 days",
                entry_signals=[
                    "Stock pulls back 10-15% from day-one high",
                    "Support level holds on high volume",
                    "RSI oversold (< 35) on 4-hour chart",
                    "Trade Score > 60",
                    "No negative news or lockup event"
                ],
                exit_signals=[
                    "Rally back to prior resistance",
                    "15-20% profit target reached",
                    "Stop loss -5% from entry",
                    "Unexpected earnings/news",
                    "Support breaks on volume"
                ],
                risk_reward_ratio="1:2 to 1:3",
                best_market_conditions=["warm", "volatile"],
                success_rate_estimate=0.59
            ),

            # POSITION TRADING
            TradingStrategy(
                name="Long-Term Value Build",
                strategy_type=StrategyType.POSITION,
                description="""Buy and hold quality IPOs for years.
                Focus on Buffett Score > 70 and business durability.
                Captures multi-year compounding.""",
                time_horizon="3-10 years",
                entry_signals=[
                    "Buffett Score > 75",
                    "Profitable, proven business model",
                    "Company age > 5 years at IPO",
                    "Revenue > $200M, growing >15%",
                    "Management pedigree (Berkshire-backed or equivalent)"
                ],
                exit_signals=[
                    "Target 3-5x return achieved",
                    "Fundamental thesis broken",
                    "Better opportunities found",
                    "Valuation becomes extreme (P/S > 20)",
                    "Portfolio needs rebalancing"
                ],
                risk_reward_ratio="1:5 to 1:10",
                best_market_conditions=["all"],
                success_rate_estimate=0.79
            ),
        ]

    def get_recommended_strategies(self, ipo_trade_score: int, buffett_score: int,
                                   market_conditions: str) -> List[Dict[str, Any]]:
        """Get recommended trading strategies based on IPO scores"""
        recommendations = []

        # Scalping: High trade score, hot market
        if ipo_trade_score > 70 and market_conditions == "hot":
            scalp_strategies = [s for s in self.strategies if s.strategy_type == StrategyType.SCALPING]
            for strategy in scalp_strategies:
                recommendations.append({
                    "strategy": strategy.name,
                    "type": strategy.strategy_type.value,
                    "suitability": "HIGH",
                    "reason": f"Strong IPO momentum (Trade Score {ipo_trade_score}) in hot market conditions",
                    "risk_level": "High",
                    "time_commitment": "Active/frequent monitoring",
                })

        # Scaling: Strong Buffett score
        if buffett_score > 65:
            scaling_strategies = [s for s in self.strategies if s.strategy_type == StrategyType.SCALING]
            for strategy in scaling_strategies:
                recommendations.append({
                    "strategy": strategy.name,
                    "type": strategy.strategy_type.value,
                    "suitability": "MEDIUM-HIGH",
                    "reason": f"Strong fundamentals (Buffett Score {buffett_score}) supports building position",
                    "risk_level": "Medium",
                    "time_commitment": "Moderate (occasional rebalancing)",
                })

        # Swing Trading: Moderate scores, warm market
        if 50 <= ipo_trade_score <= 75 and market_conditions in ["warm", "hot"]:
            swing_strategies = [s for s in self.strategies if s.strategy_type == StrategyType.SWING]
            for strategy in swing_strategies:
                recommendations.append({
                    "strategy": strategy.name,
                    "type": strategy.strategy_type.value,
                    "suitability": "MEDIUM",
                    "reason": "Moderate opportunity with realistic risk/reward",
                    "risk_level": "Medium",
                    "time_commitment": "Moderate",
                })

        # Position Trading: High Buffett score
        if buffett_score > 70:
            position_strategies = [s for s in self.strategies if s.strategy_type == StrategyType.POSITION]
            for strategy in position_strategies:
                recommendations.append({
                    "strategy": strategy.name,
                    "type": strategy.strategy_type.value,
                    "suitability": "MEDIUM-HIGH",
                    "reason": f"Superior long-term quality score ({buffett_score}) justifies buy-and-hold approach",
                    "risk_level": "Low-Medium",
                    "time_commitment": "Minimal (set and forget)",
                })

        return sorted(recommendations, key=lambda x: {"HIGH": 0, "MEDIUM-HIGH": 1, "MEDIUM": 2}.get(x["suitability"], 3))

    def get_strategy_details(self, strategy_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific strategy"""
        strategy = next((s for s in self.strategies if s.name == strategy_name), None)
        if not strategy:
            return {"error": "Strategy not found"}

        return {
            "name": strategy.name,
            "type": strategy.strategy_type.value,
            "description": strategy.description,
            "time_horizon": strategy.time_horizon,
            "entry_signals": strategy.entry_signals,
            "exit_signals": strategy.exit_signals,
            "risk_reward_ratio": strategy.risk_reward_ratio,
            "best_conditions": strategy.best_market_conditions,
            "estimated_success_rate": f"{strategy.success_rate_estimate * 100:.1f}%",
        }


class TradingEducationHub:
    """Public trading education and training materials"""

    EDUCATION_MODULES = {
        "ipo_basics": {
            "title": "IPO Fundamentals",
            "sections": [
                {
                    "title": "What is an IPO?",
                    "content": "An Initial Public Offering (IPO) is when a private company goes public by offering shares to the public for the first time.",
                },
                {
                    "title": "IPO Phases",
                    "content": "Registration → Quiet Period → Pricing → Trading Begins → Lock-up Expiration",
                },
                {
                    "title": "Key Dates",
                    "content": "Offer Date, First Trading Day, Lock-up Expiration (typically 180 days)",
                },
            ],
        },
        "scalping_guide": {
            "title": "IPO Scalping 101",
            "sections": [
                {
                    "title": "What is Scalping?",
                    "content": "Scalping targets quick, small profits (2-5%) from minor price movements. Requires active monitoring and fast execution.",
                },
                {
                    "title": "First-Day Setup",
                    "content": "Monitor offer price day before. Plan entry (gap-up opening?), profit targets (3-5%), stop loss (-2%). Be ready to execute at open.",
                },
                {
                    "title": "Risk Management",
                    "content": "Never risk more than 1-2% of account per trade. Use hard stops. Scale position size based on volatility.",
                },
                {
                    "title": "Tools Needed",
                    "content": "Real-time level 2 quotes, fast broker with low commissions, technical analysis platform, volatility indicators",
                },
            ],
        },
        "scaling_guide": {
            "title": "Position Scaling Strategy",
            "sections": [
                {
                    "title": "What is Scaling?",
                    "content": "Building a position over time by buying at multiple price levels. Reduces average cost and first-day pop risk.",
                },
                {
                    "title": "Pyramid Strategy",
                    "content": "Buy 1/3 at offer price, 1/3 at +15%, 1/3 at +30%. Takes 2-4 weeks. Locks in gains on dips.",
                },
                {
                    "title": "Dollar-Cost Averaging",
                    "content": "Buy same dollar amount every week/month regardless of price. Mathematically reduces cost basis.",
                },
                {
                    "title": "When to Scale In",
                    "content": "Only scale into quality companies (Buffett Score 60+). Avoid scaling into broken fundamentals.",
                },
            ],
        },
        "technical_analysis": {
            "title": "Technical Analysis for IPOs",
            "sections": [
                {
                    "title": "First-Day Patterns",
                    "content": "IPOs often gap up, pull back by midday, then trend. Common pattern: gap > breakout > retest > continuation.",
                },
                {
                    "title": "Key Levels",
                    "content": "Offer price (support), opening price (pivot), first-hour high/low, prior close equivalents",
                },
                {
                    "title": "Volume Signals",
                    "content": "Heavy first-hour volume signals enthusiasm. If volume drops without uptrend, momentum fades.",
                },
                {
                    "title": "Indicators",
                    "content": "RSI (overbought >70 = potential pullback), MACD (trend confirmation), Bollinger Bands (volatility extremes)",
                },
            ],
        },
        "risk_management": {
            "title": "Risk Management Rules",
            "sections": [
                {
                    "title": "The 1-2% Rule",
                    "content": "Never risk more than 1-2% of account on single trade. Protects against catastrophic loss.",
                },
                {
                    "title": "Position Sizing",
                    "content": "Scale size to volatility. High volatility (40%+ expected) = smaller position. Low volatility = normal size.",
                },
                {
                    "title": "Stop Losses",
                    "content": "Always set hard stops. For scalping: -2%. For swing: -5-7%. For position: -10%.",
                },
                {
                    "title": "Lock-Up Expiration Risk",
                    "content": "180 days after IPO, insiders can sell. Often causes 10-20% drop. Reduce position size pre-expiration.",
                },
            ],
        },
        "market_psychology": {
            "title": "IPO Market Psychology",
            "sections": [
                {
                    "title": "First-Day Frenzy",
                    "content": "Hype > reality. IPO-day gains often reverse in week 2. Best plays are quality companies after hype fades.",
                },
                {
                    "title": "FOMO Trading",
                    "content": "Avoid FOMO (Fear of Missing Out) entries at absolute highs. Best entries after 5-10% pullback.",
                },
                {
                    "title": "Retail vs Institutional",
                    "content": "Retail often piles in day 1 (pushing prices up). Institutions buy dips. Play both sides.",
                },
                {
                    "title": "Sector Rotation",
                    "content": "IPO interest rotates: tech cycles, biotech cycles, fintech cycles. Follow the momentum sector.",
                },
            ],
        },
    }

    @classmethod
    def get_module(cls, module_name: str) -> Dict[str, Any]:
        """Get full education module"""
        return cls.EDUCATION_MODULES.get(module_name, {"error": "Module not found"})

    @classmethod
    def list_modules(cls) -> List[str]:
        """List all available education modules"""
        return list(cls.EDUCATION_MODULES.keys())

    @classmethod
    def get_quick_tip(cls) -> str:
        """Get a random trading tip"""
        tips = [
            "IPO hype peaks day 1. Best long-term gains often come after initial enthusiasm fades.",
            "Profitable companies at IPO average +33.6% over 3 years vs -0.5% for unprofitable ones.",
            "Scalping requires speed & discipline. Set targets (3-5%) & stops (-2%) before entering.",
            "Scaling in protects against first-day FOMO. Buy 1/3 at offer, 1/3 at +15%, 1/3 at +30%.",
            "Lock-up expiration (180 days) causes 10-20% drops on average. Reduce size pre-expiration.",
            "Most successful IPO traders focus on quality (Buffett Score 65+) not hype.",
            "Volume is your friend. Heavy volume confirms breakouts. Falling volume warns of reversal.",
            "The best IPO trades often happen 1-2 weeks after debut when hype cools.",
        ]
        import random
        return random.choice(tips)
