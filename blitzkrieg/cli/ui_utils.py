from rich.prompt import Prompt
from blitzkrieg.cli.logging_config import setup_logging
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.layout import Layout
from rich.spinner import Spinner
from rich.status import Status
from time import sleep

backend_logger, ui_logger, console = setup_logging()

class UIComponent:
    def render(self):
        pass

class Step(UIComponent):
    def __init__(self, message: str, substeps: list = None):
        self.message = message
        self.substeps = substeps if substeps else []

    def render(self):
        console.print(f"[bold yellow]{self.message}")
        for substep in self.substeps:
            substep.render()

class TextComponent(UIComponent):
    def __init__(self, message: str):
        self.message = message

    def render(self):
        console.print(f"  -> {self.message}")

# Error Handling
def handle_error(message: str, suggestion: str = None):
    console.print(Panel(f"[bold red]Error: {message}[/bold red]", expand=False))
    if suggestion:
        console.print(Panel(f"[italic yellow]Suggestion: {suggestion}[/italic yellow]", expand=False))

# Confirm Action
def confirm_action(message: str) -> bool:
    return Prompt.ask(f"[bold cyan]{message}[/bold cyan]", choices=["y", "n"], default="n") == "y"

# Ask for Input
def ask_for_input(prompt: str, options: list = None):
    if options:
        return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]", choices=options)
    else:
        return Prompt.input(f"[bold cyan]{prompt}[/bold cyan]")

# Display List
def display_list(data_list: list, title: str):
    table = Table(show_header=True)
    table.add_column("Index")
    table.add_column("Name")
    table.add_column("Description")
    for index, item in enumerate(data_list):
        table.add_row(str(index + 1), item["name"], item["description"])
    console.print(Panel(f"[u]{title}[/u]", table))

# Progress Bar
def progress_bar(iterable, description):
    with Progress() as progress:
        task = progress.add_task(f"[cyan]{description}...", total=len(iterable))
        for item in iterable:
            progress.update(task, completed=progress.tasks[task].completed + 1)
            yield item

# Display Header
def display_header(title: str):
    console.print(Panel(f"[bold blue]{title}[/bold blue]", expand=False))

# Animated Spinner
def animated_spinner(msg: str):
    with Spinner(f"[bold magenta]{msg}[/bold magenta]", spinner_name="dots12"):
        pass  # Your long-running operation here

# Real-Time Status
def real_time_status(status: str):
    with Status(status, spinner="dots12") as status:
        pass  # Your long-running operation here

# Interactive Form
def interactive_form(fields: list):
    form_data = {}
    for field in fields:
        form_data[field['name']] = Prompt.ask(field['prompt'], choices=field.get('options', None))
    return form_data

# Step-by-Step Guide
def step_by_step(steps: list):
    for step in steps:
        step.render()

# ... You can add more components as needed
