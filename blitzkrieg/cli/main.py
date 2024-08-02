from blitzkrieg.blitz_env_manager import BlitzEnvManager
from blitzkrieg.cli.cli_interface import handle_create_project_command, handle_delete_project_command
import click
from packaging import version as packaging_version
import subprocess
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.workspace_directory_manager import WorkspaceDirectoryManager
from blitzkrieg.workspace_manager import WorkspaceManager
import os

@click.group()
def main():
    pass
@main.command('create-workspace')
@click.argument("workspace_name")
def create_workspace(workspace_name):

    blitz_env_manager = BlitzEnvManager(workspace_name=workspace_name)

    WorkspaceManager(
        workspace_name=workspace_name,
        blitz_env_manager=blitz_env_manager,
    ).blitz_init()

@main.command('delete-workspace')
@click.argument("workspace_name")
def delete_workspace(workspace_name):
    blitz_env_manager = BlitzEnvManager(workspace_name=workspace_name)
    WorkspaceManager(
        workspace_name=workspace_name,
        blitz_env_manager=blitz_env_manager
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
@main.command('release')
@click.option('--version', prompt='New version number', help='The new version number for the release')
def release(version):
    """Set up Poetry and release a new version of Blitzkrieg to PyPI"""
    blitz_env_manager = BlitzEnvManager()

    try:
        # Validate the version number
        packaging_version.parse(version)
    except packaging_version.InvalidVersion:
        click.echo(f"Invalid version number: {version}")
        return

    try:
        # Check if Poetry is installed
        try:
            subprocess.run(["poetry", "--version"], check=True)
        except FileNotFoundError:
            click.echo("Poetry is not installed. Installing Poetry...")
            subprocess.run(["pip", "install", "poetry"], check=True)

        # Initialize Poetry if pyproject.toml doesn't exist
        if not os.path.exists('pyproject.toml'):
            click.echo("Initializing Poetry...")
            subprocess.run(["poetry", "init", "--no-interaction"], check=True)

        # Update the version in pyproject.toml
        subprocess.run(["poetry", "version", version], check=True)

        # Install dependencies
        subprocess.run(["poetry", "install"], check=True)

        # Build the package
        subprocess.run(["poetry", "build"], check=True)

        # Check for PyPI credentials
        pypi_username = "__token__"
        pypi_api_key = blitz_env_manager.get_env_var_value_from_global_env_file('PYPI_API_KEY')
        if not pypi_api_key:
            click.echo("PYPI_API_KEY is not set in the global .blitz.env file. Please set it and try again.")
            return

        # Publish to PyPI
        subprocess.run(["poetry", "publish", "--username", pypi_username, "--password", pypi_api_key], check=True)

        # Create a git tag for the new version
        subprocess.run(["git", "add", "pyproject.toml"], check=True)
        subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
        subprocess.run(["git", "tag", f"v{version}"], check=True)

        # Push the new tag and commit to the remote repository using GitHub CLI
        subprocess.run(["gh", "auth", "status"], check=True)  # Ensure you're authenticated
        subprocess.run(["gh", "repo", "sync"], check=True)  # Sync changes

        click.echo(f"Successfully set up Poetry and released Blitzkrieg version {version} to PyPI!")
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred during the release process: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")
# blitz create-project <project_type='cli' | 'lib'> <project_name> <project_description>
@main.command('create-project')
@click.option('--name', prompt='Project name', help='The name of the project')
@click.option('--description', prompt='Project description', help='A brief description of the project')
def create_project(name, description):
    """Create a new project within the current workspace."""
    try:
        # First, try to get the workspace name from the environment
        blitz_env_manager = BlitzEnvManager()
        workspace_name = blitz_env_manager.get_env_var_value_from_global_env_file('CURRENT_WORKSPACE')

        if not workspace_name:
            click.echo("No current workspace found. Please create or select a workspace first.")
            return

        # Now initialize BlitzEnvManager with the workspace name
        blitz_env_manager = BlitzEnvManager(workspace_name)

        if not blitz_env_manager.workspace_env_file_exists():
            click.echo(f"Workspace environment file not found for '{workspace_name}'. Please ensure the workspace exists.")
            return

        # Rest of your create_project logic here
        click.echo(f"Creating project '{name}' in workspace '{workspace_name}'")
        click.echo(f"Description: {description}")

        # Add your project creation logic here

    except Exception as e:
        click.echo(f"An error occurred while creating the project: {str(e)}")
if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
