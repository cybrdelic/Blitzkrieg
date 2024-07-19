# workspace_db_manager.py

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
    def __init__(
            self,
            port,
            workspace_name: str = None,
            console: ConsoleInterface = None,
            email=None,
            password=None
    ):
        self.password = password
        self.email = email
        self.workspace_name = workspace_name
        self.db_user = f"{self.workspace_name}-db-user"
        self.db_port = port
        self.network_name = f"{self.workspace_name}-network"
        self.container_name = f"{self.workspace_name}-postgres"
        self.image_name = "postgres:latest"
        self.console_interface = console if console else ConsoleInterface()
        self.docker_manager = DockerManager(console=self.console_interface)


    def initialize(self):
        self.run_postgres_container()
        self.check_postgres_password()

    def test_sqlalchemy_postgres_connection(self):
            # Replace with your actual connection string
        engine = sqlalchemy.create_engine('postgresql+psycopg2://alexfigueroa-db-user:pw@localhost:5432/alexfigueroa')
        try:
            connection = engine.connect()
            print("Database connection was successful!")
            print(connection.execute(sqlalchemy.text("SELECT 1")).scalar())  # Executes a simple query to fetch '1'
        except Exception as e:
            print("Error connecting to the database: ", str(e))
        finally:
            if connection:
                connection.close()

    def teardown(self):
        return self.docker_manager.remove_container(self.container_name)

    def run_postgres_container(self):
        try:
            env_vars = {
                "POSTGRES_DB": self.workspace_name,
                "POSTGRES_USER": self.db_user,
                "POSTGRES_PASSWORD": self.password,
                "POSTGRES_INITDB_ARGS": "--auth-local=md5"
            }
            self.docker_manager.run_container(
                container_name=self.container_name,
                image_name=self.image_name,
                network_name=self.network_name,
                env_vars=env_vars,
                ports={5432: self.db_port},
                volumes={},
                detach=True
            )
            return True
        except Exception as e:
            self.console_interface.handle_error(f"Failed to run PostgreSQL container: {str(e)}")
            return False

    def check_postgres_password(self):
        try:
            time.sleep(1.5)
            connection = self.get_connection_details()
            self.console_interface.spinner.text = (f"Trying to connect to SQLAlchemy engine with password ({self.password}) at {self.get_sqlalchemy_uri()}")
            engine = sqlalchemy.create_engine(self.get_sqlalchemy_uri())
            connection = engine.connect()
            connection.close()
        except Exception as e:
            self.console_interface.handle_error(f"Failed to connect to PostgreSQL during the verification of Postgres password: {str(e)}")
            return False

    def get_connection_details(self):
        return {
            "database": self.workspace_name,
            "user": self.db_user,
            "password": self.password,
            "host": self.container_name,
            "port": self.db_port
        }

    def get_sqlalchemy_uri(self):
        db_uri = f'postgresql+psycopg2://{self.db_user}:{self.password}@{self.workspace_name}-postgres:{self.db_port}/{self.workspace_name}'
        return db_uri

    def setup_schema(self):
        self.console_interface.display_step("Database Schema Initialization")
        self.run_alembic_upgrade()

    def run_alembic_upgrade(self):
        command = ['alembic', 'upgrade', 'head']
        result = run_command(command)
        return result
