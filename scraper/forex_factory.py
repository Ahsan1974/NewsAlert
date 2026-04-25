
import requests
import urllib3
from bs4 import BeautifulSoup

from config import (
    FOREX_FACTORY_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    MAX_NEWS_ROWS
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VALID_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY",
    "AUD", "CAD", "CHF", "NZD"
]


def clean_text(value):
    if value:
        return value.strip()
    return ""


def fetch_page():
    response = requests.get(
        FOREX_FACTORY_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
        verify=False
    )

    response.raise_for_status()
    return response.text


def parse_calendar_rows(soup):
    """
    Selector-based parsing using td classes
    More accurate than raw text split
    """

    news_list = []

    rows = soup.select("tr.calendar__row, tr.calendar_row")

    last_time = ""
    last_currency = ""

    for row in rows:

        time_td = row.select_one("td.calendar__time")
        currency_td = row.select_one("td.calendar__currency")
        event_td = row.select_one("td.calendar__event")
        actual_td = row.select_one("td.calendar__actual")
        forecast_td = row.select_one("td.calendar__forecast")
        previous_td = row.select_one("td.calendar__previous")

        time_value = clean_text(time_td.get_text()) if time_td else ""
        currency = clean_text(currency_td.get_text()) if currency_td else ""
        event = clean_text(event_td.get_text(" ", strip=True)) if event_td else ""

        actual = clean_text(actual_td.get_text()) if actual_td else ""
        forecast = clean_text(forecast_td.get_text()) if forecast_td else ""
        previous = clean_text(previous_td.get_text()) if previous_td else ""

        # carry forward grouped rows
        if time_value:
            last_time = time_value
        else:
            time_value = last_time

        if currency:
            last_currency = currency
        else:
            currency = last_currency

        if currency not in VALID_CURRENCIES:
            continue

        if not event:
            continue

        raw = f"{time_value} {currency} {event} {actual} {forecast} {previous}".strip()

        news_list.append({
            "time": time_value,
            "currency": currency,
            "event": event,
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
            "raw": raw
        })

    return news_list


def fallback_parse(soup):
    """
    Backup parser if classes change
    """

    news_list = []

    rows = soup.find_all("tr")

    for row in rows[:200]:
        text = row.get_text(" ", strip=True)

        if len(text) < 8:
            continue

        for cur in VALID_CURRENCIES:
            if f" {cur} " in f" {text} ":
                news_list.append({
                    "time": "",
                    "currency": cur,
                    "event": text,
                    "actual": "",
                    "forecast": "",
                    "previous": "",
                    "raw": text
                })
                break

    return news_list


def get_news():
    """
    Main public function
    """

    try:
        html = fetch_page()

        soup = BeautifulSoup(html, "lxml")

        news_list = parse_calendar_rows(soup)

        # fallback if selector fails
        if not news_list:
            news_list = fallback_parse(soup)

        # keep latest rows
        news_list = news_list[-MAX_NEWS_ROWS:]

        if not news_list:
            news_list.append({
                "time": "-",
                "currency": "-",
                "event": "Connected but no rows found",
                "actual": "",
                "forecast": "",
                "previous": "",
                "raw": "Connected but no rows found"
            })

        return news_list

    except Exception as e:
        return [{
            "time": "-",
            "currency": "-",
            "event": f"Error fetching news: {str(e)}",
            "actual": "",
            "forecast": "",
            "previous": "",
            "raw": f"Error fetching news: {str(e)}"
        }]