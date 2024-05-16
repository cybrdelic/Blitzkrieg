from loguru import logger
from halo import Halo
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.logging import RichHandler
import time
import traceback
import re

class ConsoleInterface:
    def __init__(self, spinner_type='dots', spinner_color='cyan'):
        self.console = Console()
        logger.remove()
        logger.add(RichHandler(console=self.console, markup=True), format="{message}", level="INFO")
        self.spinner = Halo(spinner=spinner_type, color=spinner_color)

    def display_step(self, title, x=""):
        self.console.print(Text(f"=== {title} ===\n", style="bold cyan"))

    def display_banner(self, text):
        self.console.print(Text(text, style="bold white on blue"), end="\n\n")

    def clean_log_message(self, message):
        # Remove ANSI escape sequences and unnecessary parts
        message = re.sub(r'\x1b\[[0-9;]*m', '', message)
        return message.strip()

    def log(self, message, level="info"):
        levels = {
            "info": "INFO",
            "warning": "WARNING",
            "error": "ERROR",
            "success": "SUCCESS"
        }
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        clean_message = self.clean_log_message(message)
        log_message = f"[{timestamp}] {clean_message}"
        logger.log(levels[level], log_message)

    def run_tasks(self, tasks, title, task_progress_message_map):
        self.display_banner(title)
        task_metrics = {}

        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(bar_width=None),
            TextColumn("[progress.completed]/[progress.total]"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task_id = progress.add_task(title, total=len(tasks))

            for task in tasks:
                func, args = task if len(task) > 1 else (task[0], {})
                task_name = func.__name__
                task_progress_message = task_progress_message_map.get(task_name, "Executing task")

                self.display_step(task_progress_message)
                progress.update(task_id, description=task_progress_message, advance=1)

                self.spinner.start(task_progress_message)
                start_time = time.time()

                try:
                    task_output = func(**args)
                    log_level = "success"
                    self.spinner.succeed("Completed")
                except Exception as e:
                    task_output = f"Exception occurred: {str(e)}\n{traceback.format_exc()}"
                    log_level = "error"
                    self.spinner.fail("Failed")

                end_time = time.time()
                elapsed_time = end_time - start_time
                task_metrics[task_name] = elapsed_time

                self.log(f"{task_output}", level=log_level)

                if log_level == "error":
                    break

            # Display final task metrics table
            table = Table(title="Task Metrics", style="bold magenta")
            table.add_column("Task", justify="left", style="cyan")
            table.add_column("Execution Time (s)", justify="right", style="magenta")

            for name, exec_time in task_metrics.items():
                table.add_row(name, f"{exec_time:.2f}")

            self.console.print(table)
