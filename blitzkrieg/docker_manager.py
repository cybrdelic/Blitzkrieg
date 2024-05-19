# docker_manager.py

import docker
from docker.errors import NotFound, APIError
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner
import time

class DockerManager:
    def __init__(self, console: ConsoleInterface = None):
        self.client = docker.from_env()
        self.console = console if console else ConsoleInterface()

    def create_docker_network(self, network_name):
        """Create a Docker network if it doesn't exist."""
        try:
            self.client.networks.create(network_name)
            return self.console.handle_success(f"Network '{network_name}' created successfully.")

        except Exception as e:
            return self.console.handle_error(f"Failed to create network: {str(e)}")


    def wait_for_container(self, container_name, timeout=10000000000):
        """Wait for container to be in running state."""
        try:
            for _ in range(timeout):
                container = self.client.containers.get(container_name)
                if container.status == 'running':
                    success_message = f"Container [white]{container_name}[/white] is running at {container.attrs['NetworkSettings']['IPAddress']} on port {container.attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']}"
                    return self.console.handle_success(success_message)
                time.sleep(1)
        except NotFound as e:
            return self.console.handle_error(f"Container {container_name} not found.")
        except APIError as e:
            return self.console.handle_error(f"Failed to get container status: {str(e)}")
        except Exception as e:
            message =  f"Failed to wait for container '{container_name}': {str(e)}"
            return self.console.handle_error(message)

    def remove_container(self, container_name):
        """Remove a Docker container."""
        try:
            self.console.log(f"Removing container {container_name}...")
            container = self.client.containers.get(container_name)
            container.remove(force=True)
            return True
        except NotFound as e:
            self.console.log(f"Container {container_name} not found.")
            return False

    def remove_volume(self, volume_name):
        """Remove a Docker volume."""
        try:
            self.console.log(f"Removing volume {volume_name}...")
            volume = self.client.volumes.get(volume_name)
            volume.remove()
            return True
        except NotFound as e:
            self.console.log(f"Volume {volume_name} not found.")
            return False

    def remove_all_volumes(self):
        """Remove all Docker volumes."""
        try:
            self.console.display_step("Removing all volumes", "Removing all Docker volumes...")
            for volume in self.client.volumes.list():
                self.console.log(f"Removing volume {volume.name}...")
                volume.remove()
            return True
        except NotFound as e:
            self.console.log("No volumes found.")
            return False

    def remove_docker_network(self, network_name):
        """Remove a Docker network."""
        try:
            self.console.display_step("Removing Docker Networks", "Removing Docker network...")
            self.console.log(f"Removing network {network_name}...")
            network = self.client.networks.get(network_name)
            network.remove()
            return True
        except NotFound as e:
            self.console.log(f"Network {network_name} not found.")
            return False
