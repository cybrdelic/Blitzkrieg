import os
import shutil
import subprocess
import time
from rich.console import Console
from .container_manager import ContainerManager
from ..shared.command_runner import CommandRunner
import socket
from ..cli.ui import print_warning, print_message

console = Console()


class DockerManager:
    def __init__(self):
        self.runner = CommandRunner()

    def is_installed(self):
        return bool(shutil.which('docker'))

    def install(self):
        self.runner.run_command("sudo apt update")
        self.runner.run_command("sudo apt install -y docker.io")
        self.runner.run_command("sudo systemctl start docker")
        self.runner.run_command("sudo systemctl enable docker")

    def pull_image(self, image):
        self.runner.run_command(f"docker pull {image}")

    def container_exists(self, container_name):
        existing_containers = self.runner.run_command(f"docker ps -a -q -f name={container_name}")
        return bool(existing_containers)

    def remove_container(self, container_name):
        self.runner.run_command(f"docker stop {container_name}")
        self.runner.run_command(f"docker rm {container_name}")

class PostgreSQLManager(ContainerManager):
    def start_container(self, password):
        port = self.runner.find_available_port(5432)
        self.runner.run_command(f"docker run --name {self.container_name} -e POSTGRES_PASSWORD={password} -p {port}:{port} -d postgres:latest")
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

class PgAdminManager(ContainerManager):
    def __init__(self, project_name):
        super().__init__(f"{project_name}-PgAdmin")

    def start_container(self, email, password):
        port = self.runner.find_available_port(80)
        self.runner.run_command(f"docker run --name {self.container_name} -p {port}:80 \
            -e 'PGADMIN_DEFAULT_EMAIL={email}' \
            -e 'PGADMIN_DEFAULT_PASSWORD={password}' \
            -d dpage/pgadmin4")
        return port

    def container_exists(self):
        existing_containers = self.runner.run_command(f"docker ps -a -q -f name={self.container_name}")
        return bool(existing_containers)

    def remove_container(self):
        if self.container_exists():
            print_warning(f"Container with name {self.container_name} already exists. Stopping and removing...")
            self.runner.run_command(f"docker stop {self.container_name}")
            self.runner.run_command(f"docker rm {self.container_name}")
            time.sleep(5)  # Give Docker a few seconds to free up the name
