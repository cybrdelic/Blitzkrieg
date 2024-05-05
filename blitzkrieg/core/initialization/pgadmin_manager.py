import json
import os
import tarfile
import io
from docker.errors import ContainerError, APIError, NotFound

from blitzkrieg.core.initialization.docker_manager import DockerManager
from blitzkrieg.core.networking.port_allocation import find_available_port
from blitzkrieg.error_handling.ErrorManager import ErrorManager
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class PgAdminManager:
    def __init__(self, postgres_port, pgadmin_port=None):
        self.docker_manager = DockerManager()
        self.network_name = 'blitzkrieg-network'
        self.container_name = "blitzkrieg-pgadmin"
        self.pgadmin_port = pgadmin_port if pgadmin_port else find_available_port(5050)
        self.postgres_port = postgres_port
        self.error_manager = ErrorManager(ConsoleInterface())

    def setup_pgadmin(self):
        if not self.start_pgadmin_container():
            return False
        if not self.upload_server_configuration():
            return False
        self.error_manager.display_success("PgAdmin setup completed successfully.")
        return True

    def start_pgadmin_container(self):
        try:
            self.docker_manager.create_docker_network(self.network_name)
            container = self.docker_manager.client.containers.run(
                "dpage/pgadmin4",
                name=self.container_name,
                ports={'80/tcp': self.pgadmin_port},
                environment={"PGADMIN_DEFAULT_EMAIL": "admin@example.com", "PGADMIN_DEFAULT_PASSWORD": "admin"},
                volumes={f"{self.network_name}_data": {'bind': '/pgadmin4', 'mode': 'rw'}},
                network=self.network_name,
                detach=True
            )
            self.error_manager.display_success("pgAdmin container started successfully.")
            return True
        except (ContainerError, APIError, NotFound) as e:
            self.error_manager.display_error(f"Failed to start container: {str(e)}")
            return False

    def upload_server_configuration(self):
        servers_config = {
            "Servers": {
                "1": {
                    "Name": "Blitzkrieg PostgreSQL",
                    "Group": "Servers",
                    "Host": "blitzkrieg-postgres",
                    "Port": self.postgres_port,
                    "MaintenanceDB": "blitzkrieg",
                    "Username": "blitzkrieg-db-user",
                    "SSLMode": "prefer"
                }
            }
        }
        try:
            path = '/pgadmin4/servers.json'
            tar_stream = self.create_tar_stream(json.dumps(servers_config), 'servers.json')
            container = self.docker_manager.client.containers.get(self.container_name)
            container.put_archive(os.path.dirname(path), tar_stream)
            self.error_manager.display_success("Server configuration uploaded successfully.")
            return True
        except Exception as e:
            self.error_manager.display_error(f"Failed to upload server configuration: {str(e)}")
            return False

    def create_tar_stream(self, content, filename):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content.encode()))
        stream.seek(0)
        return stream
