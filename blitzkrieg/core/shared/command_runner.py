import subprocess
from rich.console import Console
from rich.progress import Progress

from blitzkrieg.cli.ui_utils import handle_error

console = Console()

import subprocess

def _run_command(cmd: str, show_progress: bool = False, log_to_console: bool = True) -> str:
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return None

        return stdout.strip()

    except Exception as e:
        return None
