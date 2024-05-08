from blitzkrieg.core.initialization.docker_manager import DockerManager
from blitzkrieg.core.networking.port_allocation import find_available_port
import json

from blitzkrieg.core.shared.run_command import run_command
import time
from docker.errors import NotFound
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner

class BlitzkriegDbManager:
    def __init__(self, port):
        self.project_name = "blitzkrieg"  # Hardcoded project name
        self.db_user = 'blitzkrieg-db-user'
        self.db_password = '0101'
        self.db_port = port
        self.network_name = f"{self.project_name}-network"
        self.container_name = f"{self.project_name}-postgres"
        self.image_name = "postgres:latest"
        self.console_interface = ConsoleInterface()
        self.docker_manager = DockerManager()

    def initialize(self):
        self.console_interface.display_step("PostgreSQL Container Initialization", "Setting up the PostgreSQL container.")
        self.run_postgres_container()
        self.wait_for_container()
        return self.db_port

    def run_postgres_container(self):
        try:
            env_vars = {
                "POSTGRES_DB": self.project_name,
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
    @with_spinner(
        message="Waiting for Postgres container to be in running state...",
        failure_message="Container did not start successfully.",
        success_message="Container is ready."
    )
    def wait_for_container(self, timeout=60):
        """Wait for container to be in running state."""
        try:
            for _ in range(timeout):
                container = self.docker_manager.client.containers.get(self.container_name)
                if container.status == 'running':
                    return True
                time.sleep(1)
            return False
        except NotFound as e:
            self.error_manager.display_error(f"Container not found: {str(e)}")
            return False
