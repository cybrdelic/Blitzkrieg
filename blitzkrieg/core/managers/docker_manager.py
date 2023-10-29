from blitzkrieg.cli.logging_config import setup_logging
from blitzkrieg.core.shared.command_runner import _run_command_async


ui_logger, backend_logger, console = setup_logging()
async def is_container_ready(container_name: str) -> bool:
    cmd = f"docker inspect --format='{{json .State.Status}}' {container_name}"
    status = await _run_command_async(cmd)
    if status == "running":
        console.print("[green]Container found and running![/green]")
        return True
    else:
        console.print("[yellow]Container {container_name} found, but not running.[/yellow]")
        return False
