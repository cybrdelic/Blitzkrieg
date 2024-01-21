from rich.console import Console
from rich.progress import Progress, BarColumn
from rich.table import Table
from rich.theme import Theme
import time
from rich.box import ROUNDED

class ConsoleInterface:
    def __init__(self):
        self.custom_theme = Theme({
            "info": "dim cyan",
            "warning": "magenta",
            "error": "bold red",
            "success": "bold green",
            "header": "bold blue"
        })
        self.console = Console(theme=self.custom_theme)

    def show_progress_bar(self, task_description, total):
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(task_description, total=total)
            while not progress.finished:
                progress.update(task, advance=0.1)
                time.sleep(0.1)

    def configure_table(self):
        table = Table(
            title="Issue Processing Status",
            show_header=True,
            header_style="bold magenta",
            title_style="bold cyan",
            border_style="bright_green",
            box=ROUNDED,
            padding=(0, 1),
            title_justify="left"
        )
        table.add_column("File", style="bold yellow", justify="left", width=40, no_wrap=True)
        table.add_column("Action", style="bold blue", justify="left", width=25)
        table.add_column("Status", style="bold green", justify="left", width=35)
        return table

    # Additional methods for console interaction
