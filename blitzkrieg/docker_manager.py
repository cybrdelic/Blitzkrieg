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
                    container_attrs = container.attrs
                    success_message = f"Container [white]{container_name}[/white] is running"
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
            return self.console.handle_success(f"Container [white]'{container_name}'[/white] removed successfully.")
        except NotFound as e:
            return self.console.handle_error(f"Container {container_name} not found.")
        except APIError as e:
            return self.console.handle_error(f"Failed to remove container [white]{container_name}[/white]: {str(e)}")
        except Exception as e:
            return self.console.handle_error(f"Failed to remove container [white]{container_name}[/white]: {str(e)}")

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
            for volume in self.client.volumes.list():
                volume.remove()
            volume_names = [v.name for v in self.client.volumes.list()]
            csv_volume_names = ', '.join(volume_names)
            return self.console.handle_success(f"The following volumes have been removed successfully: {csv_volume_names}")
        except NotFound as e:
            return self.console.handle_error(f"Volume not found.")
        except APIError as e:
            return self.console.handle_error(f"Failed to remove volume: {str(e)}")
        except Exception as e:
            return self.console.handle_error(f"Failed to remove volume: {str(e)}")

    def remove_docker_network(self, network_name):
        """Remove a Docker network."""
        try:
            network = self.client.networks.get(network_name)
            network.remove()
            return self.console.handle_success(f"Network [white]{network_name}[/white] removed successfully.")
        except NotFound as e:
            return self.console.handle_error(f"Network {network_name} not found.")
        except APIError as e:
            return self.console.handle_error(f"Failed to remove network [white]{network_name}[/white] due to APIError: {str(e)}")
        except Exception as e:
            return self.console.handle_error(f"Failed to remove network [white]{network_name}[/white]: {str(e)}")
