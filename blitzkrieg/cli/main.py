
from typing import List
from prompt_toolkit import prompt
import questionary
from sqlalchemy import text
from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager
from rich.console import Console
from rich.table import Table
from rich import box
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Static, Header
from textual import events
from textual.reactive import Reactive
from textual.containers import Container
from blitzkrieg.db.models.project import Project
from blitzkrieg.enums.project_types_enum import ProjectTypesEnum
from blitzkrieg.project_management.db.connection import get_db_session, get_docker_db_session, save_project
from blitzkrieg.utils.git_utils import authenticate_github_cli, commit_staged_files, create_git_tag, stage_files_for_commit, sync_local_changes_to_remote_repository
from blitzkrieg.utils.github_utils import clone_github_repo, create_github_repo, get_github_repo_details, push_project_to_repo
from blitzkrieg.utils.poetry_utils import build_project_package, initialize_poetry, install_project_dependencies, update_project_version
from blitzkrieg.utils.validation_utils import validate_package_installation, validate_version_number
import click
import subprocess
from blitzkrieg.cookie_cutter_manager import CookieCutterManager
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.workspace_manager import WorkspaceManager
import rust_codetextualizer
import os
from prompt_toolkit.completion import WordCompleter

@click.group()
def main():
    pass
@main.command('create-workspace')
@click.argument("workspace_name")
def create_workspace(workspace_name):


    WorkspaceManager(
        workspace_name=workspace_name
    ).blitz_init()

@main.command('delete-workspace')
@click.argument("workspace_name")
def delete_workspace(workspace_name):
    WorkspaceManager(
        workspace_name=workspace_name
    ).teardown_workspace()

@main.command('setup-test')
def setup_test():
    """Run the setup_test_env.sh script."""
    subprocess.run(['../../bash/setup_test_env.sh'], check=True)

@main.command('contextualize')
def contextualize():
    try:
        console.handle_wait("Starting the contextualization process")
        rust_codetextualizer.extract_code_context('blitz_init')

    except Exception as e:
        console.handle_error(f"An error occurred during contextualization: {str(e)}")

@main.command('release')
@click.option('--version', prompt='New version number', help='The new version number for the release')
def release(version):
    """Set up Poetry and release a new version of Blitzkrieg to PyPI"""

    validate_version_number(version)

    try:
        poetry_installation_is_successful = validate_package_installation('poetry')

        if not poetry_installation_is_successful:
            console.handle_error("Poetry installation failed. Check the validate_poetry_installation() function.")

        initialize_poetry()
        update_project_version(version)
        install_project_dependencies()
        build_project_package()


        # Check for PyPI credentials
        pypi_username = "__token__"
        pypi_api_key = blitz_env_manager.get_global_env_var('PYPI_API_KEY')
        if not pypi_api_key:
            blitz_env_manager.set_global_env_var('PYPI_API_KEY', click.prompt("Enter your PyPI API key"))
            pypi_api_key = blitz_env_manager.get_global_env_var('PYPI_API_KEY')

        # Publish to PyPI
        subprocess.run(["poetry", "publish", "--username", pypi_username, "--password", pypi_api_key], check=True)

        # Create a git tag for the new version
        stage_files_for_commit(['pyproject.toml'])
        commit_message = f"Bump version to {version}"
        commit_staged_files(commit_message)
        tag_name = f"v{version}"
        create_git_tag(tag_name)
        # Push the new tag and commit to the remote repository using GitHub CLI
        authenticate_github_cli()
        sync_local_changes_to_remote_repository()

        click.echo(f"Successfully set up Poetry and released Blitzkrieg version {version} to PyPI!")
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred during the release process: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")

import os

# find the difference between two file paths to try to navigate from the first path to the second
def find_path_difference(path1, path2):
    path1 = path1.split(os.path.sep)
    path2 = path2.split(os.path.sep)

    # find the common prefix
    i = 0
    while i < len(path1) and i < len(path2) and path1[i] == path2[i]:
        i += 1

    # find the relative path from path1 to the common prefix
    rel_path = ['..'] * (len(path1) - i)

    # find the relative path from the common prefix to path2
    rel_path += path2[i:]

    return os.path.sep.join(rel_path)

@main.command('set-global-env-var')
def set_global_env_var():
    env_var_name = questionary.text("Enter the name of the environment variable:").ask()
    env_var_value = questionary.text("Enter the value of the environment variable:").ask()

    blitz_env_manager.set_global_env_var(env_var_name, env_var_value)

@main.command('delete-global-env-var')
def delete_global_env_var():
    blitz_env_manager.delete_global_env_var()
class TableViewer(App):
    CSS = """
    DataTable {
        height: 1fr;
    }
    """

    def __init__(self, headers, data):
        super().__init__()
        self.headers = headers
        self.data = data

    def compose(self) -> ComposeResult:
        yield Container(DataTable())
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.headers)
        for row in self.data:
            table.add_row(*[str(cell) for cell in row])

    def on_key(self, event: events.Key) -> None:
        if event.key in ("q", "Q"):
            self.exit()

@main.command('view-tables')
def view_tables():
    session = get_docker_db_session()

    # Fetch schemas
    schemas = session.execute(text("SELECT schema_name FROM information_schema.schemata")).fetchall()
    if not schemas:
        console.handle_error("No schemas found in the database.")
        return

    # Select schema
    schema_select = questionary.select(
        "Select a schema to view:",
        choices=[schema[0] for schema in schemas]
    ).ask()

    if not schema_select:
        console.handle_error("No schema selected. Exiting.")
        return

    # Fetch tables for the selected schema
    tables = session.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{schema_select}'")).fetchall()
    if not tables:
        console.handle_error(f"No tables found in the schema '{schema_select}'.")
        return

    # Select table
    table_select = questionary.select(
        "Select a table to view:",
        choices=[table[0] for table in tables]
    ).ask()

    if not table_select:
        console.handle_error("No table selected. Exiting.")
        return

    # Fetch table data
    try:
        result = session.execute(text(f"SELECT * FROM {schema_select}.{table_select}"))
        columns = result.keys()
        table_data = result.fetchall()
    except Exception as e:
        console.handle_error(f"Error fetching data from table '{table_select}': {str(e)}")
        return

    # Display table information
    console.handle_info(f"Table: {table_select}")
    console.handle_info(f"Rows: {len(table_data)}")
    console.handle_info(f"Columns: {len(columns)}")

    if not table_data:
        console.handle_info("The table is empty.")
        return

    # Launch the TUI
    app = TableViewer(columns, table_data)
    app.run()

    console.handle_info("Table view closed. Press Enter to continue...")
    input()

@main.command('set-workspace')
def set_workspace():
    workspace_name = questionary.text("Enter the name of the workspace:").ask()
    blitz_env_manager.set_global_env_var('CURRENT_WORKSPACE', workspace_name)

@main.command('view-global-env-vars')
def view_global_env_vars():
    global_env_vars = blitz_env_manager.get_global_env_vars()
    console.handle_info("Global environment variables:")
    for key, value in global_env_vars.items():
        console.handle_info(f"{key}: {value}")

@main.command('create-project')
def create_project():
    """Create a new project within the current workspace."""
    project_types = [
        {'name': pt.name.replace('_', ' ').title(), 'value': pt.value}
        for pt in ProjectTypesEnum
    ]

    type = questionary.select(
        "Select project type:",
        choices=project_types
    ).ask()

    project_name = questionary.text("Enter the project name:").ask()
    short_description = questionary.text("Enter a short description for the project (roughly 3-5 words):").ask()
    description = questionary.text("Enter a detailed description for the project:").ask()
    type = type.lower().replace(' ', '_')

    project = Project(
        name=project_name,
        project_type=type,
        short_description=short_description,
        description=description
    )

    try:
        session = get_docker_db_session()
        console.handle_info(f"Starting the create_project command. About to initialize the CookieCutterManager")
        cookie_cutter_manager = CookieCutterManager()
        console.handle_info(f"CookieCutterManager initialized successfully")
        console.handle_info(f"About to get the template path for the project type: {type}")
        template_path = cookie_cutter_manager.get_template_path(type)
        console.handle_info(f"Template path retrieved successfully: {template_path}")
        console.handle_info(f"About to generate the project")
        cookie_cutter_manager.generate_project(
            template_path=template_path,
            project=project
        )
        console.handle_success(f"Successfully created project: {project_name}")
        console.handle_info(f"About to create a GitHub repo")
        create_github_repo(project)
        save_project(project, session)
        console.handle_success(f"Successfully created a GitHub repository for the project: {project_name}")
        push_project_to_repo(project)
    except Exception as e:
        console.handle_error(f"An error occurred while creating the project: {str(e)}")

@main.command('track-project')
# add optional flag to allow the user to attach a repo_url to clone the project from
@click.option('--repo_url', prompt='Enter the project repository URL', help='The URL of the project repository')
def track_project(repo_url):
    """Track a project within the current workspace."""
    if repo_url:
        project_github_repo_details = get_github_repo_details(repo_url)
    else:
        project_github_repo_details = get_github_repo_details()

    project_name = project_github_repo_details['name']

    if repo_url:
        project_github_repo_details['url'] = repo_url

    project = Project(
        name=project_name,
        github_repo=project_github_repo_details['url'],
        description=project_github_repo_details['description']

    )

    try:
        session = get_docker_db_session()
        save_project(project, session)
        console.handle_success(f"Successfully tracked project: {project_name}")
    except Exception as e:
        console.handle_error(f"An error occurred while tracking the project: {str(e)}")

    clone_github_repo(project_github_repo_details['url'])

if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
