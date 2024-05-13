from blitzkrieg.db.models.issue import Issue
from blitzkrieg.db.models.project import Project
from blitzkrieg.db.models.Base import Base
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner
import subprocess
import os
import shutil
import sys

class AlembicManager:
    def __init__(self, db_manager, workspace_name: str = None):
        self.workspace_name = workspace_name
        self.console = ConsoleInterface()
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager
        self.alembic_env_path = os.path.join(self.workspace_path, 'migrations/env.py')
        self.alembic_ini_path = os.path.join(self.workspace_path, 'alembic.ini')
        self.migrations_path = os.path.join(self.workspace_path, 'migrations')
        self.sqlalchemy_models_path = os.path.join(self.workspace_path, 'sqlalchemy_models')
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
                self.console.print(f"Created __init__.py in {path}")

    def remove_last_dir_from_path_and_keep_the_beginning(self, path):
        """ Removes the last directory from a path and returns the beginning part. """
        return os.path.dirname(path)

    @with_spinner(
        message="Copying SQLAlchemy models to workspace...",
        failure_message="Failed to copy SQLAlchemy models.",
        success_message="SQLAlchemy models copied successfully."
    )
    def copy_sqlalchemy_models(self):
        self.console.print(f"sqlalchemy_models dir: {self.sqlalchemy_models_path}")
        self.console.print(f"models dir: {self.models_directory}")
        """ Copies the SQLAlchemy model files from a specified directory to the workspace. """
        if self.models_directory and os.path.exists(self.models_directory):
            for filename in os.listdir(self.models_directory):
                full_file_path = os.path.join(self.models_directory, filename)
                if os.path.isfile(full_file_path) and filename.endswith('.py'):
                    shutil.copy(full_file_path, self.sqlalchemy_models_path)
                    self.console.print(f"Copied {filename} to {self.sqlalchemy_models_path}")


    def execute_command(self, command, directory, message=None):
        """ Utility method to execute a command with logging. """
        self.console.print(f"Executing command: {' '.join(command)}")
        self.console.print(f"Directory: {directory}")
        if message:
            self.console.print(message)
        try:
            subprocess.run(command, cwd=directory, check=True)
            self.console.print("Command executed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self.console.display_notice(f"Command failed: {str(e)}")
            return False

    @with_spinner(
        message="Setting up Alembic...",
        failure_message="Failed to set up Alembic.",
        success_message="Alembic set up successfully."
    )
    def setup_alembic(self):
        """ Fully sets up Alembic in the workspace. """
        self.create_sqlalchemy_models_directory()
        self.copy_sqlalchemy_models()
        self.install_alembic()
        self.initialize_alembic()
        self.create_init_files()
        self.update_sqlalchemy_uri()
        self.update_alembic_env()
        self.setup_alembic_for_schemas()
        self.auto_generate_initial_alembic_migration_script()
        self.run_migrations()

    def create_sqlalchemy_models_directory(self):
        """ Ensure the sqlalchemy_models directory is created and models are initialized. """
        if not os.path.exists(self.sqlalchemy_models_path):
            os.makedirs(self.sqlalchemy_models_path, exist_ok=True)
            self.console.print(f"Created sqlalchemy_models directory at {self.sqlalchemy_models_path}")
            sys.path.append(self.workspace_path)
        # Optionally, also ensure that model files are present or generate them

    @with_spinner(
        message="Installing Alembic...",
        failure_message="Failed to install Alembic.",
        success_message="Alembic installed successfully."
    )
    def install_alembic(self):
        """ Installs Alembic. """
        return self.execute_command(['pip', 'install', 'alembic'], self.workspace_path)

    @with_spinner(
        message="Initializing Alembic...",
        failure_message="Failed to initialize Alembic.",
        success_message="Alembic initialized successfully."
    )
    def initialize_alembic(self):
        """ Initializes the Alembic directory. """
        return self.execute_command(['alembic', 'init', 'migrations'], self.workspace_path)

    def replace_line_in_file(self, file_path, old_line, new_line):
        """ Replaces a line in a file with a new line. """
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            with open(file_path, 'w') as file:
                for line in lines:
                    if line.strip() == old_line:
                        file.write(new_line + '\n')
                        return True
                    else:
                        file.write(line)
                        return True
        except Exception as e:
            self.console.display_notice(f"Failed to replace line in file: {str(e)}")
            return False

    def update_sqlalchemy_uri(self):
        """ Updates the SQLAlchemy URI in the Alembic configuration file. """
        try:
            with open(self.alembic_ini_path, 'r') as f:
                lines = f.readlines()
            with open(self.alembic_ini_path, 'w') as f:
                for line in lines:
                    if line.startswith('sqlalchemy.url'):
                        f.write(f'sqlalchemy.url = {self.db_manager.get_sqlalchemy_uri()}\n')
                    else:
                        f.write(line)
            self.console.print("SQLAlchemy URI updated successfully in the Alembic configuration.")
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to update SQLAlchemy URI: {str(e)}")
            return False

    def update_alembic_env(self):
        """ Updates the 'target_metadata' line in the Alembic environment file. """
        env_content = self.get_new_env_py_content()
        self.write_env_py_content_to_file(env_content)

    def get_new_env_py_content(self):
        """ Generates new content for the env.py file with dynamic imports and configuration. """
        return f"""
from sqlalchemy import create_engine
from alembic import context
import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(__file__)))

# Dynamically adjust the path to ensure imports work correctly
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("{str(self.workspace_path)}")

# Dynamically import all models
from {self.workspace_name}.sqlalchemy_models.Base import Base

# Set the SQLAlchemy database URL
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
        """ Writes the updated env.py content to the file. """
        with open(self.alembic_env_path, 'w') as env_file:
            env_file.write(content)
        self.console.display_notice("env.py updated successfully for Alembic.")

    def auto_generate_initial_alembic_migration_script(self):
        """ Auto-generates an initial Alembic migration script. """
        return self.execute_command(['alembic', 'revision', '--autogenerate', '-m', 'Initial'], self.workspace_path)

    @with_spinner(
        message="Running migrations...",
        failure_message="Failed to run migrations.",
        success_message="Migrations run successfully."
    )
    def run_migrations(self):
        """ Executes the Alembic migration to the latest version. """
        return self.execute_command(['alembic', 'upgrade', 'head'], self.workspace_path)

    def setup_alembic_for_schemas(self):
        """ Sets up and runs Alembic migrations for creating schemas. """
        for schema in self.initial_schema_names:
            migration_label = f"create_{schema}_schema"
            self.generate_blank_migration(migration_label)
            self.modify_migration_for_schema(schema, migration_label)
        self.run_migrations()

    def generate_blank_migration(self, label):
        """ Generates a blank Alembic migration for schema creation. """
        command = ['alembic', 'revision', '--autogenerate', '-m', label]
        self.execute_command(command, self.workspace_path, f"Generating blank migration for {label}.")

    def modify_migration_for_schema(self, schema_name, migration_label):
        """ Modifies a migration file to include SQL for schema creation. """
        migration_file = self.find_migration_file(migration_label)
        if migration_file:
            self.insert_schema_creation_sql(migration_file, schema_name)

    def find_migration_file(self, label):
        """ Finds the migration file containing the specified label. """
        versions_path = os.path.join(self.migrations_path, 'versions')
        for filename in os.listdir(versions_path):
            if label in filename:
                return os.path.join(versions_path, filename)
        return None

    def insert_schema_creation_sql(self, migration_file, schema_name):
        """ Inserts SQL for creating a schema into the migration file. """
        with open(migration_file, 'r+') as file:
            content = file.read()
            position = content.find('def upgrade():')
            if position != -1:
                upgrade_section = f"\n    op.execute('CREATE SCHEMA IF NOT EXISTS {schema_name}')\n"
                content = content[:position + len('def upgrade():')] + upgrade_section + content[position + len('def upgrade():'):]
                file.seek(0)
                file.write(content)
                file.truncate()
            self.console.print(f"Added schema creation SQL for {schema_name} in {migration_file}.")

    def auto_generate_schema_migrations(self):
        """ Triggers auto-generation of schema-specific migrations. """
        self.console.display_step("Generating migrations for schemas", "Running migrations for the initial setup of schemas...")
        for schema in self.initial_schema_names:
            migration_label = f"Add {schema}"
            self.generate_blank_migration(migration_label)
            self.modify_migration_for_schema(schema, migration_label)
        self.run_migrations()

    def run_schema_migrations(self):
        """ Runs the migrations that add schemas to the database. """
        self.console.display_step("Running Schema Migrations", "Applying schema migrations to the database...")
        self.run_migrations()
