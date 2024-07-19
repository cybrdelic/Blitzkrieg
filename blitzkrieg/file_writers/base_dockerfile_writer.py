import os

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class BaseDockerfileWriter:
    def __init__(self, path: str, console: ConsoleInterface):
        self.path = path
        self.console = console

    def write_dockerfile(self, dockerfile_content: str):
        dockerfile_path = os.path.join(self.path, 'Dockerfile')
        self.console.handle_wait(f"Writing Dockerfile to {dockerfile_path}")
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        self.console.handle_success(f"Dockerfile written to {dockerfile_path}")
        self.console.display_file_content(dockerfile_path)
