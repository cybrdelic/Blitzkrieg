
from rundbfast.cli.ui import print_error, print_header, print_message, print_success, print_warning, show_progress
from rundbfast.cli.user_input import get_postgres_password
from rundbfast.managers.initializers import DOCKER_IMAGE_POSTGRES
from rundbfast.managers.manager import PostgreSQLManager
from rundbfast.shared.utils import wait_for_container


class PostgreSQLInitializer:
    def __init__(self, docker, project_name):
        self.docker = docker
        self.project_name = project_name
        self.container_name = f"{project_name}-postgres"
        self.volume_name = f"{project_name}-postgres-volume"
        self.pg_password = None
        self.used_port = None
        self.postgres = None

    def initialize(self):
        self._print_initialization_header()
        self._get_postgres_password()
        self._ensure_postgres_image()
        self._handle_existing_container()
        self._ensure_data_persistence_volume()
        self._start_postgresql_container()
        self._wait_and_setup_database()
        return self.postgres, self.pg_password, self.used_port

    def _print_initialization_header(self):
        print_header("PostgreSQL Initialization")

    def _get_postgres_password(self):
        self.pg_password = get_postgres_password()

    def _ensure_postgres_image(self):
        if not self.docker.image_exists(DOCKER_IMAGE_POSTGRES):
            with show_progress(f"Pulling {DOCKER_IMAGE_POSTGRES}...") as progress:
                self.docker.pull_image(DOCKER_IMAGE_POSTGRES)
                progress.update(100)
                print_success(f"{DOCKER_IMAGE_POSTGRES} pulled successfully!")

    def _handle_existing_container(self):
        if self.docker.container_exists(self.container_name):
            is_running = self.docker.is_container_running(self.container_name)

            if is_running:
                # Check container's state, configuration, etc.
                container_info = self.docker.inspect_container(self.container_name)
                # Based on container_info, decide whether to proceed or not
                user_confirmation = input(f"Container {self.container_name} is running. Do you want to remove it? (yes/no): ")
                if user_confirmation.lower() != 'yes':
                    print("Operation aborted by the user.")
                    return

            # Backup logic here (if it's a database or data container)

            print_warning(f"Removing container {self.container_name}...")
            self.docker.remove_container(self.container_name)

            # Restore logic here (if backups were taken)

    def _ensure_data_persistence_volume(self):
        if not self.docker.volume_exists(self.volume_name):
            self.docker.create_volume(self.volume_name)

    def _start_postgresql_container(self):
        self.postgres = PostgreSQLManager(self.container_name)
        print_message(f"Starting container {self.container_name} with data persistence...")
        self.used_port = self.postgres.start_container(self.pg_password, self.volume_name)

    def _wait_and_setup_database(self):
        if wait_for_container(self.docker, self.container_name):
            print_success(f"PostgreSQL is now running with data persistence on port {self.used_port}.")
            self.postgres.setup_database(self.project_name)
        else:
            print_error(f"Failed to start the {self.container_name} container.")
