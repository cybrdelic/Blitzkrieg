from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from contextlib import contextmanager
from rich.rule import Rule
import pyfiglet

console = Console()

def print_cli_header():
    """Prints a CLI header."""
    title_text = "RunDBFast"
    ascii_art = pyfiglet.figlet_format(title_text, font="slant")
    console.print(Panel("[bold bright_yellow]" + ascii_art + "[/bold bright_yellow]", expand=False, style="bright_yellow"))

def print_cli_footer():
    """Prints a CLI footer."""
    footer_text = "[bold bright_cyan]🚀 Thanks for riding with us! Until next time! 🚀[/bold bright_cyan]"
    console.print(Rule(footer_text, style="bright_cyan"))

def print_message(message, style="bright_blue", title=None):
    if title:
        console.print(Panel(message, title=title, style=style))
    else:
        console.print(message, style=style)

@contextmanager
def show_progress(task_name):
    with Progress(
            "[progress.description]{task.description}",
            BarColumn(bar_width=None, style="bright_magenta"),
            "[progress.percentage]{task.percentage:>3.1f}%",
            SpinnerColumn(),
            transient=True
    ) as progress:
        task = progress.add_task(task_name, total=100)
        yield task

@contextmanager
def show_spinner(message):
    with Progress(SpinnerColumn(spinner_name='aesthetic'), "[bold bright_purple]{task.description}", transient=True) as progress:
        task = progress.add_task(message)
        yield task

def print_table(data, title=None):
    table = Table(show_header=True, header_style="bold bright_magenta")
    for column in data[0].keys():
        table.add_column(column)
    for row in data:
        table.add_row(*row.values())
    if title:
        console.print(Panel(table, title=title, style="bright_blue"))
    else:
        console.print(table)

def print_header(message, style="bold"):
    """Prints a header with text between two half-rules."""
    half_rule_len = (console.width - len(message) - 2) // 2
    half_rule = "─" * half_rule_len
    console.print()
    console.print(Text(half_rule), end="")
    console.print(Text(f" {message} ", style=style), end="")
    console.print(Text(half_rule))

def print_label(text, style="bold bright_green"):
    """Prints a label."""
    console.print(Text(text, style=style))
