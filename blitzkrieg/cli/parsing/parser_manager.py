import inquirer
import asyncio
from blitzkrieg.cli.inquiries import get_initial_answer, get_project_init_confirmation
from blitzkrieg.core.managers.postgres.postgres_manager import (
    initialize_with_persistence_check,
    stop_containers_async,
)
from blitzkrieg.core.shared.utils.config import generate_project_config, ProjectConfig, get_project_config_from_inquirer
from blitzkrieg.cli.logging_config import setup_logging
from blitzkrieg.cli.ui_utils import confirm_action, handle_error, display_info

ui_logger, backend_logger, console = setup_logging()

def run():
    command = get_initial_answer()
    handle_new_project_flow(command)
    handle_stop_containers_flow(command)

def handle_init_blitzkrieg_flow(command: str):
    if command == 'Initialize Blitzkrieg':
        

def handle_new_project_flow(command: str):
    if command == 'Start a new project':
        project_config = get_project_config_from_inquirer()
        project_init_confirmation = get_project_init_confirmation(project_config.project_name)

        if project_init_confirmation == 'Yes':
                initialize_with_persistence_check(project_config=project_config)

def handle_stop_containers_flow(command: str):
    if command == 'Stop containers':
        stop_containers_async()
