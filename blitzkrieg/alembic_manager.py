# alembic_manager.py

import os
import subprocess
import shutil
from blitzkrieg.db.models.Base import Base
from blitzkrieg.db.models.issue import Issue
from blitzkrieg.db.models.project import Project
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
import sys
from blitzkrieg.ui_management.decorators import with_spinner

class AlembicManager:
    def __init__(self, db_manager, workspace_name: str, console: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager
        self.alembic_env_path = os.path.join(self.workspace_path, 'migrations/env.py')
        self.alembic_ini_path = os.path.join(self.workspace_path, 'alembic.ini')
        self.migrations_path = os.path.join(self.workspace_path, 'migrations')
        self.sqlalchemy_models_path = os.path.join(self.workspace_path, 'sqlalchemy_models')
        self.initial_schema_names = ['project_management', 'event_management', 'workspace_management']
        self.initial_table_models = [Base, Project, Issue]
        self.models_directory = os.path.join(os.getcwd(), 'blitzkrieg', 'db', 'models')
        self.console = console if console else ConsoleInterface()
        self.initial_schema_names = [
            'project_management',
            'event_management',
            'workspace_management'
        ]
        self.initial_table_models = [
            Base,
            Project,
            Issue
        ]
        self.base_sql_alchemy_model = Base
        self.models_directory = os.path.join(os.getcwd(), 'blitzkrieg','db', 'models')
        self.init_paths = [
            self.workspace_path,
            os.path.join(self.workspace_path, 'sqlalchemy_models'),
            os.path.join(self.workspace_path, 'migrations'),
            os.path.join(self.workspace_path, 'migrations', 'versions')
        ]

    def create_init_files(self):
        """ Ensures that __init__.py files are present in all necessary directories. """
        for path in self.init_paths:
            init_file = os.path.join(path, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
        return "Created __init__.py files in all necessary directories."


    def create_sqlalchemy_models_directory(self):
        if not os.path.exists(self.sqlalchemy_models_path):
            os.makedirs(self.sqlalchemy_models_path, exist_ok=True)
            self.console.log(f"Created sqlalchemy_models directory at {self.sqlalchemy_models_path}")
            sys.path.append(self.workspace_path)

    def copy_sqlalchemy_models(self):
        try:
            if self.models_directory and os.path.exists(self.models_directory):
                for filename in os.listdir(self.models_directory):
                    full_file_path = os.path.join(self.models_directory, filename)
                    if os.path.isfile(full_file_path) and filename.endswith('.py'):
                        shutil.copy(full_file_path, self.sqlalchemy_models_path)
                return f"Copied SQLAlchemy models from [white]'{self.models_directory}'[/white] to [white]'{self.sqlalchemy_models_path}'[/white]"
        except Exception as e:
            return f"Failed to copy SQLAlchemy models: [bold red]{str(e)}[/bold red]"

    def execute_command(self, command, directory, message=None):
        """Execute a shell command in a given directory and handle errors."""
        # Constructing the command based on whether it's a pip operation
        if command[0] == 'pip':
            # Use sys.executable to ensure the correct pip is called
            full_command = [sys.executable, '-m'] + command
        else:
            full_command = command

        try:
            result = subprocess.run(
                full_command, cwd=directory, shell=False, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.stdout:
                self.console.log(f"Output: {result.stdout}")
            if result.stderr:
                self.console.log(f"Error: {result.stderr}", level='error')
            return self.console.handle_success(f"Command '{' '.join(command)}' executed successfully.")
        except subprocess.CalledProcessError as e:
            error_detail = f"{e.stderr}" if e.stderr else "No error details available."
            return self.console.handle_error(f"Command failed with error: {error_detail}")
        except Exception as e:
            return self.console.handle_error(f"Unexpected error: {str(e)}")

    def create_sqlalchemy_models_directory(self):
        """ Ensure the sqlalchemy_models directory is created and models are initialized. """
        try:
            if not os.path.exists(self.sqlalchemy_models_path):
                os.makedirs(self.sqlalchemy_models_path, exist_ok=True)
                sys.path.append(self.workspace_path)
                return f"Created sqlalchemy_models directory at {self.sqlalchemy_models_path}"
        except Exception as e:
            return f"Failed to create sqlalchemy_models directory: {str(e)}"
            # Optionally, also ensure that model files are present or generate them


    def install_alembic(self):
        return self.execute_command(['pip', 'install', 'alembic'], self.workspace_path)

    def initialize_alembic(self):
        return self.execute_command(['alembic', 'init', 'migrations'], self.workspace_path)

    def update_sqlalchemy_uri(self):
        try:
            with open(self.alembic_ini_path, 'r') as f:
                lines = f.readlines()
            with open(self.alembic_ini_path, 'w') as f:
                for line in lines:
                    if line.startswith('sqlalchemy.url'):
                        f.write(f'sqlalchemy.url = {self.db_manager.get_sqlalchemy_uri()}\n')
                    else:
                        f.write(line)
            self.console.log(f"SQLAlchemy URI updated successfully in the Alembic configuration. Changed 'sqlalchemy.url' from 'sqlite:///alembic.sqlite' to '{self.db_manager.get_sqlalchemy_uri()}'.")
            return True
        except Exception as e:
            self.console.log(f"Failed to update SQLAlchemy URI: {str(e)}")
            return False

    def update_alembic_env(self):
        env_content = self.get_new_env_py_content()
        self.write_env_py_content_to_file(env_content)

    def get_new_env_py_content(self):
        return f"""
from sqlalchemy import create_engine
from alembic import context
import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(__file__)))

project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("{str(self.workspace_path)}")

from {self.workspace_name}.sqlalchemy_models.Base import Base

url = '{self.db_manager.get_sqlalchemy_uri()}'
config = context.config
config.set_main_option('sqlalchemy.url', url)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

    def write_env_py_content_to_file(self, content):
        with open(self.alembic_env_path, 'w') as env_file:
            env_file.write(content)
        self.console.log("Alembic env.py file updated successfully with target metadata and sys.path.append() for SQLAlchemy models.")

    def auto_generate_initial_alembic_migration_script(self):
        return self.execute_command(['alembic', 'revision', '--autogenerate', '-m', 'Initial'], self.workspace_path)

    def run_migrations(self):
        return self.execute_command(['alembic', 'upgrade', 'head'], self.workspace_path)

    @with_spinner(
        message="Setting up Alembic for schemas...",
        failure_message="Failed to set up Alembic for schemas.",
        success_message="Alembic schemas set up successfully."
    )
    def setup_alembic_for_schemas(self):
        for schema in self.initial_schema_names:
            migration_label = f"create_{schema}_schema"
            self.generate_blank_migration(migration_label)
            self.modify_migration_for_schema(schema, migration_label)
        self.run_migrations()

    def generate_blank_migration(self, label):
        command = ['alembic', 'revision', '--autogenerate', '-m', label]
        self.execute_command(command, self.workspace_path, f"Generating blank migration for {label}.")

    def modify_migration_for_schema(self, schema_name, migration_label):
        migration_file = self.find_migration_file(migration_label)
        if migration_file:
            self.insert_schema_creation_sql(migration_file, schema_name)

    def find_migration_file(self, label):
        versions_path = os.path.join(self.migrations_path, 'versions')
        for filename in os.listdir(versions_path):
            if label in filename:
                return os.path.join(versions_path, filename)
        return None

    def insert_schema_creation_sql(self, migration_file, schema_name):
        with open(migration_file, 'r+') as file:
            content = file.read()
            position = content.find('def upgrade():')
            if position != -1:
                upgrade_section = f"\n    op.execute('CREATE SCHEMA IF NOT EXISTS {schema_name}')\n"
                content = content[:position + len('def upgrade():')] + upgrade_section + content[position + len('def upgrade():'):]
                file.seek(0)
                file.write(content)
                file.truncate()
            self.console.log(f"Added schema creation SQL for {schema_name} in {migration_file}.")
