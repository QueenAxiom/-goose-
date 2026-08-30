"""
Axiom IPO Intelligence Web Application
"""

from flask import Flask, render_template, request, jsonify
from axiom_ipo.scorer import IPOScorer, IPOData
from axiom_ipo.historical_data import HISTORICAL_IPOS, get_historical_ipo, get_all_symbols, get_cohort_stats

app = Flask(__name__)
scorer = IPOScorer()

# Sample IPO data for testing
SAMPLE_IPOS = {
    "meta": {
        "company_name": "Meta Platforms (then Facebook)",
        "ipo_date": "2012-05-18",
        "profitable": True,
        "annual_revenue": 3709,  # millions
        "price_to_sales": 11.2,
        "company_age_years": 8,
        "management_berkshire_history": False,
        "market_conditions": "warm",
        "expected_volatility": "high",
        "public_float_pct": 16.5
    },
    "snapchat": {
        "company_name": "Snap Inc.",
        "ipo_date": "2017-03-02",
        "profitable": False,
        "annual_revenue": 404,
        "price_to_sales": 44.8,
        "company_age_years": 4,
        "management_berkshire_history": False,
        "market_conditions": "hot",
        "expected_volatility": "high",
        "public_float_pct": 20.0
    },
    "costco": {
        "company_name": "Costco Wholesale (hypothetical at IPO 1983)",
        "ipo_date": "1983-09-26",
        "profitable": True,
        "annual_revenue": 124,
        "price_to_sales": 2.1,
        "company_age_years": 2,
        "management_berkshire_history": False,
        "market_conditions": "warm",
        "expected_volatility": "low",
        "public_float_pct": 22.0
    },
    "dexcom": {
        "company_name": "DexCom Inc.",
        "ipo_date": "2005-04-06",
        "profitable": False,
        "annual_revenue": 25,
        "price_to_sales": 8.4,
        "company_age_years": 5,
        "management_berkshire_history": False,
        "market_conditions": "warm",
        "expected_volatility": "medium",
        "public_float_pct": 24.0
    },
}


@app.route("/")
def index():
    """Home page with interactive scorer"""
    return render_template("index.html", sample_ipo_keys=list(SAMPLE_IPOS.keys()))


@app.route("/api/score", methods=["POST"])
def api_score():
    """Score an IPO and return analysis"""
    data = request.get_json()

    try:
        ipo_data = IPOData(
            company_name=data.get("company_name", "Unknown"),
            ipo_date=data.get("ipo_date", ""),
            profitable=data.get("profitable", False),
            annual_revenue=float(data.get("annual_revenue", 0)),
            price_to_sales=float(data.get("price_to_sales", 1)),
            company_age_years=int(data.get("company_age_years", 0)),
            management_berkshire_history=data.get("management_berkshire_history", False),
            market_conditions=data.get("market_conditions", "warm"),
            expected_volatility=data.get("expected_volatility", "medium"),
            public_float_pct=float(data.get("public_float_pct", 20))
        )

        result = scorer.score_ipo(ipo_data)

        return jsonify({
            "success": True,
            "company_name": result.company_name,
            "ipo_date": result.ipo_date,
            "ipo_trade_score": result.ipo_trade_score,
            "ipo_trade_grade": result.ipo_trade_grade.value,
            "buffett_score": result.buffett_score,
            "buffett_grade": result.buffett_grade.value,
            "factors": {
                "profitability_score": result.factors.profitability_score,
                "revenue_scale_score": result.factors.revenue_scale_score,
                "valuation_score": result.factors.valuation_score,
                "company_history_score": result.factors.company_history_score,
                "management_score": result.factors.management_score,
                "capital_structure_score": result.factors.capital_structure_score,
                "market_conditions_score": result.factors.market_conditions_score,
            },
            "historical_analogue": result.historical_analogue,
            "summary": result.summary,
            "risks": result.risks
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/sample/<ipo_key>", methods=["GET"])
def api_sample(ipo_key):
    """Get sample IPO data"""
    if ipo_key not in SAMPLE_IPOS:
        return jsonify({"error": "Unknown sample"}), 404

    return jsonify(SAMPLE_IPOS[ipo_key])


@app.route("/api/score-sample/<ipo_key>", methods=["GET"])
def api_score_sample(ipo_key):
    """Score a sample IPO"""
    if ipo_key not in SAMPLE_IPOS:
        return jsonify({"error": "Unknown sample"}), 404

    data = SAMPLE_IPOS[ipo_key]
    return api_score_from_dict(data)


def api_score_from_dict(data):
    """Helper to score from dict"""
    try:
        ipo_data = IPOData(
            company_name=data.get("company_name", "Unknown"),
            ipo_date=data.get("ipo_date", ""),
            profitable=data.get("profitable", False),
            annual_revenue=float(data.get("annual_revenue", 0)),
            price_to_sales=float(data.get("price_to_sales", 1)),
            company_age_years=int(data.get("company_age_years", 0)),
            management_berkshire_history=data.get("management_berkshire_history", False),
            market_conditions=data.get("market_conditions", "warm"),
            expected_volatility=data.get("expected_volatility", "medium"),
            public_float_pct=float(data.get("public_float_pct", 20))
        )

        result = scorer.score_ipo(ipo_data)

        return jsonify({
            "success": True,
            "company_name": result.company_name,
            "ipo_date": result.ipo_date,
            "ipo_trade_score": result.ipo_trade_score,
            "ipo_trade_grade": result.ipo_trade_grade.value,
            "buffett_score": result.buffett_score,
            "buffett_grade": result.buffett_grade.value,
            "factors": {
                "profitability_score": result.factors.profitability_score,
                "revenue_scale_score": result.factors.revenue_scale_score,
                "valuation_score": result.factors.valuation_score,
                "company_history_score": result.factors.company_history_score,
                "management_score": result.factors.management_score,
                "capital_structure_score": result.factors.capital_structure_score,
                "market_conditions_score": result.factors.market_conditions_score,
            },
            "historical_analogue": result.historical_analogue,
            "summary": result.summary,
            "risks": result.risks
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/backtest/all", methods=["GET"])
def api_backtest_all():
    """Run backtest on all historical IPOs"""
    results = []
    win_count = 0

    for ipo in HISTORICAL_IPOS:
        backtest_result = scorer.backtest_historical_ipo(ipo)
        results.append({
            "symbol": backtest_result.ipo_symbol,
            "company_name": backtest_result.ipo_name,
            "predicted_buffett_score": backtest_result.predicted_buffett,
            "predicted_trade_score": backtest_result.predicted_trade,
            "actual_3yr_return": round(backtest_result.actual_3yr_return, 2),
            "first_day_return": round(backtest_result.first_day_return, 2),
            "correct_prediction": backtest_result.correct_call
        })
        if backtest_result.correct_call:
            win_count += 1

    # Calculate accuracy metrics
    buffett_scores = [r["predicted_buffett_score"] for r in results]
    actual_returns = [r["actual_3yr_return"] for r in results]

    # Simple correlation: higher score should mean higher return
    correlation = calculate_correlation(buffett_scores, actual_returns)

    accuracy = (win_count / len(results) * 100) if results else 0

    return jsonify({
        "success": True,
        "total_backtests": len(HISTORICAL_IPOS),
        "correct_predictions": win_count,
        "accuracy_pct": round(accuracy, 1),
        "correlation_buffett_vs_return": round(correlation, 3),
        "avg_actual_3yr_return": round(sum(actual_returns) / len(actual_returns), 2),
        "best_performer": max(results, key=lambda x: x["actual_3yr_return"]),
        "worst_performer": min(results, key=lambda x: x["actual_3yr_return"]),
        "results": sorted(results, key=lambda x: x["correct_prediction"], reverse=True)
    })


@app.route("/api/backtest/<symbol>", methods=["GET"])
def api_backtest_single(symbol):
    """Backtest a specific historical IPO"""
    ipo = get_historical_ipo(symbol)
    if not ipo:
        return jsonify({"error": "IPO not found"}), 404

    backtest_result = scorer.backtest_historical_ipo(ipo)

    return jsonify({
        "success": True,
        "symbol": backtest_result.ipo_symbol,
        "company_name": backtest_result.ipo_name,
        "ipo_date": ipo.ipo_date,
        "predicted_buffett_score": backtest_result.predicted_buffett,
        "predicted_trade_score": backtest_result.predicted_trade,
        "prediction_call": "GOOD LONG-TERM" if backtest_result.predicted_buffett >= 60 else "CAUTION/TRADE",
        "actual_first_day_return": backtest_result.first_day_return,
        "actual_3yr_return": backtest_result.actual_3yr_return,
        "prediction_correct": backtest_result.correct_call,
        "company_age_at_ipo": ipo.company_age_years,
        "profitable_at_ipo": ipo.profitable_at_ipo,
        "price_to_sales": ipo.price_to_sales,
        "annual_revenue": ipo.annual_revenue_m,
        "notes": ipo.notes,
        "interpretation": generate_interpretation(backtest_result, ipo)
    })


@app.route("/api/backtest/symbols", methods=["GET"])
def api_backtest_symbols():
    """List all available historical IPOs for backtesting"""
    return jsonify({
        "symbols": get_all_symbols(),
        "total": len(HISTORICAL_IPOS),
        "stats": get_cohort_stats()
    })


@app.route("/backtest", methods=["GET"])
def backtest_page():
    """Backtest results page"""
    return render_template("backtest.html", symbols=get_all_symbols())


def calculate_correlation(x, y):
    """Simple Pearson correlation coefficient"""
    n = len(x)
    if n < 2:
        return 0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    denominator_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5

    if denominator_x == 0 or denominator_y == 0:
        return 0

    return numerator / (denominator_x * denominator_y)


def generate_interpretation(backtest_result, ipo):
    """Generate human-readable interpretation of backtest results"""
    buffett = backtest_result.predicted_buffett
    actual = backtest_result.actual_3yr_return
    first_day = backtest_result.first_day_return

    if backtest_result.correct_call:
        if buffett >= 60:
            return f"✅ Axiom Predicted Success: Buffett score {buffett}/100 suggested good long-term hold. Actual 3-year return: {actual:.1f}%."
        else:
            return f"✅ Axiom Predicted Caution: Buffett score {buffett}/100 suggested weak fundamentals. Actual 3-year return: {actual:.1f}% confirmed concerns."
    else:
        if buffett >= 60:
            return f"❌ Missed Upside: Buffett score {buffett}/100 seemed attractive but IPO underperformed ({actual:.1f}% return). {ipo.notes}"
        else:
            return f"❌ False Warning: Buffett score {buffett}/100 seemed concerning but IPO outperformed ({actual:.1f}% return). {ipo.notes}"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
