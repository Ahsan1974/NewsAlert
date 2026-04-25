

import re
import cloudscraper
from bs4 import BeautifulSoup

from config import (
    HEADERS,
    REQUEST_TIMEOUT,
    MAX_NEWS_ROWS
)

FOREX_NEWS_URL = "https://www.forexfactory.com/news"


def clean_text(value):
    return value.strip() if value else ""


def fetch_page():
    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False
        }
    )

    response = scraper.get(
        FOREX_NEWS_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()
    return response.text


def detect_sentiment(text):
    t = text.upper()

    bullish_words = [
        "WAR", "MISSILE", "ATTACK", "TENSION",
        "SANCTION", "RECESSION", "RISK OFF",
        "RATE CUT", "LOWER YIELDS", "WEAK DOLLAR",
        "IRAN"
    ]

    bearish_words = [
        "HAWKISH", "RATE HIKE", "STRONG DOLLAR",
        "HIGHER YIELDS", "STRONG JOBS",
        "HOT CPI", "INFLATION SURGE"
    ]

    for word in bullish_words:
        if word in t:
            return "GOLD BULLISH"

    for word in bearish_words:
        if word in t:
            return "GOLD BEARISH"

    return "NEUTRAL"


def detect_impact(title, section):
    t = title.upper()
    score = 0

    if "BREAKING" in section or "HOT" in section:
        score += 3
    elif "LATEST" in section:
        score += 1

    high_words = [
        "FED", "POWELL", "CPI", "NFP", "INFLATION",
        "TRUMP", "IRAN", "WAR", "ECB", "RATE",
        "RECESSION", "YIELDS", "SANCTIONS"
    ]

    medium_words = [
        "PMI", "GDP", "RETAIL", "SENTIMENT",
        "WEEKLY", "FORECAST", "SALES"
    ]

    for w in high_words:
        if w in t:
            score += 3

    for w in medium_words:
        if w in t:
            score += 1

    if score >= 5:
        return "🔴 HIGH"
    elif score >= 2:
        return "🟡 MEDIUM"
    else:
        return "⚪ LOW"


def valid_title(title):
    if len(title) < 25:
        return False

    bad_starts = [
        "from ",
        "login",
        "register"
    ]

    for b in bad_starts:
        if title.lower().startswith(b):
            return False

    return True


def extract_age(text):
    """
    Detect:
    2 hr ago
    2 hr 17 min ago
    35 min ago
    1 day ago
    """

    text = text.lower()

    patterns = [
        r"\d+\s*hr\s*\d+\s*min\s*ago",
        r"\d+\s*hr\s*ago",
        r"\d+\s*min\s*ago",
        r"\d+\s*day[s]?\s*ago"
    ]

    for p in patterns:
        match = re.search(p, text)
        if match:
            return match.group(0)

    return "Fresh"


def parse_news_cards(soup):
    news_list = []
    used = set()

    # Search larger content blocks instead of only links
    cards = soup.find_all(["li", "div", "article"])

    for card in cards:

        full_text = clean_text(
            card.get_text(" ", strip=True)
        )

        if len(full_text) < 40:
            continue

        link = card.find("a", href=True)

        if not link:
            continue

        title = clean_text(
            link.get_text(" ", strip=True)
        )

        if not valid_title(title):
            continue

        if title in used:
            continue

        used.add(title)

        href = link["href"]

        if href.startswith("/"):
            url = "https://www.forexfactory.com" + href
        else:
            url = href

        age = extract_age(full_text)

        # Optional source detection
        source = "ForexFactory"

        source_match = re.search(
            r"from\s+([a-zA-Z0-9@._-]+)",
            full_text,
            re.IGNORECASE
        )

        if source_match:
            source = source_match.group(1)

        section = "LATEST STORIES"

        sentiment = detect_sentiment(title)
        impact = detect_impact(title, section)

        news_list.append({
            "section": section,
            "title": title,
            "source": source,
            "age": age,
            "url": url,
            "impact": impact,
            "sentiment": sentiment,
            "raw": title
        })

    return news_list[:MAX_NEWS_ROWS]


def get_news():
    try:
        html = fetch_page()

        soup = BeautifulSoup(html, "lxml")

        news_list = parse_news_cards(soup)

        if not news_list:
            news_list.append({
                "section": "-",
                "title": "Connected but no news found",
                "source": "ForexFactory",
                "age": "-",
                "url": "",
                "impact": "⚪ LOW",
                "sentiment": "NEUTRAL",
                "raw": "Connected but no news found"
            })

        return news_list

    except Exception as e:
        return [{
            "section": "-",
            "title": f"Error fetching news: {str(e)}",
            "source": "ForexFactory",
            "age": "-",
            "url": "",
            "impact": "⚪ LOW",
            "sentiment": "NEUTRAL",
            "raw": f"Error fetching news: {str(e)}"
        }]