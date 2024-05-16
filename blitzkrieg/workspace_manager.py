# main_blitzkrieg.py

from blitzkrieg.alembic_manager import AlembicManager
from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.workspace_directory_manager import WorkspaceDirectoryManager
from blitzkrieg.pgadmin_manager import PgAdminManager
from blitzkrieg.postgres_manager import WorkspaceDbManager
from blitzkrieg.ui_management.decorators import with_spinner
from blitzkrieg.utils.port_allocation import find_available_port
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
import os

class WorkspaceManager:
    def __init__(self, workspace_name, console: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.console = console if console else ConsoleInterface()
        self.docker_manager = DockerManager(console=self.console)
        self.postgres_port = find_available_port(5432)
        self.pgadmin_port = find_available_port(5050)
        self.pgadmin_manager = PgAdminManager(
            postgres_port=self.postgres_port,
            pgadmin_port=self.pgadmin_port,
            workspace_name=self.workspace_name,
            console=self.console
        )
        self.workspace_db_manager = WorkspaceDbManager(port=self.postgres_port, workspace_name=self.workspace_name, console=self.console)
        self.workspace_directory_manager = WorkspaceDirectoryManager(workspace_name=self.workspace_name, db_manager=self.workspace_db_manager, console_interface=self.console)
        self.docker_network_name = f"{self.workspace_name}-network"
        self.cwd = os.getcwd()
        self.alembic_manager = AlembicManager(db_manager=self.workspace_db_manager, workspace_name=self.workspace_name, console=self.console)

    def teardown_workspace(self):
        self.console.display_step('Tearing Down Workspace', 'Tearing down Blitzkrieg workspace...')
        self.workspace_db_manager.teardown()
        self.pgadmin_manager.teardown()
        self.docker_manager.remove_docker_network(self.docker_network_name)
        self.workspace_directory_manager.teardown()

    def create_workspace(self):
        self.console.run_tasks(
            tasks=[
                (self.docker_manager.create_docker_network, {'network_name': self.docker_network_name}),
                (self.workspace_db_manager.initialize, {}),
                (self.pgadmin_manager.setup_pgadmin, {}),
                (self.pgadmin_manager.upload_server_configuration, {})
            ],
            title="Container Configuration",
            task_progress_message_map={
                'create_docker_network': "Creating Docker network",
                'initialize': "Initializing PostgreSQL container",
                'setup_pgadmin': "Initializing PgAdmin container",
                'upload_server_configuration': 'Uploading PostgreSQL server configuration to PgAdmin'
            }
        )
        self.setup_workspace()

    def setup_db_schema(self):
        self.console.display_step('Database Schema Initialization', 'Setting up the database schema...')
        self.console.run_tasks(
            tasks=[(self.workspace_db_manager.setup_schema, {})],
            title="Database Schema Initialization",
            task_progress_message_map={'setup_schema': "Setting up database schema"}
        )
        self.workspace_db_manager.setup_schema()

    def setup_workspace(self):
        self.console.run_tasks(
            tasks = [
                (self.workspace_directory_manager.create_workspace_directory, {}),
                (self.workspace_directory_manager.create_projects_directory, {})
            ],
            title ="Workspace Directory Initialization",
            task_progress_message_map={
                'create_workspace_directory': "Creating workspace directory",
                'create_projects_directory': "Creating /projects directory"
            }
        )
        self.alembic_manager.setup_alembic()
