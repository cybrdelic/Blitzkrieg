from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from contextlib import contextmanager

console = Console()

def print_message(message, style=None):
    console.print(message, style=style)

@contextmanager
def show_progress(task_name):
    with Progress() as progress:
        task = progress.add_task(task_name, total=100)
        yield task
