# decorators.py

from functools import wraps
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def with_spinner(message, success_message="Succeeded", failure_message="Failed", spinner="dots"):
    def spinner_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            console_interface = args[0].console
            task_id = console_interface.start_task(message)
            try:
                result = func(*args, **kwargs)
                console_interface.complete_task(task_id)
                console_interface.log(f"[bold green]{success_message}[/bold green]")
                return result
            except Exception as e:
                console_interface.complete_task(task_id)
                console_interface.log(f"[bold red]{failure_message}: {str(e)}[/bold red]")
                console.print_exception(show_locals=True)
                return False
        return wrapper
    return spinner_decorator
