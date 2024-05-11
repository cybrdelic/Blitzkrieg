import os

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner
import subprocess
import time

from blitzkrieg.utils.run_command import run_command

class WorkspaceDirectoryManager:
    def __init__(self, db_manager, workspace_name: str = None):
        self.workspace_name = workspace_name
        self.console = ConsoleInterface()
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager

    def teardown(self):
        self.console.display_step('Tearing Down Workspace Directory', 'Tearing down workspace directory...')
        self.delete_workspace_directory()

    @with_spinner(
        message="Deleting workspace directory ...",
        failure_message="Failed to delete workspace directory.",
        success_message="Workspace directory deleted successfully."
    )
    def delete_workspace_directory(self):
        try:
            subprocess.run(['rm', '-rf', self.workspace_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.console.display_notice(f"Failed to delete workspace directory: {str(e)}")
            return False

    def create_dir(self, dir_path):
        os.makedirs(dir_path, exist_ok=True)

    @with_spinner(
        message="Creating workspace directory ...",
        failure_message="Failed to create workspace directory.",
        success_message="Workspace directory created successfully."
    )
    def create_workspace_directory(self):
        try:
            os.makedirs(self.workspace_path, exist_ok=True)
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create workspace directory: {str(e)}")
            return False

    @with_spinner(
        message="Creating /projects directory inside of workspace",
        failure_message="Failed to create /projects directory inside of workspace.",
        success_message="/projects directory created successfully."
    )
    def create_projects_directory(self):
        try:
            projects_path = os.path.join(self.workspace_path, 'projects')
            self.create_dir(projects_path)
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create /projects directory inside of workspace: {str(e)}")
            return False
    
