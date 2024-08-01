# workspace_directory_manager.py

import os
import subprocess
from blitzkrieg.blitz_env_manager import BlitzEnvManager
from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner

class WorkspaceDirectoryManager:
    def __init__(self, blitz_env_manager: BlitzEnvManager, workspace_name: str = None, console_interface: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.console = console_interface if console_interface else ConsoleInterface()
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.blitz_env_manager: BlitzEnvManager = blitz_env_manager

    def teardown(self):
        return self.delete_workspace_directory()

    def delete_workspace_directory(self):
        try:
            subprocess.run(['rm', '-rf', self.workspace_path], check=True)
            return self.console.handle_success(f"Deleted workspace directory at [white]{self.workspace_path}[/white]")
        except subprocess.CalledProcessError as e:
            return self.console.handle_error(f"Failed to delete workspace directory: {str(e)}")

    def create_dir(self, dir_path):
        os.makedirs(dir_path, exist_ok=True)

    def create_workspace_directory(self):
        try:
            os.makedirs(self.workspace_path, exist_ok=True)
            return self.console.handle_success(f"Created workspace directory at [white]{self.workspace_path}[/white]")
        except Exception as e:
            return self.console.handle_error(f"Failed to create workspace directory: {str(e)}")

    def save_workspace_directory_details_to_env_file(self):
        try:
            self.blitz_env_manager.add_env_var_to_workspace_file('WORKSPACE_PATH', self.workspace_path)
            self.blitz_env_manager.add_env_var_to_workspace_file('IS_WORKSPACE', True)
            self.blitz_env_manager.add_env_var_to_workspace_file('WORKSPACE_NAME', self.workspace_name)
            return self.console.handle_success(f"Saved workspace directory details to .blitz.env file")
        except Exception as e:
            return self.console.handle_error(f"Failed to save workspace directory details to .blitz.env file: {str(e)}")

    def create_projects_directory(self):
        try:
            projects_path = os.path.join(self.workspace_path, 'projects')
            self.create_dir(projects_path)
            return self.console.handle_success(f"Created /projects directory inside workspace at [white]{projects_path}[/white]")
        except Exception as e:
            return self.console.handle_error(f"Failed to create /projects directory: {str(e)}")
