import json
import tempfile
import time
from config import load_configurations
from cli.ui import print_error, print_warning
from core.managers.container_manager import ContainerManager
from core.shared.command_runner import CommandRunner
import subprocess

# Load configurations
config = load_configurations()

class PgAdminManager(ContainerManager):
    def __init__(self, project_name: str):
        super().__init__(f"{project_name}-PgAdmin")
        self.runner = CommandRunner()

    def start_container(self, email: str, password: str) -> int:
        if self.container_exists():
            self.remove_container()

        port = self.runner.find_available_port(80)
        self._run_container(email, password, port)
        return port

    def _run_container(self, email: str, password: str, port: int):
        try:
            self.runner.run_command(
                f"docker run --name {self.container_name} -p {port}:80 "
                f"-e 'PGADMIN_DEFAULT_EMAIL={email}' "
                f"-e 'PGADMIN_DEFAULT_PASSWORD={password}' "
                "-d my-custom-pgadmin"
            )
        except subprocess.CalledProcessError as cpe:
            print_error(f"Failed to start the container: {str(cpe)}")
            raise

    def remove_container(self):
        self.stop_and_remove_container()
        time.sleep(config.get("WAIT_AFTER_CONTAINER_REMOVE", 5))

    def stop_and_remove_container(self):
        self.runner.run_command(f"docker stop {self.container_name}")
        self.runner.run_command(f"docker rm {self.container_name}")

    def add_server(self, server_name: str, db_name: str, password: str, pgadmin_email: str, port: int):
        if not self._servers_config_exists():
            server_config = self._generate_server_config(server_name, db_name, password, port)
            temp_file_path = self._write_server_config_to_temp_file(server_config)
            self._execute_transfer_command(temp_file_path)
            self._execute_add_server_command(temp_file_path, pgadmin_email)

    def _servers_config_exists(self) -> bool:
        check_cmd = f"docker exec {self.container_name} sh -c 'if [ -f /pgadmin4/servers.json ]; then echo exists; else echo not_exists; fi'"
        return self.runner.run_command(check_cmd).strip() == "exists"

    def _generate_server_config(self, server_name: str, db_name: str, password: str, port: int) -> dict:
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

    def _write_server_config_to_temp_file(self, server_config: dict) -> str:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
            json.dump(server_config, f)
            return f.name

    def _execute_add_server_command(self, temp_file_path: str, pgadmin_email: str):
        self._execute_transfer_command(temp_file_path)
        setup_cmd = (f"docker exec {self.container_name} /venv/bin/python3 /pgadmin4/setup.py "
                     f"--load-servers /pgadmin4/servers.json --user {pgadmin_email}")
        self.runner.run_command(setup_cmd)

    def _execute_transfer_command(self, temp_file_path: str):
        copy_cmd = f"docker cp {temp_file_path} {self.container_name}:/pgadmin4/servers.json"
        self.runner.run_command(copy_cmd)
        chmod_cmd = f"docker exec -u root {self.container_name} chmod 644 /pgadmin4/servers.json"
        self.runner.run_command(chmod_cmd)
