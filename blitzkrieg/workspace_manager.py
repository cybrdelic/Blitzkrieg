# main_blitzkrieg.py

from prettytable import PrettyTable
from blitzkrieg.alembic_manager import AlembicManager
from blitzkrieg.docker_manager import DockerManager
from blitzkrieg.file_manager import FileManager
from blitzkrieg.file_writers.workspace_docker_compose_writer import WorkspaceDockerComposeWriter
from blitzkrieg.file_writers.workspace_dockerfile_writer import WorkspaceDockerfileWriter
from blitzkrieg.workspace_directory_manager import WorkspaceDirectoryManager
from blitzkrieg.pgadmin_manager import PgAdminManager
from blitzkrieg.postgres_manager import WorkspaceDbManager
from blitzkrieg.ui_management.decorators import with_spinner
from blitzkrieg.utils.port_allocation import find_available_port
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
import os
from prettytable import PrettyTable

class WorkspaceManager:
    def __init__(self, workspace_name, console: ConsoleInterface = None, email=None, password=None):
        self.email: str = email
        self.password: str = password
        self.workspace_name: str = workspace_name
        self.console: ConsoleInterface = console if console else ConsoleInterface()
        self.docker_manager: DockerManager = DockerManager(console=self.console)
        self.postgres_port: int = find_available_port(5432)
        self.pgadmin_port: int = find_available_port(5050)
        self.pgadmin_manager:PgAdminManager = PgAdminManager(
            postgres_port=self.postgres_port,
            pgadmin_port=self.pgadmin_port,
            workspace_name=self.workspace_name,
            console=self.console,
            email=email,
            password=password
        )
        self.file_manager: FileManager = FileManager()
        self.workspace_db_manager: WorkspaceDbManager = WorkspaceDbManager(
            port=self.postgres_port,
            workspace_name=self.workspace_name,
            console=self.console,
            email=email,
            password=password
        )
        self.workspace_directory_manager: WorkspaceDirectoryManager = WorkspaceDirectoryManager(
            workspace_name=self.workspace_name,
            db_manager=self.workspace_db_manager,
            console_interface=self.console,
            docker_manager=self.docker_manager
        )
        self.workspace_db_manager.set_workspace_directory_manager(self.workspace_directory_manager)
        self.docker_network_name: str = f"{self.workspace_name}-network"
        self.cwd = os.getcwd()
        self.alembic_manager: AlembicManager = AlembicManager(
            db_manager=self.workspace_db_manager,
            workspace_name=self.workspace_name,
            file_manager=self.file_manager,
            console=self.console
        )
        self.workspace_db_manager.set_alembic_manager(self.alembic_manager)
        self.workspace_db_manager.set_pgadmin_manager(self.pgadmin_manager)
        self.workspace_dockerfile_writer = WorkspaceDockerfileWriter(workspace_path=self.workspace_directory_manager.workspace_path, console=self.console)
        self.workspace_docker_compose_writer = WorkspaceDockerComposeWriter(workspace_name=self.workspace_name, workspace_path=self.workspace_directory_manager.workspace_path, console=self.console, pgadmin_manager=self.pgadmin_manager, postgres_manager=self.workspace_db_manager)
        self.file_manager = FileManager()

    def blitz_init(self):
        blitzkrieg_initialization_process = self.console.create_workflow("Blitzkrieg Initialization")

        workspace_directory_initalization_group = self.console.create_phase(blitzkrieg_initialization_process, "Workspace Directory Initialization")
        workspace_docker_files_composition_group = self.console.create_phase(blitzkrieg_initialization_process, "Workspace Docker Files Composition")
        workspace_container_initialization = self.console.create_phase(blitzkrieg_initialization_process, "Workspace Container Initialization")

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Creating workspace docker network",
            func=self.docker_manager.create_docker_network,
            network_name=self.docker_network_name
        )
        # Workspace Directory Initialization
        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Creating workspace directory...",
            func=self.workspace_directory_manager.create_workspace_directory
        )

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Storing workspace configuration in .env file...",
            func=self.store_credentials
        )
        self.console.add_action(
            phase=workspace_directory_initalization_group,
            func=self.alembic_manager.create_sqlalchemy_models_directory,
            name="Creating /sqlalchemy_models directory"
        )

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            func=self.alembic_manager.copy_sqlalchemy_models,
            name="Copying SQLAlchemy Models"
        )

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            func=self.alembic_manager.copy_requirements_txt,
            name="Copying requirements.txt file"
        )

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            func=self.alembic_manager.copy_alembic_init_script,
            name="Copying Alembic Init Script"
        )

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Creating alembic.ini file to replace later...",
            func=self.alembic_manager.create_alembic_ini_file
        )

        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Creating alembic env file to copy into workspace directory...",
            func=self.alembic_manager.update_alembic_env
        )
        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Creating __init__.py files in workspace directory",
            func=self.alembic_manager.create_init_files
        )
        self.console.add_action(
            phase=workspace_directory_initalization_group,
            name="Creating servers.json file for pgadmin",
            func=self.pgadmin_manager.create_server_config)

        self.console.add_action(
            phase=workspace_docker_files_composition_group,
            name="Creating Dockerfile for workspace...",
            func=self.workspace_dockerfile_writer.write_dockerfile
        )


        self.console.add_action(
            phase=workspace_docker_files_composition_group,
            name="Creating docker-compose.yml for workspace...",
            func=self.workspace_docker_compose_writer.write_docker_compose_file
        )

        self.console.add_action(
            phase=workspace_container_initialization,
            name="Building workspace container...",
            func=self.workspace_directory_manager.build_workspace_container
        )

        self.console.add_action(
            phase=workspace_container_initialization,
            name="Starting workspace container...",
            func=self.workspace_directory_manager.start_workspace_container
        )

        self.console.add_action(
            phase=workspace_container_initialization,
            name="Saving workspace details to workspace database",
            func=self.save_workspace_details
        )

        self.console.run_workflow(blitzkrieg_initialization_process)

    def teardown_workspace(self):
        teardown_workspace_process = self.console.create_workflow("Teardown Workspace")
        workspace_teardown_group = self.console.create_phase(teardown_workspace_process, "Workspace Teardown")
        # self.console.add_action(
        #     phase=workspace_teardown_group,
        #     name="Removing workspace details from database",
        #     func=self.workspace_db_manager.remove_workspace_details
        # )
        self.console.add_action(
            phase=workspace_teardown_group,
            name="Removing Workspace Postgres Database...",
            func=self.workspace_db_manager.teardown
        )
        self.console.add_action(
            phase=workspace_teardown_group,
            name="Removing Workspace PgAdmin Container...",
            func=self.docker_manager.remove_container,
            container_name=self.pgadmin_manager.container_name
        )

        self.console.add_action(
            phase=workspace_teardown_group,
            name="Removing Workspace Alembic Worker Container...",
            func=self.docker_manager.remove_container,
            container_name=f"{self.workspace_name}-alembic-worker"
        )

        self.console.add_action(
            phase=workspace_teardown_group,
            name="Removing All Docker Volumes...",
            func=self.docker_manager.remove_all_volumes
        )

        self.console.add_action(
            phase=workspace_teardown_group,
            name="Removing Workspace Docker Network...",
            func=self.docker_manager.remove_docker_network,
            network_name=self.docker_network_name
        )

        self.console.add_action(
            phase=workspace_teardown_group,
            name="Removing Workspace Directory...",
            func=self.workspace_directory_manager.teardown
        )

        self.console.run_workflow(teardown_workspace_process)

    def save_workspace_details(self):
        self.workspace_db_manager.save_workspace_details()

    def store_credentials(self):
        try:
            with open(f"{self.workspace_directory_manager.workspace_path}/.env", "w") as f:
                f.write(f"POSTGRES_USER={self.workspace_db_manager.db_user}\n")
                f.write(f"POSTGRES_PASSWORD={self.workspace_db_manager.password}\n")
                f.write(f"POSTGRES_DB={self.workspace_name}\n")
                f.write(f"POSTGRES_HOST={self.workspace_db_manager.container_name}\n")
                f.write(f"POSTGRES_PORT={self.workspace_db_manager.db_port}\n")
                f.write(f"PGADMIN_DEFAULT_EMAIL={self.email}\n")
                f.write(f"PGADMIN_DEFAULT_PASSWORD={self.password}\n")
                f.write(f"PGADMIN_PORT={self.pgadmin_port}\n")
                f.write(f"WORKSPACE_NAME={self.workspace_name}\n")
                f.write(f"WORKSPACE_DIRECTORY={self.workspace_directory_manager.workspace_path}\n")
                f.write(f"ALEMBIC_INI_PATH={self.alembic_manager.alembic_ini_path}\n")
                f.write(f"ALEMBIC_ENV_PATH={self.alembic_manager.alembic_env_path}\n")
                f.write(f"SQLALCHEMY_MODELS_PATH={self.alembic_manager.sqlalchemy_models_path}\n")
                f.write(f"SQLALCHEMY_URI={self.workspace_db_manager.get_sqlalchemy_uri()}\n")
                f.write(f"POSTGRES_SERVER_CONFIG_HOST={self.pgadmin_manager.postgres_server_config_host}\n")
                f.write(f"POSTGRES_SERVER_CONFIG_USERNAME={self.pgadmin_manager.postgres_server_config_username}\n")
                f.write(f"PGADMIN_BINDING_CONFIG_PATH={self.pgadmin_manager.pgadmin_binding_config_path}\n")
            return self.console.handle_success(f"Stored the following credentials in an env file: {self.workspace_directory_manager.workspace_path}/.env")
        except Exception as e:
            return self.console.handle_error(f"Failed to store credentials: {str(e)}")



    def add_color(self, text, color):
        colors = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "red": "\033[91m",
            "end": "\033[0m",
        }
        return f"{colors[color]}{text}{colors['end']}"

    def show_workspace_details(self):
        with open(f"{self.workspace_directory_manager.workspace_path}/.env", "r") as f:
            content = f.readlines()

        table = PrettyTable()
        table.field_names = [self.add_color("Variable", "blue"), self.add_color("Value", "green")]
        table.align = "l"  # Align the text to the left

        for line in content:
            if "=" in line:
                var, val = line.strip().split('=', 1)
                table.add_row([var, self.add_color(val, "red")])

        print(table)
