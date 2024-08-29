from blitzkrieg.ui_management.console_instance import console
import subprocess

from blitzkrieg.utils.validation_utils import validate_file_exists_in_cwd

def initialize_poetry():
    try:
        console.handle_wait("Initializing poetry")

        pyproject_toml_exists_in_cwd = validate_file_exists_in_cwd('pyproject.toml')
        if pyproject_toml_exists_in_cwd:
            console.handle_info("Poetry is already initialized.")
            return
        subprocess.run(["poetry", "init", '--no-interaction'], check=True)
        console.handle_success("Poetry initialized successfully.")
        validate_file_exists_in_cwd('pyproject.toml')
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to initialize poetry: {str(e)}")

def update_project_version(version_num: str):
    try:
        console.handle_wait(f"Updating project version to {version_num}")
        subprocess.run(["poetry", "version", version_num], check=True)
        console.handle_success(f"Updated project version to {version_num}")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to update project version: {str(e)}")

def install_project_dependencies():
    try:
        console.handle_wait("Installing project dependencies")
        subprocess.run(["poetry", "install"], check=True)
        console.handle_success("Installed project dependencies")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to install project dependencies: {str(e)}")

def build_project_package():
    try:
        console.handle_wait("Building project package")
        subprocess.run(["poetry", "build"], check=True)
        console.handle_success("Built project package")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to build project package: {str(e)}")
