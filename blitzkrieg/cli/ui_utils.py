from rich.prompt import Prompt
from blitzkrieg.cli.logging_config import setup_logging

backend_logger, ui_logger, console = setup_logging()

def handle_error(message: str):
    console.print(f"[bold red]Error: [/bold red][italic yellow]{message}[/italic yellow]")

def confirm_action(message: str) -> bool:
    return Prompt.ask(message, choices=["y", "n"], default="n") == "y"
