# alembic_manager.py

import os
import subprocess
import shutil
from blitzkrieg.alembic_management.alembic_command_runner import AlembicCommandRunner
from blitzkrieg.db.models.Base import Base
from blitzkrieg.db.models.issue import Issue
from blitzkrieg.db.models.project import Project
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
import sys

class AlembicManager:
    def __init__(self, db_manager, workspace_name: str, console: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager
        self.alembic_env_path = os.path.join(self.workspace_path, 'alembic/env.py')
        self.alembic_ini_path = os.path.join(self.workspace_path, 'alembic.ini')
        self.migrations_path = os.path.join(self.workspace_path, 'alembic')
        self.sqlalchemy_models_path = os.path.join(self.workspace_path, 'sqlalchemy_models')
        self.initial_schema_names = ['project_management', 'event_management', 'workspace_management']
        self.initial_table_models = [Base, Project, Issue]
        self.models_directory = os.path.join(os.getcwd(), 'blitzkrieg', 'db', 'models')
        self.console = console if console else ConsoleInterface()
        self.init_paths = [
            self.workspace_path,
            os.path.join(self.workspace_path, 'sqlalchemy_models'),
            os.path.join(self.workspace_path, 'alembic'),
            os.path.join(self.workspace_path, 'alembic', 'versions')
        ]
        self.command_runner = AlembicCommandRunner(self.console, self.workspace_name)

    def create_init_files(self):
        """ Ensures that __init__.py files are present in all necessary directories. """
        try:
            for path in self.init_paths:
                init_file = os.path.join(path, '__init__.py')
                if not os.path.exists(init_file):
                    open(init_file, 'a').close()
                    self.console.handle_info(f"Created __init__.py file at {path}")
            return self.console.handle_success("All __init__.py files created successfully.")
        except Exception as e:
            return self.console.handle_error(f"Failed to create init files: {str(e)}")

    def create_sqlalchemy_models_directory(self):
        """ Ensure the sqlalchemy_models directory is created and models are initialized. """
        try:
            if not os.path.exists(self.sqlalchemy_models_path):
                os.makedirs(self.sqlalchemy_models_path, exist_ok=True)
                sys.path.append(self.workspace_path)
                return self.console.handle_success(f"Created sqlalchemy_models directory at [white]{self.sqlalchemy_models_path}[/white]")
        except Exception as e:
            return self.console.handle_error(f"Failed to create sqlalchemy_models directory: {str(e)}")

    def copy_sqlalchemy_models(self):
        try:
            if self.models_directory and os.path.exists(self.models_directory):
                for filename in os.listdir(self.models_directory):
                    full_file_path = os.path.join(self.models_directory, filename)
                    if os.path.isfile(full_file_path) and filename.endswith('.py'):
                        shutil.copy(full_file_path, self.sqlalchemy_models_path)
                return self.console.handle_success(f"Copied SQLAlchemy models from [white]{self.models_directory}[/white] to [white]{self.sqlalchemy_models_path}[/white].")
        except Exception as e:
            return self.console.handle_error(f"Failed to copy SQLAlchemy models: {str(e)}")

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
            return self.console.handle_success(f"SQLAlchemy URI updated successfully in the Alembic configuration. Changed 'sqlalchemy.url' from 'sqlite:///alembic.sqlite' to '{self.db_manager.get_sqlalchemy_uri()}'.")
        except Exception as e:
            return self.console.handle_error(f"Failed to update SQLAlchemy URI: {str(e)}")

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
        self.console.handle_info("Alembic env.py file updated successfully with target metadata and sys.path.append() for SQLAlchemy models.")

    def setup_alembic_for_schemas(self):
        self.command_runner.run_migrations()
        for schema in self.initial_schema_names:
            migration_label = f"create_{schema}_schema"
            self.command_runner.generate_blank_migration(migration_label)
            self.modify_migration_for_schema(schema, migration_label)
            self.command_runner.run_migrations()

    def install_alembic(self):
        self.command_runner.install_alembic()

    def initialize_alembic(self):
        self.command_runner.initialize_alembic()

    def modify_migration_for_schema(self, schema_name, migration_label):
        self.console.handle_wait(f"Modifying migration file for schema creation: {schema_name}. Migration label: {migration_label}...")
        self.console.handle_info(f"Modifiying migration file for schema creation: {schema_name}. Migration label: {migration_label}...")
        migration_file = self.find_migration_file(migration_label)
        if migration_file:
            self.insert_schema_creation_sql(migration_file, schema_name)

    def find_migration_file(self, label):
        versions_path = os.path.join(self.migrations_path, 'versions')
        for filename in os.listdir(versions_path):
            if label in filename:
                migration_file_path = os.path.join(versions_path, filename)
                self.console.handle_info(f"Found migration file: {migration_file_path}")
                return migration_file_path
        return None

    def insert_schema_creation_sql(self, migration_file, schema_name):
        try:
            with open(migration_file, 'r+') as file:
                content = file.read()
                import re
                pattern = r'def upgrade\(\) *-> *None:'
                match = re.search(pattern, content)
                if match:
                    position = match.start()
                    upgrade_section = f"\n    op.execute('CREATE SCHEMA IF NOT EXISTS {schema_name}')\n"
                    content = content[:position + len(match.group())] + upgrade_section + content[position + len(match.group()):]
                    file.seek(0)
                    file.write(content)
                    file.truncate()
                    self.console.handle_success(f"Successfully inserted schema creation SQL into migration file: {migration_file}")
                else:
                    self.console.handle_error(f"Failed to find 'def upgrade() -> None:' in migration file: {migration_file}. Position: {match}")
        except FileNotFoundError:
            self.console.handle_error(f"Migration file not found: {migration_file}")
        except IOError as e:
            self.console.handle_error(f"IOError while handling migration file: {migration_file}, Error: {e}")
        except Exception as e:
            self.console.handle_error(f"An unexpected error occurred: {e}")
