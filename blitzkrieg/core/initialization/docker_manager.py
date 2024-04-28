import docker
from docker.errors import NotFound, APIError

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def does_docker_network_exist(self, network_name):
        """Check if a Docker network exists."""
        try:
            self.client.networks.get(network_name)
            return True
        except NotFound:
            return False
        except APIError as e:
            print(f"API error occurred: {e}")
            return False

    def create_docker_network(self, network_name):
        """Create a Docker network."""
        if not self.does_docker_network_exist(network_name):
            try:
                self.client.networks.create(network_name)
                print(f"Network '{network_name}' created successfully.")
            except APIError as e:
                print(f"Failed to create network '{network_name}': {e}")
        else:
            print(f"Network '{network_name}' already exists.")
