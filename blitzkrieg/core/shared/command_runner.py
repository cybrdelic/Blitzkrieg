import subprocess
from rich.console import Console
from rich.progress import Progress

from blitzkrieg.cli.ui_utils import handle_error

console = Console()

def _run_command(cmd: str, show_progress: bool = True, log_to_console: bool = True) -> str:
    try:
        if show_progress:
            with Progress() as progress:
                task = progress.add_task(f"[cyan]Executing command: {cmd}[/cyan]", total=100)
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    text=True
                )
                stdout, stderr = process.communicate()
                progress.update(task, completed=100)

        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate()

        if process.returncode != 0:
            handle_error(f"Command failed: {stderr.strip()}")
            if log_to_console:
                console.print("[red]Suggested Action: Please check the command and try again.[/red]")
            return None

        if log_to_console:
            console.print("[green]Command executed successfully![/green]")
        return stdout.strip()

    except Exception as e:
        handle_error(f"An unexpected error occurred: {e}")
        if log_to_console:
            console.print("[red]Suggested Action: Please consult the documentation or seek help.[/red]")
        return None
