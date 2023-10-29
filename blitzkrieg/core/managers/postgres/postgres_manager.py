import asyncio
from pathlib import Path
from jinja2 import Template
from rich.console import Console
from blitzkrieg.cli.logging_config import setup_logging
from blitzkrieg.cli.ui_utils import (
    progress_bar, handle_error, Step, TextComponent, step_by_step, confirm_action
)
from blitzkrieg.core.managers.docker_manager import is_container_ready
from blitzkrieg.core.shared.command_runner import _run_command_async
from blitzkrieg.core.shared.utils.config import ProjectConfig
from blitzkrieg.core.shared.utils.file_handling import get_template_path
from blitzkrieg.core.shared.utils.networking import find_available_port

backend_logger, ui_logger, console = setup_logging()

async def generate_docker_compose_file(project_config: ProjectConfig) -> Path:
    steps = [
        Step("Generating Docker Compose File", [
            TextComponent(f"Working on container named {project_config.project_name}"),
            TextComponent("Rendering Template")
        ])
    ]
    step_by_step(steps)

    template_path = await get_template_path(project_config.template_dir, 'docker-compose-template.yml')
    if template_path is None:
        handle_error("Template not found", "Please ensure the template exists.")
        return None

    output_path = project_config.instances_dir / f"docker-compose-{project_config.project_name}.yml"
    try:
        with open(template_path, 'r') as f:
            template = Template(f.read())

        with open(output_path, 'w') as f:
            rendered = template.render(
                PROJECT_NAME=project_config.project_name,
                # ... other variables
            )
            f.write(rendered)

        console.print("[green]Docker compose file generated successfully![/green]")
        return output_path

    except Exception as e:
        handle_error(f"An unexpected error occurred: {e}", "Check your template and configuration.")
        return None

async def start_containers_async(project_config: ProjectConfig):
    steps = [
        Step("Starting Containers", [
            TextComponent("Checking if container is already running"),
            TextComponent("Starting container if not running")
        ])
    ]
    step_by_step(steps)

    is_ready = await is_container_ready(project_config.postgres_container_name)
    if is_ready:
        ui_logger.info(f"Container {project_config.postgres_container_name} is already running.")
        return

    compose_file_path = await generate_docker_compose_file(project_config)
    if compose_file_path:
        cmd = f"docker-compose -p {project_config.project_name} -f {compose_file_path} up -d"
        await _run_command_async(cmd)
        ui_logger.info("Containers started.")

async def stop_containers_async(project_name: str):
    steps = [
        Step("Stopping Containers", [
            TextComponent("Executing docker-compose down command")
        ])
    ]
    step_by_step(steps)

    cmd = f"docker-compose -f docker-compose-{project_name}.yml down"
    await _run_command_async(cmd)
    ui_logger.info("Containers stopped.")

async def initialize_with_persistence_check(project_config: ProjectConfig):
    if confirm_action(f"Do you want to initialize the project {project_config.project_name}?"):
        is_ready = await is_container_ready(project_config.postgres_container_name)
        if not is_ready:
            ui_logger.info(f"Container {project_config.postgres_container_name} is not running. Starting containers.")
            await start_containers_async(project_config)
