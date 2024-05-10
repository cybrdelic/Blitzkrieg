from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.workspace_directory_manager import WorkspaceDirectoryManager
from blitzkrieg.pgadmin_manager import PgAdminManager
from blitzkrieg.postgres_manager import WorkspaceDbManager
from blitzkrieg.ui_management.decorators import with_spinner
from blitzkrieg.utils.port_allocation import find_available_port
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
import os


class WorkspaceManager:
    def __init__(self, workspace_name):
        self.workspace_name = workspace_name
        self.console = ConsoleInterface()
        self.docker_manager = DockerManager()
        self.postgres_port = find_available_port(5432)
        self.pgadmin_port = find_available_port(5050)
        self.pgadmin_manager = PgAdminManager(
            postgres_port=self.postgres_port,
            pgadmin_port=self.pgadmin_port,
            workspace_name=self.workspace_name
        )
        self.workspace_db_manager = WorkspaceDbManager(port=self.postgres_port, workspace_name=self.workspace_name)
        self.workspace_directory_manager = WorkspaceDirectoryManager(workspace_name=self.workspace_name, db_manager=self.workspace_db_manager)
        self.docker_network_name = f"{self.workspace_name}-network"
        self.cwd = os.getcwd()

    def teardown_workspace(self):
        self.console.display_step('Tearing Down Workspace', 'Tearing down Blitzkrieg workspace...')
        self.workspace_db_manager.teardown()
        self.pgadmin_manager.teardown()
        self.docker_manager.remove_docker_network(self.docker_network_name)
        self.workspace_directory_manager.teardown()

    def create_workspace(self):

        self.console.display_step('Docker Network Creation', 'Creating Docker network for Blitzkrieg...')
        self.docker_manager.create_docker_network(self.docker_network_name)
        self.workspace_db_manager.initialize()
        self.pgadmin_manager.setup_pgadmin()
        self.console.display_step('Creating Workspace Directory', 'Creating workspace directory for Blitzkrieg...')
        self.setup_workspace()

    def setup_db_schema(self):
        self.console.display_step('Database Schema Initialization', 'Setting up the database schema...')
        self.workspace_db_manager.setup_schema()

    def setup_workspace(self):
        self.workspace_directory_manager.create_workspace_directory()
        self.workspace_directory_manager.create_projects_directory()
        self.workspace_directory_manager.setup_alembic()
        self.workspace_directory_manager.create_sqlalchemy_models_directory()
