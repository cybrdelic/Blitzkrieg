from blitzkrieg.core.initialization.docker_manager import DockerManager
from blitzkrieg.core.initialization.pgadmin_manager import PgAdminManager
from blitzkrieg.core.initialization.postgres_manager import WorkspaceDbManager
from blitzkrieg.core.networking.port_allocation import find_available_port
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface


class BlitzkriegInitializer:
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
        self.blitzkrieg_db_manager = WorkspaceDbManager(port=self.postgres_port, workspace_name=self.workspace_name)
        self.docker_network_name = f"{self.workspace_name}-network"

    def setup_db_environment(self):
        self.console.display_step('Docker Network Creation', 'Creating Docker network for Blitzkrieg...')
        self.docker_manager.create_docker_network(self.docker_network_name)
        self.blitzkrieg_db_manager.initialize()
        self.pgadmin_manager.setup_pgadmin()

    def setup_db_schema(self):
        self.console.display_step('Database Schema Initialization', 'Setting up the database schema...')
        self.blitzkrieg_db_manager.setup_schema()
