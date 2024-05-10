from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.utils.port_allocation import find_available_port
import json

from blitzkrieg.utils.run_command import run_command
import time
from docker.errors import NotFound
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner
import sqlalchemy

class WorkspaceDbManager:
    def __init__(self, port, workspace_name: str =None):
        self.workspace_name = workspace_name
        self.db_user = f"{self.workspace_name}-db-user"
        self.db_password = '0101'
        self.db_port = port
        self.network_name = f"{self.workspace_name}-network"
        self.container_name = f"{self.workspace_name}-postgres"
        self.image_name = "postgres:latest"
        self.console_interface = ConsoleInterface()
        self.docker_manager = DockerManager()

    def initialize(self):
        self.console_interface.display_step("PostgreSQL Container Initialization", "Setting up the PostgreSQL container.")
        self.run_postgres_container()
        self.docker_manager.wait_for_container(self.container_name)
        return self.db_port

    def run_postgres_container(self):
        try:
            env_vars = {
                "POSTGRES_DB": self.workspace_name,
                "POSTGRES_USER": self.db_user,
                "POSTGRES_PASSWORD": self.db_password,
                "POSTGRES_INITDB_ARGS": "--auth-local=md5"
            }
            env_options = " ".join([f"-e {k}={v}" for k, v in env_vars.items()])
            command = (
                f"docker run -d --name {self.container_name} {env_options} "
                f"--network {self.network_name} -p {self.db_port}:5432 {self.image_name}"
            )
            run_command(command)
            return True
        except Exception as e:
            return False
            # After running, consider adding a small delay or check to ensure the database initializes fully before continuing
    # get connection details to genrate the connection string for this database to connection to a session to setup the sqlaclhemy engibne and schema
    def get_connection_details(self):
        return {
            "database": self.workspace_name,
            "user": self.db_user,
            "password": self.db_password,
            "host": self.container_name,
            "port": self.db_port
        }

    def get_sqlalchemy_uri(self):
        db_uri = f'postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.container_name}:{self.db_port}/{self.workspace_name}'
        return db_uri
