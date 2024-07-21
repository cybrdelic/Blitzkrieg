from blitzkrieg.file_writers.base_docker_compose_writer import BaseDockerComposeWriter
from blitzkrieg.pgadmin_manager import PgAdminManager
from blitzkrieg.postgres_manager import WorkspaceDbManager
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.utils.port_allocation import find_available_port

class WorkspaceDockerComposeWriter(BaseDockerComposeWriter):
    def __init__(self, workspace_name: str, workspace_path: str, console: ConsoleInterface, pgadmin_manager: PgAdminManager, postgres_manager: WorkspaceDbManager):
        super().__init__(console=console, path=workspace_path)
        self.workspace_name = workspace_name
        self.network_name = f"{self.workspace_name}-network"
        self.volumes = {
            'postgres_data': None,
            'pgadmin_data': None,
        }
        self.console = console
        self.pgadmin = pgadmin_manager
        self.postgres: WorkspaceDbManager = postgres_manager
        self.initialize_services()

    def add_service(self, name: str, service_config: dict):
        return super().add_service(name, service_config)

    def initialize_services(self):
        self.add_service(
            name=f"{self.workspace_name}-postgres",
            service_config={
                'image': 'postgres:latest',
                'container_name': f"{self.workspace_name}-postgres",
                'environment': {
                    'POSTGRES_DB': self.workspace_name,
                    'POSTGRES_USER': f"{self.workspace_name}-db-user",
                    'POSTGRES_PASSWORD': 'pw'
                },
                'ports': [f"{self.postgres.db_port}:{self.postgres.db_port}"],
                'volumes': ['postgres_data:/var/lib/postgresql/data'],
                'networks': [self.network_name],
                'healthcheck': {
                    'test': ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}'],
                    'interval': '10s',
                    'timeout': '5s',
                    'retries': 5
                }
            }
        )
        self.add_service(
            name=f"{self.workspace_name}-pgadmin",
            service_config={
                'image': 'dpage/pgadmin4:latest',
                'container_name': f"{self.workspace_name}-pgadmin",
                'environment': {
                    'PGADMIN_DEFAULT_EMAIL': 'alexfigueroa.cybr@gmail.com',
                    'PGADMIN_DEFAULT_PASSWORD': 'pw'
                },
                'volumes': [
                    'pgadmin_data:/var/lib/pgadmin',
                    f"{self.pgadmin.servers_config_path}:/pgadmin4/servers.json:ro"
                ],
                'networks': [self.network_name],
                'ports': [
                    f"{self.pgadmin.pgadmin_port}:80",
                    f"{self.pgadmin.pgadmin_port_2}:{self.pgadmin.pgadmin_port_2}"]
            }
        )
        self.add_service(
            name=f"{self.workspace_name}-alembic-worker",
            service_config={
                'build': {
                    'context': '.',
                    'dockerfile': 'Dockerfile'
                },
                'container_name': f"{self.workspace_name}-alembic-worker",
                'environment': {
                    'ALEMBIC_CONFIG': '/app/alembic.ini',
                    'POSTGRES_USER': f"{self.workspace_name}-db-user",
                    'POSTGRES_PASSWORD': 'pw',
                    'POSTGRES_DB': self.workspace_name,
                    'POSTGRES_HOST': f"{self.workspace_name}-postgres"
                },
                'volumes': ['.:/app'],
                'networks': [self.network_name],
                'depends_on': {
                    f"{self.workspace_name}-postgres": {
                        'condition': 'service_healthy'
                    }
                }
            }
        )
        for volume in self.volumes.keys():
            self.add_volume(volume)
        self.add_network(self.network_name, {'external': True})

import yaml
import os
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class BaseDockerComposeWriter:
    def __init__(self, console: ConsoleInterface, path: str, version: str = '3.8'):
        self.path = path
        self.version = version
        self.services = {}
        self.volumes = {}
        self.networks = {}
        self.console = console

    def add_service(self, name: str, service_config: dict):
        self.services[name] = service_config

    def add_volume(self, name: str, volume_config: dict = None):
        self.volumes[name] = volume_config

    def add_network(self, name: str, network_config: dict = None):
        self.networks[name] = network_config

    def write_docker_compose_file(self):
        compose_content = {
            'version': self.version,
            'services': self.services,
            'volumes': self.volumes,
            'networks': self.networks,
        }

        compose_path = os.path.join(self.path, 'docker-compose.yml')
        self.console.handle_wait(f"Writing docker-compose.yml to {compose_path}")
        with open(compose_path, 'w') as file:
            yaml.dump(compose_content, file, default_flow_style=False)
        self.console.handle_success(f"docker-compose.yml written to {compose_path}")
        self.console.display_file_content(compose_path)
