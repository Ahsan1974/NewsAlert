


"""
News impact engine
XAUUSD focused logic
"""

from config import XAUUSD_KEYWORDS


def safe_float(value):
    """
    Convert text like 0.4% -> 0.4
    """
    try:
        return float(
            value.replace("%", "")
                 .replace(",", "")
                 .strip()
        )
    except:
        return None


def is_xauusd_related(text):
    """
    Filter only gold relevant news
    """
    text = text.upper()
    return any(keyword in text for keyword in XAUUSD_KEYWORDS)


def analyze_news(item):
    """
    Analyze structured news item
    item = {
        time, currency, event, actual, forecast, previous, raw
    }
    """

    text = item["raw"].upper()
    currency = item["currency"].upper()

    actual = safe_float(item["actual"])
    forecast = safe_float(item["forecast"])

    result = {
        "impact": "LOW",
        "affects": [],
        "gold_bias": "NEUTRAL",
        "action": "SAFE TO TRADE"
    }

    # -----------------------------
    # EXTREME EVENTS
    # -----------------------------
    if "NFP" in text or "NON-FARM" in text:
        result["impact"] = "EXTREME"
        result["affects"] = ["USD", "XAUUSD", "EURUSD", "GBPUSD"]
        result["gold_bias"] = "HIGH VOLATILITY"
        result["action"] = "AVOID TRADE"

    elif "FOMC" in text or "INTEREST RATE" in text or "RATE DECISION" in text:
        result["impact"] = "EXTREME"
        result["affects"] = ["USD", "XAUUSD", "ALL MARKETS"]
        result["gold_bias"] = "STRONG VOLATILITY"
        result["action"] = "AVOID TRADE"

    elif "POWELL" in text or "FED" in text:
        result["impact"] = "EXTREME"
        result["affects"] = ["USD", "XAUUSD"]
        result["gold_bias"] = "VOLATILE"
        result["action"] = "AVOID TRADE"

    # -----------------------------
    # CPI / INFLATION LOGIC
    # -----------------------------
    elif "CPI" in text or "INFLATION" in text or "PCE" in text:
        result["impact"] = "VERY HIGH"
        result["affects"] = [currency, "XAUUSD"]
        result["action"] = "CAUTION"

        if currency == "USD":
            if actual is not None and forecast is not None:
                if actual > forecast:
                    result["gold_bias"] = "GOLD BEARISH"
                elif actual < forecast:
                    result["gold_bias"] = "GOLD BULLISH"
                else:
                    result["gold_bias"] = "NEUTRAL"
            else:
                result["gold_bias"] = "VOLATILE"

        else:
            result["gold_bias"] = "WATCH USD REACTION"

    # -----------------------------
    # GDP
    # -----------------------------
    elif "GDP" in text:
        result["impact"] = "HIGH"
        result["affects"] = [currency]
        result["gold_bias"] = "MEDIUM IMPACT"
        result["action"] = "WATCH"

    # -----------------------------
    # JOBLESS / UNEMPLOYMENT
    # -----------------------------
    elif "JOBLESS" in text or "UNEMPLOYMENT" in text:
        result["impact"] = "HIGH"
        result["affects"] = [currency, "XAUUSD"]
        result["gold_bias"] = "VOLATILE"
        result["action"] = "CAUTION"

    # -----------------------------
    # PPI
    # -----------------------------
    elif "PPI" in text:
        result["impact"] = "MEDIUM"
        result["affects"] = [currency]
        result["gold_bias"] = "MILD"
        result["action"] = "WATCH"

    # -----------------------------
    # CENTRAL BANK SPEECHES
    # -----------------------------
    elif "LAGARDE" in text or "SPEAKS" in text:
        result["impact"] = "HIGH"
        result["affects"] = [currency]
        result["gold_bias"] = "VOLATILE"
        result["action"] = "CAUTION"

    return result