import docker
from docker.errors import NotFound, APIError

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner
import time

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.console = ConsoleInterface()

    @with_spinner(
        message="Creating Docker network...",
        failure_message="Failed to create Docker network.",
        success_message="Docker network created successfully."
    )
    def create_docker_network(self, network_name):
        """Create a Docker network if it doesn't exist."""
        try:
            self.client.networks.get(network_name)
            return True
        except docker.errors.NotFound:
            self.client.networks.create(network_name)
            print(f"Network '{network_name}' created successfully.")
            return False

    @with_spinner(
        message="Waiting for container to be in running state...",
        failure_message="Container did not start successfully.",
        success_message="Container is ready."
    )
    def wait_for_container(self, container_name, timeout=60):
        """Wait for container to be in running state."""
        try:
            for _ in range(timeout):
                container = self.client.containers.get(container_name)
                if container.status == 'running':
                    return True
                time.sleep(1)
            return False
        except NotFound as e:
            return False
