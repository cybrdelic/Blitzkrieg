
from typing import List
from prompt_toolkit import prompt
import questionary
from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager

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

# @main.command("show")
# @click.argument("workspace_name")
# def show(workspace_name):
#     WorkspaceManager(workspace_name=workspace_name, console=console_interface, email="dfsfdsd", password='').show_workspace_details()

# @main.command('delete')
# @click.argument('entity_type')
# def delete(entity_type):
#     if entity_type == 'project':
#         handle_delete_project_command()
#     if entity_type == 'issue':
#         pass

@main.command('setup-test')
def setup_test():
    """Run the setup_test_env.sh script."""
    subprocess.run(['../../bash/setup_test_env.sh'], check=True)

# @main.command('view')
# @click.option('--model_name', prompt="Enter the model name", help="The name of the model to view tables")
# def view(model_name):
#     """View the table of the specified model"""
#     # check if cwd contains a blitz.env file
#     try:
#         env_file = open('blitz.env','r')
#         if env_file:


# @main.command('create')
# def create_project():
#     handle_create_project_command()import os

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
# blitz create-project <project_type='cli' | 'lib'> <project_name> <project_description>
from cookiecutter.main import cookiecutter
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
