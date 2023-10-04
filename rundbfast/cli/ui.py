from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, SpinnerColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from contextlib import contextmanager
from rich.rule import Rule
import pyfiglet
import questionary

console = Console()

INFO_COLOR = "#808080"
SUCCESS_COLOR = "#00FF00"  # This is the hex code for red.
WARNING_COLOR = "bold yellow"
ERROR_COLOR = "FF0000"

def print_cli_header():
    """Prints a CLI header."""
    title_text = pyfiglet.figlet_format("RunDBFast", font="slant")
    console.print(Panel("[bold bright_yellow]" + title_text + "[/bold bright_yellow]", expand=False))

def print_cli_footer():
    """Prints a CLI footer."""
    footer_text = "[bold bright_cyan]🚀 Thanks for riding with us! Until next time! 🚀[/bold bright_cyan]"
    console.print(Rule(footer_text, style="bright_cyan"))

def print_message(message, style="#808080", title=None):
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

def print_label(text, style="#808080"):
    """Prints a label."""
    console.print(Text(text, style=style))

def print_warning(message):
    """Prints a warning message."""
    console.print(f"⚠️  {message}", style=WARNING_COLOR)

def print_error(message):
    """Prints an error message."""
    console.print(f"❌  {message}", style=ERROR_COLOR)

def print_success(message):
    """Prints a success message."""
    console.print(f"✅  {message}", style=SUCCESS_COLOR)

def print_divider():
    """Prints a simple divider for visually separating sections."""
    console.print(Rule(style=INFO_COLOR))

def show_choices(prompt, choices_list):
    """Displays a list of choices and lets the user select one."""
    return questionary.select(prompt, choices=choices_list).ask()

def pause_for_user():
    """Pauses the execution until the user presses enter."""
    input("\nPress [Enter] to continue...")

def clear_screen():
    """Clears the terminal."""
    console.clear()
