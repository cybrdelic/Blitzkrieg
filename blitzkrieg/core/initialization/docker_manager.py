import docker
from docker.errors import NotFound, APIError

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.console = ConsoleInterface()

    def create_docker_network(self, network_name):
        """Create a Docker network if it doesn't exist."""
        try:
            self.client.networks.get(network_name)
            return True
        except docker.errors.NotFound:
            self.client.networks.create(network_name)
            print(f"Network '{network_name}' created successfully.")
            return False
