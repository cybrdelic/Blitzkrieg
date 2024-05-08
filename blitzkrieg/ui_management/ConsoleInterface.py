from alive_progress import alive_bar
from halo import Halo
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.panel import Panel
import time
from rich.text import Text

class ConsoleInterface:
    def __init__(self):
        self.console = Console()

    def show_progress(self, total, message, check_function=None):
        """
        Shows a progress bar and optionally checks a condition at each step.
        Returns True if the condition is met before completion, False otherwise.
        """
        with alive_bar(total, title=message, bar="blocks", spinner="dots") as bar:
            for _ in range(total):
                time.sleep(1)  # Simulate time passing
                if check_function and check_function():
                    self.console.print("[bold green]PostgreSQL is now ready.[/bold green] \n")
                    return True
                bar()  # Update the progress bar
        return False

    def show_spinner(self, action, message, success_message="Succeeded", failure_message="Failed", spinner='dots'):
        with Halo(text=message, spinner=spinner, color='magenta'):
            try:
                result = action()  # Execute the passed function
                if result:
                    self.console.print(f"[bold green]{success_message}[/bold green]")
                else:
                    self.console.print(f"[bold red]{failure_message}[/bold red]")
                return result
            except Exception as e:
                self.console.print(f"[bold red]{failure_message}: {str(e)}[/bold red]")
                return False

    def configure_table(self):
        table = Table(
            title="Issue Processing Status",
            show_header=True,
            header_style="bold magenta",
            title_style="bold cyan",
            border_style="bright_green",
            padding=(0, 1),
            title_justify="left"
        )
        table.add_column("File", style="bold yellow", justify="left", width=40, no_wrap=True)
        table.add_column("Action", style="bold blue", justify="left", width=25)
        table.add_column("Status", style="bold green", justify="left", width=35)
        return table

    def display_notice(self, message, style="bold yellow"):
        panel = Panel(message, style=style)
        self.console.print(panel)

    def display_step(self, title, description, is_successful=True):
        self.console.print(f"[bold blue]{title}[/bold blue]")
        self.console.print(f"{description}")

    def show_status_chip(self, message, success=True):
        icon = "✔️" if success else "❌"
        color = "bold green" if success else "bold red"
        self.console.print(f"[{color}]{icon} {message}[/{color}]")
