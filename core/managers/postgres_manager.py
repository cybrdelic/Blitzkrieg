import time
from rundbfast.core.cli.ui import print_label, print_message, print_success, print_warning
from rundbfast.core.managers.container_manager import ContainerManager
from rundbfast.core.managers.helpers.metadb_helper import execute_initial_user_setup
from rundbfast.core.managers.initializers import initialize_pgadmin

# Constants
DEFAULT_PORT = 5432
TIMEOUT = 60
SLEEP_INTERVAL = 2
WAIT_AFTER_CONTAINER_START = 10
WAIT_AFTER_CONTAINER_REMOVE = 5

class PostgreSQLManager(ContainerManager):
    def __init__(self, runner):
        super().__init__(runner)

    def start_container(self, password, volume_name=None):
        port = self.runner.find_available_port(DEFAULT_PORT)
        volume_option = f"-v {volume_name}:/var/lib/postgresql/data" if volume_name else ""
        self.runner.run_command(f"docker run --name {self.container_name} -e POSTGRES_PASSWORD={password} {volume_option} -p {port}:{port} -d postgres:latest")
        time.sleep(WAIT_AFTER_CONTAINER_START)
        return port

    def is_ready(self):
        try:
            output = self.runner.run_command(f"docker exec {self.container_name} pg_isready")
            return "accepting connections" in output
        except Exception as e:
            raise RuntimeError(f"Error checking PostgreSQL readiness: {str(e)}")

    def wait_for_ready(self):
        start_time = time.time()
        while True:
            if self.is_ready():
                return True
            elif time.time() - start_time > TIMEOUT:
                raise TimeoutError("Timed out waiting for PostgreSQL to be ready")
            time.sleep(SLEEP_INTERVAL)

    def database_exists(self, db_name):
        result = self.runner.run_command(f"docker exec {self.container_name} psql -U postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='{db_name}'\"")
        return bool(result)

    def setup_database(self, project_name):
        quoted_project_name = f"\"{project_name}\""
        if not self.database_exists(project_name):
            self.runner.run_command(f"docker exec {self.container_name} psql -U postgres -c 'CREATE DATABASE {quoted_project_name};'")
        self.runner.run_command(f"docker exec {self.container_name} psql -U postgres -d {project_name} -c 'CREATE EXTENSION IF NOT EXISTS cube;'")

    def remove_container(self):
        if self.container_exists():
            print_warning(f"Container with name {self.container_name} already exists. Removing...")
            self.runner.run_command(f"docker stop {self.container_name}")
            self.runner.run_command(f"docker rm {self.container_name}")
            time.sleep(WAIT_AFTER_CONTAINER_REMOVE)

    def initialize_and_start(self, db_name, password, volume_name=None):
        if self.container_exists():
            self.remove_container()
        port = self.start_container(password, volume_name)
        if not self.wait_for_ready():
            raise Exception("Failed to initialize PostgreSQL container.")
        return port
