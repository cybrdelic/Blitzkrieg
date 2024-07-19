
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
