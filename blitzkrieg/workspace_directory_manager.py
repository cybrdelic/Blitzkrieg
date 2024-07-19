# workspace_directory_manager.py

import os
import subprocess
from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner

class WorkspaceDirectoryManager:
    def __init__(self, db_manager, docker_manager: DockerManager, workspace_name: str = None, console_interface: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.console = console_interface if console_interface else ConsoleInterface()
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager
        self.docker_manager = docker_manager

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

    def create_projects_directory(self):
        try:
            projects_path = os.path.join(self.workspace_path, 'projects')
            self.create_dir(projects_path)
            return self.console.handle_success(f"Created /projects directory inside workspace at [white]{projects_path}[/white]")
        except Exception as e:
            return self.console.handle_error(f"Failed to create /projects directory: {str(e)}")

    def build_workspace_container(self):
        try:
            self.console.handle_wait("Building workspace container...")
            self.console.handle_info(f"Running docker command to build workspace container on the following dir: {self.workspace_path}")
            self.console.execute_command(command=['docker-compose', 'build'], directory=self.workspace_path, message="Building workspace container...")
            self.console.handle_success(f"Built workspace container")
        except subprocess.CalledProcessError as e:
            return self.console.handle_error(f"Failed to build workspace container: {str(e)}")

    def start_workspace_container(self):
        try:
            self.console.execute_command(command=['docker-compose', 'up', '-d'], directory=self.workspace_path, message="Starting workspace container...")
            self.docker_manager.wait_for_container(container_name=f"{self.workspace_name}-postgres")
            self.docker_manager.wait_for_container(container_name=f"{self.workspace_name}-pgadmin")
            self.console.handle_success(f"Started all workspace containers")
        except subprocess.CalledProcessError as e:
            return self.console.handle_error(f"Failed to start workspace container: {str(e)}", error_object=e)
