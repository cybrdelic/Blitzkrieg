import time
from rundbfast.core.cli.ui import print_label, print_message, print_success, print_warning
from rundbfast.core.cli.user_input import get_persistence_choice
from rundbfast.core.managers.container_manager import ContainerManager
from rundbfast.core.managers.helpers.metadb_helper import execute_initial_user_setup
from rundbfast.core.managers.initializers import initialize_pgadmin


class PostgreSQLManager(ContainerManager):
    def start_container(self, password, volume_name=None):
        port = self.runner.find_available_port(5432)
        volume_option = f"-v {volume_name}:/var/lib/postgresql/data" if volume_name else ""
        self.runner.run_command(f"docker run --name {self.container_name} -e POSTGRES_PASSWORD={password} {volume_option} -p {port}:{port} -d postgres:latest")
        time.sleep(10)  # Give Docker some time to initialize the container
        return port

    def is_ready(self):
        try:
            output = self.runner.run_command(f"docker exec {self.container_name} pg_isready")
            return "accepting connections" in output
        except:
            return False

    def wait_for_ready(self, timeout=60):
        start_time = time.time()
        while True:
            if self.is_ready():
                return True
            elif time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for PostgreSQL to be ready")
            time.sleep(2)

    def database_exists(self, db_name):
        result = self.runner.run_command(f"docker exec {self.container_name} psql -U postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='{db_name}'\"")
        return bool(result)

    def setup_database(self, project_name):
        # Quote the project name to handle reserved keywords
        quoted_project_name = f"\"{project_name}\""
        if not self.database_exists(project_name):
            self.runner.run_command(f"docker exec {self.container_name} psql -U postgres -c 'CREATE DATABASE {quoted_project_name};'")
        self.runner.run_command(f"docker exec {self.container_name} psql -U postgres -d {project_name} -c 'CREATE EXTENSION IF NOT EXISTS cube;'")

    def container_exists(self):
        existing_containers = self.runner.run_command(f"docker ps -a -q -f name={self.container_name}")
        return bool(existing_containers)

    def remove_container(self):
        if self.container_exists():
            print_warning(f"Container with name {self.container_name} already exists. Stopping and removing...")
            self.runner.run_command(f"docker stop {self.container_name}")
            self.runner.run_command(f"docker rm {self.container_name}")
            time.sleep(5)  # Give Docker a few seconds to free up the name

    def ensure_data_persistence(self, password):
        self.remove_container()
        print_message("Setting up Docker volume for data persistence...")
        # Add any extensions or initial setup for the meta database here.

    def execute_sql(self, db_name, sql):
        self.runner.run_command(f"docker exec meta-postgres psql -U postgres -d meta -c \"{sql}\"")

    def admin_user_exists(self, db_name):
        try:
            result = self.execute_sql(db_name, "SELECT COUNT(*) FROM users WHERE username LIKE '%-ADMIN';")
            return int(result) > 0
        except:
            return False

    def get_admin_email(self, db_name):
        try:
            email = self.execute_sql(db_name, "SELECT email FROM users WHERE username LIKE '%-ADMIN' LIMIT 1;")
            return email.strip()
        except:
            return None

    def initialize_and_start(self, db_name, password, volume_name=None):
        if self.container_exists():
            self.remove_container()
        self.ensure_data_persistence(password)
        port = self.start_container(password, volume_name)
        if not self.wait_for_ready():
            raise Exception("Failed to initialize PostgreSQL container.")
        return port

    def setup_meta_database(self, docker, db_name='meta'):
        pg_password = self.initialize_and_start(db_name, 'password')  # Choose an appropriate password or get it from the user
        pgadmin, pgadmin_email = initialize_pgadmin(db_name, self)
        pgadmin.add_server('RunDBFast Meta Server', db_name, pg_password, pgadmin_email, self.port)
        execute_initial_user_setup(db_name, self, email=pgadmin_email, password=pg_password)

    def initialize_with_persistence_check(self, project_name):
        persist_data = get_persistence_choice()
        if persist_data == 'Yes':
            print_label("Ensuring data persistence...")
            self.initialize_and_start(project_name, 'password')  # Choose an appropriate password or get it from the user
            print_success(f"PostgreSQL is now running with data persistence enabled.")
