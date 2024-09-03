# alembic_manager.py

import os
import subprocess
import shutil
import time

from psycopg2 import OperationalError
from sqlalchemy import create_engine, text
from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.file_manager import FileManager
import sys

class AlembicManager:
    def __init__(self, db_manager, file_manager: FileManager, workspace_name: str, console: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.file_manager = file_manager
        self.sqlalchemy_models_path = os.path.join(self.workspace_path, 'sqlalchemy_models')
        self.models_directory = os.path.join(os.getcwd(), 'blitzkrieg', 'db', 'models')
        self.console = console if console else ConsoleInterface()
        self.init_paths = [
            self.workspace_path,
            os.path.join(self.workspace_path, 'sqlalchemy_models'),
        ]
        self.postgres_port = None
    def initialize_alembic(self):
        try:
            self._run_command(['alembic', 'init', 'migrations'])
            self._update_env_py()
            self._run_initial_migration()
            self._run_command(['alembic', 'upgrade', 'head'])
            self.console.handle_success("Alembic initialization completed successfully")
        except Exception as e:
            self.console.handle_error(f"An error occurred during Alembic initialization: {str(e)}")
            raise
    def _run_command(self, command):
        result = subprocess.run(command, cwd=self.workspace_path, check=True,
                                capture_output=True, text=True)
        self.console.handle_info(result.stdout)
        if result.stderr:
            self.console.handle_warning(result.stderr)

    def wait_for_db(self):
        postgres_port = blitz_env_manager.get_workspace_env_var('POSTGRES_PORT')
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                engine = create_engine(f'postgresql+psycopg2://{self.workspace_name}-db-user:pw@localhost:{postgres_port}/{self.workspace_name}')
                with engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                self.console.handle_info("Database is ready.")
                return
            except OperationalError:
                self.console.handle_info(f"Database not ready. Attempt {attempt + 1}/{max_attempts}. Retrying in 2 seconds...")
                time.sleep(2)
        raise Exception("Database connection timed out")

    def create_schema(self):
        postgres_port = blitz_env_manager.get_workspace_env_var('POSTGRES_PORT')
        with create_engine(f'postgresql+psycopg2://{self.workspace_name}-db-user:pw@localhost:{postgres_port}/{self.workspace_name}').connect() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS project_management"))
            connection.commit()
        self.console.handle_info("Created 'project_management' schema.")

    def _run_initial_migration(self):
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{self.workspace_path}:{env.get('PYTHONPATH', '')}"

            result = subprocess.run(['alembic', 'revision', '--autogenerate', '-m', "initial migration"],
                                    cwd=self.workspace_path,
                                    check=True,
                                    capture_output=True,
                                    text=True,
                                    env=env)
            self.console.handle_info(result.stdout)
            if result.stderr:
                self.console.handle_warning(result.stderr)
        except subprocess.CalledProcessError as e:
            self.console.handle_error(f"Initial migration failed: {e}")
            self.console.handle_error(f"Command output: {e.output}")
            self._debug_alembic_env()
            raise

    def _debug_alembic_env(self):
        self.console.handle_info("Debugging Alembic environment...")
        env_py_path = os.path.join(self.workspace_path, 'migrations', 'env.py')
        with open(env_py_path, 'r') as f:
            self.console.handle_info(f"Contents of env.py:\n{f.read()}")

        self.console.handle_info(f"Current working directory: {os.getcwd()}")
        self.console.handle_info(f"Workspace path: {self.workspace_path}")
        self.console.handle_info(f"Python path: {sys.path}")

    def _update_env_py(self):
        postgres_port = blitz_env_manager.get_workspace_env_var('POSTGRES_PORT')
        env_py_path = os.path.join(self.workspace_path, 'migrations', 'env.py')
        with open(env_py_path, 'w') as f:
            f.write(f"""
from sqlalchemy import create_engine, text
from alembic import context
import logging
import os
import sys
import importlib.util

sys.path.append(".")

# Load all models dynamically
def load_models():
    models_path = os.path.join('sqlalchemy_models')
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(models_path, filename))
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)

load_models()

# Import the Base class after loading the models
from sqlalchemy_models.base import Base # type: ignore

# Reflect the metadata
metadata = Base.metadata
for cls in Base.__subclasses__():
    cls.__table__.metadata = metadata

url = 'postgresql+psycopg2://{self.workspace_name}-db-user:pw@localhost:{postgres_port}/{self.workspace_name}'
config = context.config
config.set_main_option('sqlalchemy.url', url)

from sqlalchemy_models.base import Base  # type: ignore
# Replace 'myapp.models' with the actual path to your models
target_metadata = Base.metadata

def create_schemas(connection):
    connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS project_management'))
    connection.commit()  # Ensure the schema creation is committed
    print('Created schema: project_management')

def run_migrations_offline():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(url)
    with connectable.connect() as connection:
        try:
            create_schemas(connection)  # Create necessary schemas before running migrations
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
        except Exception as e:
            logging.error("Error during migration: %s", str(e))
            raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")
        self.console.handle_info(f"Updated {env_py_path}")


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
                        self.file_manager.replace_text_in_file(
                            os.path.join(self.sqlalchemy_models_path, filename),
                            'blitzkrieg.db.models',
                            f"sqlalchemy_models"
                        )
                        self.file_manager.replace_text_in_file(
                            os.path.join(self.sqlalchemy_models_path, filename),
                            'blitzkrieg.project_management.db.models',
                            f"sqlalchemy_models"
                        )
                        self.file_manager.replace_text_in_file(
                            os.path.join(self.sqlalchemy_models_path, filename),
                            'sqlalchemy_models.Base',
                            'sqlalchemy_models.base'
                        )

                return self.console.handle_success(f"Copied SQLAlchemy models from [white]{self.models_directory}[/white] to [white]{self.sqlalchemy_models_path}[/white].")
        except Exception as e:
            return self.console.handle_error(f"Failed to copy SQLAlchemy models: {str(e)}")
