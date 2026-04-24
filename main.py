# import json
# from rich.console import Console
# from rich.table import Table

# from scraper.forex_factory import get_news
# from utils.news_impact import analyze_news

# console = Console()


# def save_json(news):
#     with open("data/news.json", "w", encoding="utf-8") as f:
#         json.dump(news, f, indent=4)


# def save_text(lines):
#     with open("output/latest.txt", "w", encoding="utf-8") as f:
#         for line in lines:
#             f.write(line + "\n")


# def main():
#     console.print("[bold green]Forex News Scraper Started[/bold green]\n")

#     news = get_news()

#     table = Table(title="Smart Forex News Impact")

#     table.add_column("No", style="cyan")
#     table.add_column("News", style="white")
#     table.add_column("Impact", style="red")
#     table.add_column("Gold View", style="yellow")
#     table.add_column("Action", style="green")

#     json_output = []
#     text_output = []

#     for i, item in enumerate(news, start=1):
#         result = analyze_news(item["raw"])

#         table.add_row(
#             str(i),
#             item["raw"][:45],
#             result["impact"],
#             result["gold_bias"],
#             result["action"]
#         )

#         json_output.append({
#             "news": item["raw"],
#             "impact": result["impact"],
#             "gold_view": result["gold_bias"],
#             "action": result["action"]
#         })

#         text_output.append(
#             f"{i}. {item['raw']} | {result['impact']} | {result['gold_bias']} | {result['action']}"
#         )

#     console.print(table)

#     save_json(json_output)
#     save_text(text_output)

#     console.print("\n[bold green]Files Saved:[/bold green]")
#     console.print("data/news.json")
#     console.print("output/latest.txt")


# if __name__ == "__main__":
#     main()

# import json
# import time
# from rich.console import Console
# from rich.table import Table

# from scraper.forex_factory import get_news
# from utils.news_impact import analyze_news, is_xauusd_related

# from config import (
#     JSON_OUTPUT_FILE,
#     TEXT_OUTPUT_FILE,
#     REFRESH_SECONDS
# )

# console = Console()


# def save_json(news):
#     with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(news, f, indent=4)


# def save_text(lines):
#     with open(TEXT_OUTPUT_FILE, "w", encoding="utf-8") as f:
#         for line in lines:
#             f.write(line + "\n")


# def build_table(news):
#     table = Table(title="LIVE XAUUSD NEWS ENGINE")

#     table.add_column("No", style="cyan", justify="center")
#     table.add_column("Time", style="green")
#     table.add_column("Cur", style="magenta")
#     table.add_column("Event", style="white")
#     table.add_column("Actual", style="yellow")
#     table.add_column("Forecast", style="yellow")
#     table.add_column("Impact", style="red")
#     table.add_column("Gold View", style="bright_yellow")
#     table.add_column("Action", style="bright_green")

#     json_output = []
#     text_output = []

#     row_no = 1

#     for item in news:

#         # Only XAUUSD relevant news
#         if not is_xauusd_related(item["raw"]):
#             continue

#         result = analyze_news(item)

#         table.add_row(
#             str(row_no),
#             item["time"],
#             item["currency"],
#             item["event"][:32],
#             item["actual"],
#             item["forecast"],
#             result["impact"],
#             result["gold_bias"],
#             result["action"]
#         )

#         json_output.append({
#             "time": item["time"],
#             "currency": item["currency"],
#             "event": item["event"],
#             "actual": item["actual"],
#             "forecast": item["forecast"],
#             "previous": item["previous"],
#             "impact": result["impact"],
#             "gold_view": result["gold_bias"],
#             "action": result["action"]
#         })

#         text_output.append(
#             f"{row_no}. "
#             f"{item['time']} | "
#             f"{item['currency']} | "
#             f"{item['event']} | "
#             f"A:{item['actual']} "
#             f"F:{item['forecast']} | "
#             f"{result['impact']} | "
#             f"{result['gold_bias']} | "
#             f"{result['action']}"
#         )

#         row_no += 1

#     return table, json_output, text_output


# def run_once():
#     console.print("[bold green]Fetching latest live news...[/bold green]\n")

#     news = get_news()

#     table, json_output, text_output = build_table(news)

#     console.clear()
#     console.print(table)

#     save_json(json_output)
#     save_text(text_output)

#     console.print(
#         f"\n[bold green]Files Updated:[/bold green] "
#         f"{JSON_OUTPUT_FILE} | {TEXT_OUTPUT_FILE}"
#     )

#     console.print(
#         f"[bold cyan]Next Refresh In {REFRESH_SECONDS} Seconds[/bold cyan]"
#     )


# def main():
#     while True:
#         run_once()
#         time.sleep(REFRESH_SECONDS)


# if __name__ == "__main__":
#     main()


import json
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from scraper.forex_factory import get_news
from utils.news_impact import analyze_news, is_xauusd_related

from config import (
    JSON_OUTPUT_FILE,
    TEXT_OUTPUT_FILE,
    REFRESH_SECONDS
)

console = Console()

# store previous snapshot for change detection
previous_snapshot = {}


def save_json(news):
    with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(news, f, indent=4)


def save_text(lines):
    with open(TEXT_OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def get_event_key(item):
    """
    Unique identity for an event
    """
    return f"{item['time']}|{item['currency']}|{item['event']}"


def detect_changes(current_rows):
    """
    Compare previous snapshot vs current rows
    """
    global previous_snapshot

    messages = []
    new_snapshot = {}

    for item in current_rows:
        key = get_event_key(item)

        values = {
            "actual": item["actual"],
            "forecast": item["forecast"],
            "previous": item["previous"]
        }

        new_snapshot[key] = values

        # NEW EVENT
        if key not in previous_snapshot:
            messages.append(
                f"NEW: {item['currency']} {item['event']} added"
            )

        # UPDATED EVENT
        else:
            old_values = previous_snapshot[key]

            if old_values["actual"] != values["actual"]:
                messages.append(
                    f"UPDATED: {item['currency']} {item['event']} "
                    f"Actual {old_values['actual']} -> {values['actual']}"
                )

            elif old_values["forecast"] != values["forecast"]:
                messages.append(
                    f"UPDATED: {item['currency']} {item['event']} "
                    f"Forecast {old_values['forecast']} -> {values['forecast']}"
                )

    previous_snapshot = new_snapshot

    return messages


def build_table(news):
    table = Table(title="LIVE XAUUSD NEWS ENGINE")

    table.add_column("No", style="cyan", justify="center")
    table.add_column("Time", style="green")
    table.add_column("Cur", style="magenta")
    table.add_column("Event", style="white")
    table.add_column("Actual", style="yellow")
    table.add_column("Forecast", style="yellow")
    table.add_column("Impact", style="red")
    table.add_column("Gold View", style="bright_yellow")
    table.add_column("Action", style="bright_green")

    json_output = []
    text_output = []
    filtered_rows = []

    row_no = 1

    for item in news:

        # only gold relevant rows
        if not is_xauusd_related(item["raw"]):
            continue

        result = analyze_news(item)

        filtered_rows.append(item)

        table.add_row(
            str(row_no),
            item["time"],
            item["currency"],
            item["event"][:32],
            item["actual"],
            item["forecast"],
            result["impact"],
            result["gold_bias"],
            result["action"]
        )

        json_output.append({
            "time": item["time"],
            "currency": item["currency"],
            "event": item["event"],
            "actual": item["actual"],
            "forecast": item["forecast"],
            "previous": item["previous"],
            "impact": result["impact"],
            "gold_view": result["gold_bias"],
            "action": result["action"]
        })

        text_output.append(
            f"{row_no}. "
            f"{item['time']} | "
            f"{item['currency']} | "
            f"{item['event']} | "
            f"A:{item['actual']} "
            f"F:{item['forecast']} | "
            f"{result['impact']} | "
            f"{result['gold_bias']} | "
            f"{result['action']}"
        )

        row_no += 1

    return table, json_output, text_output, filtered_rows


def run_once():
    news = get_news()

    table, json_output, text_output, filtered_rows = build_table(news)

    changes = detect_changes(filtered_rows)

    console.clear()
    console.print(table)

    # show changes only
    if changes:
        for msg in changes:
            console.print(
                Panel(msg, title="ALERT", border_style="green")
            )
    else:
        console.print(
            Panel(
                "No new updates. Waiting for next refresh.",
                title="STATUS",
                border_style="yellow"
            )
        )

    save_json(json_output)
    save_text(text_output)

    console.print(
        f"\n[bold green]Files Updated:[/bold green] "
        f"{JSON_OUTPUT_FILE} | {TEXT_OUTPUT_FILE}"
    )

    console.print(
        f"[bold cyan]Next Refresh In {REFRESH_SECONDS} Seconds[/bold cyan]"
    )


def main():
    while True:
        run_once()
        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    main()