"""
Axiom IPO Intelligence Web Application
"""

from flask import Flask, render_template, request, jsonify
from axiom_ipo.scorer import IPOScorer, IPOData

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
