# import requests
# import urllib3
# from bs4 import BeautifulSoup

# from config import FOREX_FACTORY_URL, HEADERS, REQUEST_TIMEOUT

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# def get_news():
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

#         for row in rows[:100]:
#             text = row.get_text(" ", strip=True)

#             if len(text) < 8:
#                 continue

#             if any(cur in text for cur in ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"]):
#                 news_list.append({"raw": text})

#         if not news_list:
#             news_list.append({"raw": "Connected but no rows found."})

#         return news_list[:10]

#     except Exception as e:
#         return [{"raw": f"Error fetching news: {str(e)}"}]



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


def extract_numbers(parts):
    """
    Extract actual / forecast / previous values
    Example:
    ['4:30pm','USD','CPI','0.4%','0.3%','0.2%']
    """
    nums = []

    for item in parts:
        clean = item.replace("%", "").replace(".", "").replace("-", "")

        if clean.isdigit():
            nums.append(item)

    actual = ""
    forecast = ""
    previous = ""

    if len(nums) >= 3:
        actual = nums[-3]
        forecast = nums[-2]
        previous = nums[-1]

    elif len(nums) == 2:
        forecast = nums[-2]
        previous = nums[-1]

    elif len(nums) == 1:
        previous = nums[-1]

    return actual, forecast, previous


def parse_row(text):
    """
    Convert raw row into structured object
    """

    parts = text.split()

    if len(parts) < 3:
        return None

    time_value = parts[0]
    currency = parts[1]

    actual, forecast, previous = extract_numbers(parts)

    # Event text remove time/currency and numeric tail
    event_words = []

    for item in parts[2:]:
        if item in [actual, forecast, previous]:
            continue
        event_words.append(item)

    event = " ".join(event_words).strip()

    return {
        "time": time_value,
        "currency": currency,
        "event": event,
        "actual": actual,
        "forecast": forecast,
        "previous": previous,
        "raw": text
    }


def get_news():
    """
    Fetch latest Forex Factory news rows
    """

    news_list = []

    try:
        response = requests.get(
            FOREX_FACTORY_URL,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            verify=False
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        rows = soup.find_all("tr")

        for row in rows[:150]:
            text = row.get_text(" ", strip=True)

            if len(text) < 8:
                continue

            if any(cur in text for cur in ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"]):
                parsed = parse_row(text)

                if parsed:
                    news_list.append(parsed)

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

        return news_list[:MAX_NEWS_ROWS]

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