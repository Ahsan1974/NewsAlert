



# import requests
# import urllib3
# from bs4 import BeautifulSoup

# from config import (
#     FOREX_FACTORY_URL,
#     HEADERS,
#     REQUEST_TIMEOUT,
#     MAX_NEWS_ROWS
# )

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# def extract_numbers(parts):
#     """
#     Extract actual / forecast / previous values
#     Example:
#     ['4:30pm','USD','CPI','0.4%','0.3%','0.2%']
#     """
#     nums = []

#     for item in parts:
#         clean = item.replace("%", "").replace(".", "").replace("-", "")

#         if clean.isdigit():
#             nums.append(item)

#     actual = ""
#     forecast = ""
#     previous = ""

#     if len(nums) >= 3:
#         actual = nums[-3]
#         forecast = nums[-2]
#         previous = nums[-1]

#     elif len(nums) == 2:
#         forecast = nums[-2]
#         previous = nums[-1]

#     elif len(nums) == 1:
#         previous = nums[-1]

#     return actual, forecast, previous


# def parse_row(text):
#     """
#     Convert raw row into structured object
#     """

#     parts = text.split()

#     if len(parts) < 3:
#         return None

#     time_value = parts[0]
#     currency = parts[1]

#     actual, forecast, previous = extract_numbers(parts)

#     # Event text remove time/currency and numeric tail
#     event_words = []

#     for item in parts[2:]:
#         if item in [actual, forecast, previous]:
#             continue
#         event_words.append(item)

#     event = " ".join(event_words).strip()

#     return {
#         "time": time_value,
#         "currency": currency,
#         "event": event,
#         "actual": actual,
#         "forecast": forecast,
#         "previous": previous,
#         "raw": text
#     }


# def get_news():
#     """
#     Fetch latest Forex Factory news rows
#     """

#     news_list = []

#     try:
#         response = requests.get(
#             FOREX_FACTORY_URL,
#             headers=HEADERS,
#             timeout=REQUEST_TIMEOUT,
#             verify=False
#         )

#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, "lxml")
#         rows = soup.find_all("tr")

#         for row in rows[:150]:
#             text = row.get_text(" ", strip=True)

#             if len(text) < 8:
#                 continue

#             if any(cur in text for cur in ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"]):
#                 parsed = parse_row(text)

#                 if parsed:
#                     news_list.append(parsed)

#         if not news_list:
#             news_list.append({
#                 "time": "-",
#                 "currency": "-",
#                 "event": "Connected but no rows found",
#                 "actual": "",
#                 "forecast": "",
#                 "previous": "",
#                 "raw": "Connected but no rows found"
#             })

#         return news_list[:MAX_NEWS_ROWS]

#     except Exception as e:
#         return [{
#             "time": "-",
#             "currency": "-",
#             "event": f"Error fetching news: {str(e)}",
#             "actual": "",
#             "forecast": "",
#             "previous": "",
#             "raw": f"Error fetching news: {str(e)}"
#         }]


# import requests
# import urllib3
# import re
# from bs4 import BeautifulSoup

# from config import (
#     FOREX_FACTORY_URL,
#     HEADERS,
#     REQUEST_TIMEOUT,
#     MAX_NEWS_ROWS
# )

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# VALID_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]


# def is_time(value):
#     """
#     Detect values like:
#     3:30am
#     10:00pm
#     """
#     value = value.lower().strip()
#     return bool(re.match(r"^\d{1,2}:\d{2}(am|pm)$", value))


# def extract_numbers(parts):
#     """
#     Extract numeric values:
#     Actual / Forecast / Previous
#     """

#     nums = []

#     for item in parts:
#         clean = item.replace("%", "").replace(",", "").replace(".", "").replace("-", "")

#         if clean.isdigit():
#             nums.append(item)

#     actual = ""
#     forecast = ""
#     previous = ""

#     if len(nums) >= 3:
#         actual = nums[-3]
#         forecast = nums[-2]
#         previous = nums[-1]

#     elif len(nums) == 2:
#         forecast = nums[-2]
#         previous = nums[-1]

#     elif len(nums) == 1:
#         previous = nums[-1]

#     return actual, forecast, previous


# def clean_event_words(words, actual, forecast, previous):
#     """
#     Remove numeric tail from event name
#     """

#     cleaned = []

#     for item in words:
#         if item in [actual, forecast, previous]:
#             continue
#         cleaned.append(item)

#     return " ".join(cleaned).strip()


# def parse_row(text, last_time="", last_currency=""):
#     """
#     Parse grouped Forex Factory row correctly.
#     Handles rows where time/currency are omitted.
#     """

#     parts = text.split()

#     if len(parts) < 2:
#         return None, last_time, last_currency

#     idx = 0
#     time_value = last_time
#     currency = last_currency

#     # detect time
#     if is_time(parts[0]):
#         time_value = parts[0]
#         idx += 1

#     # detect currency
#     if idx < len(parts) and parts[idx] in VALID_CURRENCIES:
#         currency = parts[idx]
#         idx += 1

#     # invalid if still no currency
#     if currency == "":
#         return None, last_time, last_currency

#     remaining = parts[idx:]

#     if not remaining:
#         return None, time_value, currency

#     actual, forecast, previous = extract_numbers(remaining)

#     event = clean_event_words(
#         remaining,
#         actual,
#         forecast,
#         previous
#     )

#     item = {
#         "time": time_value,
#         "currency": currency,
#         "event": event,
#         "actual": actual,
#         "forecast": forecast,
#         "previous": previous,
#         "raw": text
#     }

#     return item, time_value, currency


# def get_news():
#     """
#     Fetch latest Forex Factory rows
#     Improved grouped row handling
#     """

#     news_list = []

#     try:
#         response = requests.get(
#             FOREX_FACTORY_URL,
#             headers=HEADERS,
#             timeout=REQUEST_TIMEOUT,
#             verify=False
#         )

#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, "lxml")
#         rows = soup.find_all("tr")

#         last_time = ""
#         last_currency = ""

#         for row in rows[:250]:

#             text = row.get_text(" ", strip=True)

#             if len(text) < 5:
#                 continue

#             if not any(cur in text for cur in VALID_CURRENCIES) and not is_time(text.split()[0]):
#                 continue

#             parsed, last_time, last_currency = parse_row(
#                 text,
#                 last_time,
#                 last_currency
#             )

#             if parsed:
#                 news_list.append(parsed)

#         # newest rows usually lower on page
#         news_list = news_list[-MAX_NEWS_ROWS:]

#         if not news_list:
#             news_list.append({
#                 "time": "-",
#                 "currency": "-",
#                 "event": "Connected but no rows found",
#                 "actual": "",
#                 "forecast": "",
#                 "previous": "",
#                 "raw": "Connected but no rows found"
#             })

#         return news_list

#     except Exception as e:
#         return [{
#             "time": "-",
#             "currency": "-",
#             "event": f"Error fetching news: {str(e)}",
#             "actual": "",
#             "forecast": "",
#             "previous": "",
#             "raw": f"Error fetching news: {str(e)}"
#         }]



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