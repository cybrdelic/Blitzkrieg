# alembic_manager.py

import os
import subprocess
import shutil
from typing import List
from blitzkrieg.db.models.base import Base
from blitzkrieg.db.models.issue import Issue
from blitzkrieg.db.models.project import Project
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.file_manager import FileManager
import sys

class AlembicManager:
    def __init__(self, db_manager, file_manager: FileManager, workspace_name: str, console: ConsoleInterface = None):
        self.workspace_name = workspace_name
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager
        self.file_manager = file_manager
        self.alembic_env_path = os.path.join(self.workspace_path, 'env.py')
        self.alembic_ini_path = os.path.join(self.workspace_path, 'alembic.ini')
        self.migrations_path = os.path.join(self.workspace_path, 'migrations')
        self.sqlalchemy_models_path = os.path.join(self.workspace_path, 'sqlalchemy_models')
        self.alembic_init__template_path = os.path.join(os.getcwd(), 'blitzkrieg', 'workspace_management', 'templates', 'alembic_init.sh')
        self.workspace_requirements_txt_template_path = os.path.join(os.getcwd(), 'blitzkrieg', 'workspace_management', 'templates', 'requirements.txt')
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
    def get_alembic_init_content(self):
        return f"""
[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python>=3.9 or backports.zoneinfo library.
# Any required deps can installed by adding `alembic[tz]` to the pip requirements
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "version_path_separator" below.
# version_locations = %(here)s/bar:%(here)s/bat:migrations/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
# If this key is omitted entirely, it falls back to the legacy behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql+psycopg2://$*workspace_name*$-db-user:pw@$*workspace_name*$-postgres:5432/$*workspace_name*$


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

"""
    def create_alembic_ini_file(self):
        try:
            self.console.handle_wait("Creating alembic.ini file...")
            alembic_init_content = self.get_alembic_init_content()
            with open(self.alembic_ini_path, 'w') as f:
                f.write(alembic_init_content)
            self.console.handle_success(f"Created alembic.ini file at [white]{self.alembic_ini_path}[/white]")
            self.console.display_file_content(self.alembic_ini_path)
        except Exception as e:
            return self.console.handle_error(f"Failed to create alembic.ini file: {str(e)}")


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

    def copy_alembic_init_script(self):
        try:
            if os.path.exists(self.alembic_init__template_path):
                shutil.copy(self.alembic_init__template_path, self.workspace_path)
                self.file_manager.chmod_permissions(os.path.join(self.workspace_path, 'alembic_init.sh'), 0o755)
                self.replace_variable_placeholders_in_alembic_init_script()
                return self.console.handle_success(f"Copied alembic_init.py to {self.workspace_path}")
            else:
                return self.console.handle_error(f"alembic_init.sh not found at {self.alembic_init__template_path}")
        except Exception as e:
            return self.console.handle_error(f"Failed to copy alembic_init.py: {str(e)}")

    def replace_variable_placeholders_in_alembic_init_script(self):
        workspace_alembic_init_script_path = os.path.join(self.workspace_path, 'alembic_init.sh')

        try:
            self.file_manager.replace_text_in_file(
                workspace_alembic_init_script_path,
                '$*workspace_name*$',
                self.workspace_name
            )
            self.console.handle_info(f"Replacing postgres_port variable placeholder in alembic_init.sh and setting its value to {self.db_manager.db_port}")
            self.file_manager.replace_text_in_file(
                workspace_alembic_init_script_path,
                '$*postgres_port*$',
                str(self.db_manager.db_port)
            )
            return self.console.handle_success(f"Replaced variable placeholders in alembic_init.sh")
        except Exception as e:
            return self.console.handle_error(f"Failed to replace variable placeholders in alembic_init.sh: {str(e)}")

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

    def copy_requirements_txt(self):
        self.copy_file_to_container(
            self.workspace_requirements_txt_template_path,
            os.path.join(self.workspace_path, 'requirements.txt')
        )
    def copy_file_to_container(self, file_path: str, container_path: str):
        try:
            if os.path.exists(file_path):
                shutil.copy(file_path, container_path)
                return self.console.handle_success(f"Copied {file_path} to {container_path}")
            else:
                return self.console.handle_error(f"File not found: {file_path}")
        except Exception as e:
            return self.console.handle_error(f"Failed to copy file to container: {str(e)}")


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
        self.console.display_file_content(self.alembic_env_path)

    def get_new_env_py_content(self):
        return f"""
from sqlalchemy import create_engine, text
from alembic import context
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
from sqlalchemy_models.base import Base

# Reflect the metadata
metadata = Base.metadata
for cls in Base.__subclasses__():
    cls.__table__.metadata = metadata

url = '{self.db_manager.get_sqlalchemy_uri()}'
config = context.config
config.set_main_option('sqlalchemy.url', url)

from sqlalchemy_models.base import Base  # Replace 'myapp.models' with the actual path to your models
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
        create_schemas(connection)  # Create necessary schemas before running migrations
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
        return

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
