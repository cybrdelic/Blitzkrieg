import os
import shutil
import subprocess
import time
from rich.console import Console
from .container_manager import ContainerManager
from ..shared.command_runner import CommandRunner
import socket
from ..cli.ui import print_warning, print_message, show_choices, print_success, print_error
import tempfile
import json
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

    def is_container_running(self, container_name):
        output = self.runner.run_command(f"docker inspect -f '{{{{.State.Running}}}}' {container_name}")
        return output == 'true'

    def image_exists(self, image_name):
        images = self.runner.run_command("docker images -q " + image_name)
        return bool(images)

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
        # Add any extensions or initial setup for the meta database here.

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
    def add_server(self, server_name, db_name, password, pgadmin_email):
        try:
            self._install_flask_if_needed()
            # Check if the servers.json already exists in the container
            if self._servers_config_exists():
                choice = show_choices("servers.json already exists in the container. Overwrite?", ["Yes", "No"])
                if choice == "No":
                    print_warning("Server addition aborted by user.")
                    return

            # Generate server configuration
            server_config = self._generate_server_config(server_name, db_name, password)

            # Write the configuration to a temporary file
            temp_file_path = self._write_server_config_to_temp_file(server_config)

            # Transfer the configuration to the container and execute the setup
            self._execute_add_server_command(temp_file_path, pgadmin_email)

            print_success(f"Server '{server_name}' added to pgAdmin successfully!")

        except subprocess.CalledProcessError as cpe:
            print_error(f"Command execution failed: {str(cpe)}")
        except Exception as e:
            print_error(f"Error adding server: {str(e)}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def _servers_config_exists(self):
        check_cmd = f"docker exec {self.container_name} sh -c 'if [ -f /pgadmin4/servers.json ]; then echo exists; else echo not_exists; fi'"
        result = self.runner.run_command(check_cmd).strip()
        return result == "exists"

    def _generate_server_config(self, server_name, db_name, password):
        return {
            "Servers": {
                "1": {
                    "Name": server_name,
                    "Group": "Servers",
                    "Host": "localhost",
                    "Port": 5432,
                    "MaintenanceDB": db_name,
                    "Username": "postgres",
                    "Password": password,
                    "SSLMode": "prefer",
                    "UseSSHTunnel": 0
                }
            }
        }

    def _check_and_get_existing_servers(self):
        check_cmd = f"docker exec {self.container_name} sh -c 'if [ -f /pgadmin4/servers.json ]; then echo exists; else echo not_exists; fi'"
        result = self.runner.run_command(check_cmd).strip()
        print(f"Result from _check_and_get_existing_servers: {result}")
        if result not in ["exists", "not_exists"]:
            raise Exception(f"Unexpected result from _check_and_get_existing_servers: {result}")
        return result


    def _write_server_config_to_temp_file(self, server_config):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
            json.dump(server_config, f)
            return f.name

    def _install_flask_if_needed(self):
        try:
            # Try to list Flask in installed packages
            cmd = f"docker exec {self.container_name} pip list | grep Flask"
            output = self.runner.run_command(cmd).strip()

            # If Flask is not listed, install it
            if not output:
                install_cmd = f"docker exec {self.container_name} pip install Flask"
                self.runner.run_command(install_cmd)
        except subprocess.CalledProcessError as cpe:
            print_error(f"Failed to check/install Flask: {str(cpe)}")

    def _execute_add_server_command(self, temp_file_path, pgadmin_email):
        cmd = f"docker cp {temp_file_path} {self.container_name}:/pgadmin4/servers.json && docker exec {self.container_name} python3 /pgadmin4/setup.py --load-servers /pgadmin4/servers.json --user {pgadmin_email}"
        self.runner.run_command(cmd)
