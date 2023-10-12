import os
import shutil
import subprocess
import time
from rich.console import Console
from rundbfast.managers.container_manager import ContainerManager
from rundbfast.shared.command_runner import CommandRunner
import socket
from rundbfast.cli.ui import print_warning, print_message, show_choices, print_success, print_error
import tempfile
import json
console = Console()
from rundbfast.managers.helpers.pgadmin_helper import add_server as add_server_helper


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

    def create_volume(self, volume_name):
        self.runner.run_command(f"docker volume create {volume_name}")

    def volume_exists(self, volume_name):
        existing_volumes = self.runner.run_command(f"docker volume ls -q -f name={volume_name}")
        return bool(existing_volumes)

    def remove_volume(self, volume_name):
        self.runner.run_command(f"docker volume rm {volume_name}")

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




class PgAdminManager(ContainerManager):
    def __init__(self, project_name):
        super().__init__(f"{project_name}-PgAdmin")

    def start_container(self, email, password):
        # Check if the container already exists
        if self.container_exists():
            print_warning(f"Container with name {self.container_name} already exists. Stopping and removing...")
            self.remove_container()

        port = self.runner.find_available_port(80)
        try:
            self.runner.run_command(f"docker run --name {self.container_name} -p {port}:80 \
                -e 'PGADMIN_DEFAULT_EMAIL={email}' \
                -e 'PGADMIN_DEFAULT_PASSWORD={password}' \
                -d my-custom-pgadmin")
            return port
        except subprocess.CalledProcessError as cpe:
            print_error(f"Failed to start the container: {str(cpe)}")
            raise
    def container_exists(self):
        existing_containers = self.runner.run_command(f"docker ps -a -q -f name={self.container_name}")
        return bool(existing_containers)

    def remove_container(self):
        if self.container_exists():
            print_warning(f"Container with name {self.container_name} already exists. Stopping and removing...")
            self.runner.run_command(f"docker stop {self.container_name}")
            self.runner.run_command(f"docker rm {self.container_name}")


            time.sleep(5)  # Give Docker a few seconds to free up the name
    def add_server(self, server_name, db_name, password, pgadmin_email, port):
        add_server_helper(self, server_name, db_name, password, pgadmin_email, port)

    def _servers_config_exists(self):
        check_cmd = f"docker exec {self.container_name} sh -c 'if [ -f /pgadmin4/servers.json ]; then echo exists; else echo not_exists; fi'"
        result = self.runner.run_command(check_cmd).strip()
        return result == "exists"

    def _generate_server_config(self, server_name, db_name, password, port):
        return {
            "Servers": {
                "1": {
                    "Name": server_name,
                    "Group": "Servers",
                    "Host": f"{db_name}-postgres",
                    "Port": port,
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


    def _execute_add_server_command(self, temp_file_path, pgadmin_email):
        # Step 1: Copy the configuration file to the container
        copy_cmd = f"docker cp {temp_file_path} {self.container_name}:/pgadmin4/servers.json"
        self.runner.run_command(copy_cmd)

        # Step 2: Change the permissions of the configuration file inside the container
        chmod_cmd = f"docker exec -u root {self.container_name} chmod 644 /pgadmin4/servers.json"
        self.runner.run_command(chmod_cmd)

        # Step 3: Execute the setup
        setup_cmd = (f"docker exec {self.container_name} /venv/bin/python3 /pgadmin4/setup.py "
                    f"--load-servers /pgadmin4/servers.json --user {pgadmin_email}")
        self.runner.run_command(setup_cmd)

    def _execute_transfer_command(self, temp_file_path):
        """
        Transfers the server configuration from the temporary file to the container and sets its permissions.
        """
        # Step 1: Copy the configuration file to the container
        copy_cmd = f"docker cp {temp_file_path} {self.container_name}:/pgadmin4/servers.json"
        self.runner.run_command(copy_cmd)

        # Step 2: Change the permissions of the configuration file inside the container
        chmod_cmd = f"docker exec -u root {self.container_name} chmod 644 /pgadmin4/servers.json"
        self.runner.run_command(chmod_cmd)
