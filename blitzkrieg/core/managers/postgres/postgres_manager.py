import asyncio
from pathlib import Path
from jinja2 import Template
from fuzzywuzzy import process
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt
from blitzkrieg.cli.logging_config import setup_logging
from blitzkrieg.cli.ui_utils import confirm_action, handle_error
from blitzkrieg.core.managers.docker_manager import is_container_ready
from blitzkrieg.core.shared.command_runner import _run_command_async
from blitzkrieg.core.shared.utils.config import ProjectConfig
from blitzkrieg.core.shared.utils.file_handling import get_template_path
from blitzkrieg.core.shared.utils.networking import find_available_port

backend_logger, ui_logger, console = setup_logging()

async def generate_docker_compose_file(project_config: ProjectConfig) -> Path:
    project_name = project_config.project_name
    password = project_config.password
    with Progress() as progress:
        task1 = progress.add_task(f"[cyan]Writing Docker Compose template for container named {project_name}...", total=100)
        try:
            template_path = await get_template_path(project_config.template_dir, 'docker-compose-template.yml')
            if template_path is None:
                return None

            output_path = project_config.instances_dir / f"docker-compose-{project_name}.yml"
            with open(template_path, 'r') as f:
                template = Template(f.read())
            rendered = template.render(
                PROJECT_NAME=project_name,
                POSTGRES_USER=project_config.db_user,
                POSTGRES_PASSWORD=password,
                POSTGRES_DB=project_name,
                POSTGRES_PORT=find_available_port(),
                PGADMIN_EMAIL=project_config.admin_email,
                PGADMIN_PASSWORD=password,
                PGADMIN_PORT=find_available_port(5050)
            )

            with open(output_path, 'w') as f:
                f.write(rendered)
            progress.update(task1, completed=100)
            console.print("[green]Docker compose file generated successfully![/green]")
            return output_path
        except Exception as e:
            handle_error(f"An exception occurred: {e}")
            return None

async def start_containers_async(project_config: ProjectConfig):
    project_name = project_config.project_name
    if await is_container_ready(project_config.postgres_container_name):
        ui_logger.info(f"Container {project_config.postgres_container_name} is already running.")
        return

    console.print("[blue]Container found, but not running. Starting containers...[/blue]")
    compose_file_path = await generate_docker_compose_file(project_config)
    if compose_file_path:
        cmd = f"docker-compose -p {project_name} -f {compose_file_path} up -d"
        await _run_command_async(cmd)
        ui_logger.info("Containers started.")

async def stop_containers_async(project_name: str):
    console.print("[blue]Stopping containers...[/blue]")
    cmd = f"docker-compose -f docker-compose-{project_name}.yml down"
    await _run_command_async(cmd)
    ui_logger.info("Containers stopped.")

async def initialize_with_persistence_check(project_config: ProjectConfig):
    if confirm_action(f"Do you want to initialize the project {project_config.project_name}?"):
        is_ready = await is_container_ready(project_config.postgres_container_name)
        if not is_ready:
            ui_logger.info(f"Container {project_config.postgres_container_name} is not running. Starting containers.")
            await start_containers_async(project_config)
