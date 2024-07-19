import os
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class DockerComposeServiceBuild:
    def __init__(self, context: str, dockerfile: str):
        self.context = context
        self.dockerfile = dockerfile

class DockerComposeService:
    def __init__(self, name: str, build: DockerComposeServiceBuild, environment: dict, volumes: list, command: list, networks: list):
        self.name = name
        self.build = build
        self.container_name = name
        self.environment = environment if environment else {
            "ALEMBIC_CONFIG": "/app/alembic.ini",
        }
        self.volumes = volumes
        self.command = command
        self.networks = networks

    def write_lines(self):
        def __tab__(number_of_indents: int, line: str):
            return f"{' ' * 2 * number_of_indents}{line}"

        service_lines = []
        service_lines.append(__tab__(1, f"{self.name}:"))
        for key, value in self.__dict__.items():
            if key == 'build':
                service_lines.append(__tab__(2, f"{key}:"))
                for build_key, build_value in value.__dict__.items():
                    service_lines.append(__tab__(3, f"{build_key}: {build_value}"))
            elif key == 'environment':
                service_lines.append(__tab__(2, f"{key}:"))
                for env_key, env_value in value.items():
                    service_lines.append(__tab__(3, f"- {env_key}={env_value}"))
            elif key == 'volumes':
                service_lines.append(__tab__(2, f"{key}:"))
                for volume in value:
                    service_lines.append(__tab__(3, f"- {volume}"))
            elif key == 'command':
                service_lines.append(__tab__(2, f"{key}: ["))
                for command in value:
                    service_lines.append(__tab__(3, f'"{command}",'))
                service_lines[-1] = service_lines[-1][:-1]




class DockerComposeManager:
    def __init__(self, console: ConsoleInterface, workspace_name: str):
        self.console = console
        self.workspace_name = workspace_name
        self.workspace_path = os.path.join(os.getcwd(), workspace_name)
        self.version = '3.8'
        self.alembic_worker_service_name = 'alembic-worker'
        self.alembic_build_context = "."
        self.alembic_dockerfile = "Dockerfile"
        self.alembic_worker_container_name = f"{self.workspace_name}-{self.alembic_worker_service_name}"
        self.alembic_worker_environment_variables = {
            "ALEMBIC_CONFIG": '/app/alembic.ini'
        }
        self.network_name = f"{self.workspace_name}-network"
        self.volumes = {'app-volume': None}
        self.volume_mounts = ['app-volume:/app']
        self.start_commands = ["/bin/sh", "-c",'''alembic revision --autogenerate -m "Initial migration"
''',  "echo 'Starting Alembic upgrade...' && alembic upgrade head && echo 'Alembic upgrade completed' && tail -f /dev/null"]

    def get_services(self):
        return {
            self.alembic_worker_service_name: {
                "build": {
                    "context": self.alembic_build_context,
                    "dockerfile": self.alembic_dockerfile
                },
                "container_name": self.alembic_worker_container_name,
                "environment": self.alembic_worker_environment_variables,
                "volumes": self.volume_mounts,
                "command": self.start_commands,
                "networks": [self.network_name]
            }
        }

    def get_services_lines(self):
        def __tab__(number_of_indents: int, line: str):
            return f"{' ' * 2 * number_of_indents}{line}"

        services = self.get_services()
        service_lines = []
        service_lines.append("services:")
        for service_name, service_config in services.items():
            service_lines.append(__tab__(1, f"{service_name}:"))
            for key, value in service_config.items():
                if key == 'build':
                    service_lines.append(__tab__(2, f"{key}:"))
                    for build_key, build_value in value.items():
                        service_lines.append(__tab__(3, f"{build_key}: {build_value}"))
                elif key == 'environment':
                    service_lines.append(__tab__(2, f"{key}:"))
                    for env_key, env_value in value.items():
                        service_lines.append(__tab__(3, f"- {env_key}={env_value}"))
                elif key == 'volumes':
                    service_lines.append(__tab__(2, f"{key}:"))
                    for volume in value:
                        service_lines.append(__tab__(3, f"- {volume}"))
                elif key == 'command':
                    service_lines.append(__tab__(2, f"{key}: ["))
                    for command in value:
                        service_lines.append(__tab__(3, f'"{command}",'))
                    service_lines[-1] = service_lines[-1][:-1]  # Remove the last comma
                    service_lines.append(__tab__(2, f"]"))
                elif key == 'networks':
                    service_lines.append(__tab__(2, f"{key}:"))
                    for network in value:
                        service_lines.append(__tab__(3, f"- {network}"))
                else:
                    service_lines.append(__tab__(2, f"{key}: {value}"))
        return service_lines

    def get_version_line(self):
        return f"version: '{self.version}'"

    def get_networks_line(self):
        return f"networks:\n  {self.network_name}:\n    external: true"

    def get_volumes_line(self):
        volumes_lines = [
            f"volumes:\n  {volume}:" for volume in self.volumes.keys()
        ]
        return "\n".join(volumes_lines)

    def get_docker_compose_data(self):
        data = [
            self.get_networks_line(),
            self.get_volumes_line()
        ]
        data += self.get_services_lines()
        return "\n".join(data)

    def write_docker_compose_file(self):
        docker_compose_path = os.path.join(self.workspace_path, 'docker-compose.yml')
        self.console.handle_wait(f"Creating docker-compose.yml file at {docker_compose_path}...")
        with open(docker_compose_path, 'w') as f:
            self.console.handle_wait("Writing docker-compose.yml file...")
            f.write(self.get_docker_compose_data())
        return self.console.handle_success(f"docker-compose.yml file created successfully at {docker_compose_path}")
