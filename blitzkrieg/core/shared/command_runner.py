import subprocess
import socket
from rich.console import Console
from rich.progress import Progress
import asyncio

from blitzkrieg.cli.ui_utils import handle_error
console = Console()

async def _run_command_async(cmd: str) -> str:
    """Run shell commands asynchronously."""
    try:
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Executing command :::{cmd}:::...[/cyan]", total=100)
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            progress.update(task, completed=100)

        if process.returncode != 0:
            handle_error(f"Command failed with error: {stderr.decode()}")
            return None

        return stdout.decode().strip()
    except Exception as e:
        handle_error(f"An exception occurred: {e}")
        return None
