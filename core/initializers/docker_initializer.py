from rundbfast.core.cli.ui import print_header, print_message, print_success, show_progress
from rundbfast.core.managers.manager import DockerManager


def initialize_docker():
    print_header("Docker Initialization")
    docker = DockerManager()

    if not docker.is_installed():
        with show_progress("Installing Docker...") as progress:
            docker.install()
            progress.completed = 100
            print_success("Docker installed successfully!")
    else:
        print_message("Docker is already installed.")

    return docker
