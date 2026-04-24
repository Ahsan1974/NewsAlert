# """
# Project configuration
# """

# # Forex Factory Calendar URL
# FOREX_FACTORY_URL = "https://www.forexfactory.com/calendar"

# # Pakistan timezone
# TIMEZONE = "Asia/Karachi"

# # How many news rows to show in terminal
# MAX_NEWS_ROWS = 10

# # Save output files
# JSON_OUTPUT_FILE = "data/news.json"
# TEXT_OUTPUT_FILE = "output/latest.txt"

# # Request timeout (seconds)
# REQUEST_TIMEOUT = 15

# # Browser user-agent
# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/124.0 Safari/537.36"
#     )
# }


"""
Project configuration
"""

# Forex Factory Calendar URL
FOREX_FACTORY_URL = "https://www.forexfactory.com/calendar"

# Pakistan timezone
TIMEZONE = "Asia/Karachi"

# How many news rows to show in terminal
MAX_NEWS_ROWS = 15

# Save output files
JSON_OUTPUT_FILE = "data/news.json"
TEXT_OUTPUT_FILE = "output/latest.txt"

# Request timeout (seconds)
REQUEST_TIMEOUT = 15

# Auto refresh every 60 seconds (live mode)
REFRESH_SECONDS = 60

# Browser user-agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# Gold / XAUUSD relevant keywords only
XAUUSD_KEYWORDS = [
    "USD",
    "FOMC",
    "FED",
    "POWELL",
    "CPI",
    "PCE",
    "NFP",
    "NON-FARM",
    "INTEREST RATE",
    "RATE DECISION",
    "JOBLESS",
    "INFLATION",
    "TREASURY",
    "YIELD",
    "WAR",
    "GEOPOLITICAL"
]