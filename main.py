

import json
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# CHANGED: use news scraper instead of calendar scraper
from scraper.forex_news import get_news

from config import (
    JSON_OUTPUT_FILE,
    TEXT_OUTPUT_FILE,
    REFRESH_SECONDS
)

console = Console()

# store previous headlines
previous_snapshot = set()


def save_json(news):
    with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(news, f, indent=4)


def save_text(lines):
    with open(TEXT_OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def detect_changes(news_rows):
    """
    Detect new headlines only
    """
    global previous_snapshot

    current_snapshot = set()
    messages = []

    for item in news_rows:
        key = item["title"]
        current_snapshot.add(key)

        if key not in previous_snapshot:
            messages.append(f"NEW: {item['title']}")

    previous_snapshot = current_snapshot

    return messages


def build_table(news):
    """
    Build news headlines table
    """

    table = Table(title="LIVE FOREX FACTORY NEWS")

    table.add_column("No", style="cyan", justify="center")
    table.add_column("Section", style="green")
    table.add_column("Headline", style="white")
    table.add_column("Age", style="cyan")
    table.add_column("Source", style="magenta")
    table.add_column("Impact", style="red")
    table.add_column("Gold Bias", style="yellow")

    json_output = []
    text_output = []

    row_no = 1

    for item in news:

        table.add_row(
            str(row_no),
            item["section"],
            item["title"][:75],
            item["age"],
            item["source"],
            item["impact"],
            item["sentiment"]
        )

        json_output.append({
            "section": item["section"],
            "headline": item["title"],
            "age": item["age"],
            "source": item["source"],
            "impact": item["impact"],
            "sentiment": item["sentiment"],
            "url": item["url"]
        })

        text_output.append(
            f"{row_no}. "
            f"{item['section']} | "
            f"{item['title']} | "
            f"{item['age']} | "
            f"{item['source']} | "
            f"{item['impact']} | "
            f"{item['sentiment']}"
        )

        row_no += 1

    return table, json_output, text_output


def run_once():
    news = get_news()

    table, json_output, text_output = build_table(news)

    changes = detect_changes(news)

    console.clear()
    console.print(table)

    # alerts
    if changes:
        for msg in changes:
            console.print(
                Panel(msg, title="BREAKING ALERT", border_style="green")
            )
    else:
        console.print(
            Panel(
                "No new headlines. Waiting for next refresh.",
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