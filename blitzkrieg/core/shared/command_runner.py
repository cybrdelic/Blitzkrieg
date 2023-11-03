import subprocess
from typing import Optional, Tuple
from rich.console import Console
from rich.progress import Progress

from blitzkrieg.cli.ui_utils import handle_error

console = Console()

import subprocess

def _run_command(cmd: str, show_progress: bool = False, log_to_console: bool = True) -> Tuple[int, Optional[str]]:
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        stdout, stderr = process.communicate()

        # Return both the return code and the output or error message
        if process.returncode != 0:
            error_message = f"Command '{cmd}' failed with exit code {process.returncode}: {stderr}"
            return process.returncode, error_message
        return process.returncode, stdout.strip()

    except Exception as e:
        error_message = f"An exception occurred: {str(e)}"
        return -1, error_message
