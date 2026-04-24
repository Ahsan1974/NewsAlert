from rich.console import Console
from rich.table import Table

console = Console()


def show_news(news_items):
    table = Table(title="Forex Factory News (PKT)")

    table.add_column("No", style="cyan")
    table.add_column("News", style="green")

    for i, item in enumerate(news_items, start=1):
        table.add_row(str(i), item["raw"])

    console.print(table)