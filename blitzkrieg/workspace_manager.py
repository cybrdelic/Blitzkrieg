# main_blitzkrieg.py

from prettytable import PrettyTable
from blitzkrieg.alembic_manager import AlembicManager
from blitzkrieg.docker_manager import DockerManager
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
        self.email = email
        self.password = password
        self.workspace_name = workspace_name
        self.console = console if console else ConsoleInterface()
        self.docker_manager = DockerManager(console=self.console)
        self.postgres_port = find_available_port(5432)
        self.pgadmin_port = find_available_port(5050)
        self.pgadmin_manager = PgAdminManager(
            postgres_port=self.postgres_port,
            pgadmin_port=self.pgadmin_port,
            workspace_name=self.workspace_name,
            console=self.console,
            email=email,
            password=password
        )
        self.workspace_db_manager = WorkspaceDbManager(
            port=self.postgres_port,
            workspace_name=self.workspace_name,
            console=self.console,
            email=email,
            password=password
        )
        self.workspace_directory_manager = WorkspaceDirectoryManager(
            workspace_name=self.workspace_name,
            db_manager=self.workspace_db_manager,
            console_interface=self.console
        )
        self.docker_network_name = f"{self.workspace_name}-network"
        self.cwd = os.getcwd()
        self.alembic_manager = AlembicManager(db_manager=self.workspace_db_manager, workspace_name=self.workspace_name, console=self.console)

    def blitz_init(self):

        self.console.add_task(
            key="create_docker_network",
            func_tuple=(self.docker_manager.create_docker_network, {'network_name': self.docker_network_name}),
            progress_message="Creating Docker network",
            error_message="Failed to create Docker network"
        )
        self.console.add_task(
            key="initialize",
            func_tuple=(self.workspace_db_manager.initialize, {}),
            progress_message="Initializing PostgreSQL container",
            error_message="Failed to initialize PostgreSQL container"
        )
        self.console.add_task(
            key="setup_pgadmin",
            func_tuple=(self.pgadmin_manager.setup_pgadmin, {}),
            progress_message="Initializing PgAdmin container",
            error_message="Failed to initialize PgAdmin container"
        )
        self.console.add_task(
            key="upload_server_configuration",
            func_tuple=(self.pgadmin_manager.upload_server_configuration, {}),
            progress_message="Uploading PostgreSQL server configuration to PgAdmin",
            error_message="Failed to upload PostgreSQL server configuration to PgAdmin"
        )
        self.console.add_task_group(
            title="PgAdmin and Postgres Initialization and Configuration",
            task_keys=[
                "create_docker_network",
                "initialize",
                "setup_pgadmin",
                "upload_server_configuration"
            ]
        )
        self.console.add_task(
            key="create_workspace_directory",
            func_tuple=(self.workspace_directory_manager.create_workspace_directory, {}),
            progress_message="Creating workspace directory",
            error_message="Failed to create workspace directory"
        )
        self.console.add_task(
            key="store_credentials",
            func_tuple=(self.store_credentials, {}),
            progress_message="Storing credentials in .env file",
            error_message="Failed to store credentials"
        )
        self.console.add_task(
            key="create_projects_directory",
            func_tuple=(self.workspace_directory_manager.create_projects_directory, {}),
            progress_message="Creating /projects directory",
            error_message="Failed to create /projects directory"

        )
        self.console.add_task_group(
            title="Workspace Directory Initialization",
            task_keys=[
                "create_workspace_directory",
                "store_credentials",
                "create_projects_directory"
            ]
        )
        self.console.add_task(
            key="create_sqlalchemy_models_directory",
            func_tuple=(self.alembic_manager.create_sqlalchemy_models_directory, {}),
            progress_message="Creating /sqlalchemy_models directory",
            error_message="Failed to create /sqlalchemy_models directory",

        )
        self.console.add_task(
            key="copy_sqlalchemy_models",
            func_tuple=(self.alembic_manager.copy_sqlalchemy_models, {}),
            progress_message="Copying SQLAlchemy models",
            error_message="Failed to copy SQLAlchemy models"
        )

        self.console.add_task_group(
            title="SQLAlchemy Model Generation",
            task_keys=[
                "create_sqlalchemy_models_directory",
                "copy_sqlalchemy_models"
            ]
        )
        self.console.add_task(
            key="install_alembic",
            func_tuple=(self.alembic_manager.install_alembic, {}),
            progress_message="Installing Alembic",
            error_message="Failed to install Alembic"
        )
        self.console.add_task(
            key="initialize_alembic",
            func_tuple=(self.alembic_manager.initialize_alembic, {}),
            progress_message="Initializing Alembic with alembic init",
            error_message="Failed to initialize Alembic"
        )
        self.console.add_task_group(
            title="Alembic Initialization",
            task_keys=[
                "install_alembic",
                "initialize_alembic"
            ]
        )
        self.console.add_task(
            key="create_init_files",
            func_tuple=(self.alembic_manager.create_init_files, {}),
            progress_message="Creating __init__.py files",
            error_message="Failed to create __init__.py files"
        )

        self.console.add_task(
            key="update_sqlalchemy_uri",
            func_tuple=(self.alembic_manager.update_sqlalchemy_uri, {}),
            progress_message="Updating SQLAlchemy URI in alembic.ini",
            error_message="Failed to update SQLAlchemy URI in alembic.ini"
        )
        self.console.add_task(
            key="update_alembic_env",
            func_tuple=(self.alembic_manager.update_alembic_env, {}),
            progress_message="Updating Alembic environment.py",
            error_message="Failed to update Alembic environment.py"
        )

        self.console.run_tasks()

    def teardown_workspace(self):
        self.console.add_task(
            key="teardown",
            func_tuple=(self.workspace_db_manager.teardown, {}),
            progress_message="Tearing down PostgreSQL container",
            error_message="Failed to tear down PostgreSQL container"
        )
        self.console.add_task(
            key="teardown_pgadmin",
            func_tuple=(self.docker_manager.remove_container, {"container_name": self.pgadmin_manager.container_name}),
            progress_message="Tearing down PgAdmin container",
            error_message="Failed to tear down PgAdmin container"
        )
        self.console.add_task(
            key="remove_all_volumes",
            func_tuple=(self.docker_manager.remove_all_volumes, {}),
            progress_message="Removing all Docker volumes",
            error_message="Failed to remove all Docker volumes"
        )
        self.console.add_task(
            key="remove_docker_network",
            func_tuple=(self.docker_manager.remove_docker_network, {'network_name': self.docker_network_name}),
            progress_message="Removing Docker network",
            error_message="Failed to remove Docker network"
        )
        self.console.add_task(
            key="remove_workspace_directory",
            func_tuple=(self.workspace_directory_manager.teardown, {}),
            progress_message="Removing workspace directory",
            error_message="Failed to remove workspace directory"
        )
        self.console.add_task_group(
            title="Workspace Teardown",
            task_keys=[
                "teardown",
                "teardown_pgadmin",
                "remove_all_volumes",
                "remove_docker_network",
                "remove_workspace_directory"
            ]
        )
        self.console.run_tasks()

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
