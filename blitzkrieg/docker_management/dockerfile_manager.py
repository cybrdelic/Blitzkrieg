import os
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class DockerfileService:
    def __init__(self, name: str, build_context: str, dockerfile: str, environment_variables: dict, volumes: list, command: list, networks: list):
        self.name = name
        self.build_context = build_context
        self.dockerfile = dockerfile
        self.environment_variables = environment_variables
        self.volumes = volumes
        self.command = command
        self.networks = networks
        
class DockerfileManager:
    def __init__(self, workspace_name: str, console: ConsoleInterface):
        self.workspace_name = workspace_name
        self.console = console
        self.dockerfile_path = os.path.join(os.getcwd(), self.workspace_name, 'Dockerfile')
        self.dockerignore_path = os.path.join(os.getcwd(), self.workspace_name, '.dockerignore')
        self.parent_image = "python:3.11-slim"
        self.build_commands = [
            "pip install --upgrade pip",
            "pip install alembic",
            "pip install psycopg2-binary",
            "alembic --version"
        ]
        self.start_commands = [
            "/bin/sh",
            "-c",
            '''alembic revision --autogenerate -m "Initial migration"''',
            "echo 'Starting Alembic upgrade...' && alembic upgrade head && echo 'Alembic upgrade completed' && tail -f /dev/null"
        ]
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)

    def get_parent_image_line(self):
        return f"FROM {self.parent_image}"

    def get_build_command_lines(self):
        command_lines = [
            f"RUN {command}" for command in self.build_commands
        ]
        return '\n'.join(command_lines) if command_lines else ''

    def get_start_command_lines(self):
        command_lines = []
        for command in self.start_commands:
            split_command = command.split(' ')
            formatted_command = ' '.join([f'"{word}"' for word in split_command])
            command_lines.append(f'CMD [{formatted_command}]')
        return '\n'.join(command_lines) if command_lines else ''

    def get_set_working_directory_line(self):
        return f"WORKDIR app"

    def get_copy_files_line(self):
        return f"COPY . ."

    def get_expose_ports_line(self):
        return f"EXPOSE {self.port}"

    def write_dockerfile(self):
        with open(self.dockerfile_path, 'w') as f:
            f.write(f"{self.get_parent_image_line()}\n")
            f.write(f"{self.get_set_working_directory_line()}\n")
            f.write(f"{self.get_copy_files_line()}\n")
            f.write(f"{self.get_build_command_lines()}\n")
            f.write(f"{self.get_start_command_lines()}\n")
