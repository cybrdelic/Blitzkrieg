import json
import shutil
from typing import Generator, Optional

from rundbfast.config import load_configurations
from rundbfast.core.cli.ui import print_success, print_warning
from rundbfast.core.shared.command_runner import CommandRunner

# Load configurations
config = load_configurations()

class DockerManager:
    def __init__(self):
        self.runner = CommandRunner()

    def is_installed(self) -> bool:
        return bool(shutil.which('docker'))

    def install(self):
        self.update_system()
        self.install_docker()
        self.start_docker()
        self.enable_docker()

    def update_system(self):
        self.runner.run_command("sudo apt update")

    def install_docker(self):
        self.runner.run_command("sudo apt install -y docker.io")

    def start_docker(self):
        self.runner.run_command("sudo systemctl start docker")

    def enable_docker(self):
        self.runner.run_command("sudo systemctl enable docker")

    def pull_image(self, image: str) -> Generator[int, None, None]:
        for percentage in self.parse_docker_pull_output(image):
            yield percentage

    def parse_docker_pull_output(self, image: str) -> Generator[int, None, None]:
        for line in self.runner.run_command_realtime(f"docker pull {image}"):
            if "Pulling from" in line:
                continue
            try:
                parsed_data = json.loads(line)
                yield self.get_pull_progress(parsed_data)
            except json.JSONDecodeError:
                pass

    def get_pull_progress(self, parsed_data: dict) -> int:
        if 'progressDetail' in parsed_data and 'total' in parsed_data['progressDetail']:
            current = parsed_data['progressDetail'].get('current', 0)
            total = parsed_data['progressDetail']['total']
            return (current / total) * 100
        return 0

    def container_exists(self, container_name: str) -> bool:
        existing_containers = self.runner.run_command(f"docker ps -a -q -f name={container_name}")
        return bool(existing_containers)

    def remove_container(self, container_name: str):
        self.stop_container(container_name)
        self.delete_container(container_name)

    def stop_container(self, container_name: str):
        self.runner.run_command(f"docker stop {container_name}")

    def delete_container(self, container_name: str):
        self.runner.run_command(f"docker rm {container_name}")

    def is_container_running(self, container_name: str) -> bool:
        output = self.runner.run_command(f"docker inspect -f '{{{{.State.Running}}}}' {container_name}")
        return output == 'true'

    def image_exists(self, image_name: str) -> bool:
        images = self.runner.run_command(f"docker images -q {image_name}")
        return bool(images)

    def create_volume(self, volume_name: str):
        self.runner.run_command(f"docker volume create {volume_name}")

    def volume_exists(self, volume_name: str) -> bool:
        existing_volumes = self.runner.run_command(f"docker volume ls -q -f name={volume_name}")
        return bool(existing_volumes)

    def remove_volume(self, volume_name: str):
        self.runner.run_command(f"docker volume rm {volume_name}")
