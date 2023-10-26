from cli.ui import print_header, print_message, print_success
from core.managers.docker_manager import DockerManager
from config import load_configurations
from cli.ui import show_progress

config = load_configurations()

class DockerInitializer:
    @staticmethod
    def initialize():
        print_header("Docker Initialization")
        docker = DockerManager()

        if not docker.is_installed():
            with show_progress("Installing Docker...") as progress:
                docker.install()
                progress.update(100)
            print_success("Docker installed successfully!")
        else:
            print_message("Docker is already installed.")

        return docker
