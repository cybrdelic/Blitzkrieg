import json
import os
import tarfile
import io
import time
from docker.errors import ContainerError, APIError, NotFound
from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.utils.port_allocation import find_available_port
from blitzkrieg.error_handling.ErrorManager import ErrorManager
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner

class PgAdminManager:
    def __init__(self, postgres_port, pgadmin_port=None, workspace_name: str = None):
        self.docker_manager = DockerManager()
        self.workspace_name = workspace_name
        self.network_name = f"{self.workspace_name}-network"
        self.container_name = f"{self.workspace_name}-pgadmin"
        self.pgadmin_port = pgadmin_port if pgadmin_port else find_available_port()
        self.postgres_port = postgres_port
        self.console_interface = ConsoleInterface()
        self.error_manager = ErrorManager(self.console_interface)
        self.postgres_server_config_name = f"{self.workspace_name.capitalize()} PostgreSQL"
        self.postgres_server_config_host = f"{self.workspace_name}-postgres"
        self.postgres_server_config_username = f"{self.workspace_name}-db-user"
        self.pgadmin_binding_config_path = '/pgadmin4'
        self.pgadmin_login_email = "admin@example.com"
        self.pgadmin_login_password = "admin"

    def teardown(self):
        self.console_interface.display_step("PgAdmin Container Teardown", "Tearing down the PgAdmin container...")
        self.docker_manager.remove_container(self.container_name)
        self.docker_manager.remove_all_volumes()

    def setup_pgadmin(self):
        self.console_interface.display_step("PgAdmin Container Initialization", "Starting the PgAdmin setup process.")
        self.start_pgadmin_container()
        self.docker_manager.wait_for_container(self.container_name)
        self.console_interface.display_step("PgAdmin Server Configuration", "Configuring postgres servers in PgAdmin...")
        self.upload_server_configuration()


        return True

    @with_spinner(
            message="Starting PgAdmin container...",
            failure_message="Failed to start PgAdmin container.",
            success_message="PgAdmin container started successfully."
    )
    def start_pgadmin_container(self):
        try:
            self.docker_manager.client.containers.run(
                "dpage/pgadmin4",
                name=self.container_name,
                ports={'80/tcp': self.pgadmin_port},
                environment={"PGADMIN_DEFAULT_EMAIL": "admin@example.com", "PGADMIN_DEFAULT_PASSWORD": "admin"},
                volumes={f"{self.network_name}_data": {'bind': self.pgadmin_binding_config_path, 'mode': 'rw'}},
                network=self.network_name,
                detach=True
            )
            return True
        except (ContainerError, APIError, NotFound) as e:
            self.error_manager.display_error(f"Failed to start container: {str(e)}")
            return False



    @with_spinner(
        message="Uploading server configuration to PgAdmin...",
        failure_message="Failed to upload server configuration.",
        success_message="Server configuration uploaded successfully."
    )
    def upload_server_configuration(self):
        servers_config = {
            "Servers": {
                "1": {
                    "Name": self.postgres_server_config_name,
                    "Group": "Servers",
                    "Host": self.postgres_server_config_host,
                    "Port": self.postgres_port,
                    "MaintenanceDB": self.workspace_name,
                    "Username": self.postgres_server_config_username,
                    "SSLMode": "prefer"
                }
            }
        }
        try:
            path = f"/pgadmin4/servers.json"
            tar_stream = self.create_tar_stream(json.dumps(servers_config), 'servers.json')
            container = self.docker_manager.client.containers.get(self.container_name)
            container.put_archive(os.path.dirname(path), tar_stream)
            return True
        except Exception as e:
            return False

    def create_tar_stream(self, content, filename):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content.encode()))
        stream.seek(0)
        return stream
