import os

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.ui_management.decorators import with_spinner
import subprocess
import time

from blitzkrieg.utils.run_command import run_command

class WorkspaceDirectoryManager:
    def __init__(self, db_manager, workspace_name: str = None):
        self.workspace_name = workspace_name
        self.console = ConsoleInterface()
        self.workspace_path = os.path.join(os.getcwd(), self.workspace_name)
        self.db_manager = db_manager

    def teardown(self):
        self.console.display_step('Tearing Down Workspace Directory', 'Tearing down workspace directory...')
        self.delete_workspace_directory()

    @with_spinner(
        message="Deleting workspace directory ...",
        failure_message="Failed to delete workspace directory.",
        success_message="Workspace directory deleted successfully."
    )
    def delete_workspace_directory(self):
        try:
            subprocess.run(['rm', '-rf', self.workspace_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.console.display_notice(f"Failed to delete workspace directory: {str(e)}")
            return False

    def create_dir(self, dir_path):
        os.makedirs(dir_path, exist_ok=True)

    @with_spinner(
        message="Creating workspace directory ...",
        failure_message="Failed to create workspace directory.",
        success_message="Workspace directory created successfully."
    )
    def create_workspace_directory(self):
        try:
            os.makedirs(self.workspace_path, exist_ok=True)
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create workspace directory: {str(e)}")
            return False

    @with_spinner(
        message="Creating /projects directory inside of workspace",
        failure_message="Failed to create /projects directory inside of workspace.",
        success_message="/projects directory created successfully."
    )
    def create_projects_directory(self):
        try:
            projects_path = os.path.join(self.workspace_path, 'projects')
            self.create_dir(projects_path)
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create /projects directory inside of workspace: {str(e)}")
            return False
    @with_spinner(
        message="Creating /sqlalchemy_models directory inside of workspace",
        failure_message="Failed to create /sqlalchemy_models directory inside of workspace.",
        success_message="/sqlalchemy_models directory created successfully."
    )
    def create_sqlalchemy_models_directory(self):
        try:
            sqlalchemy_models_path = os.path.join(self.workspace_path, 'sqlalchemy_models')
            self.create_dir(sqlalchemy_models_path)
            self.create_workspace_details_table_sqlalchemy_model()
            self.create_project_table_sqlalchemy_model()
            self.modify_env_dot_py_to_import_models_and_configure_target_metadata()
            self.auto_generate_initial_alembic_migration_script()
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create /sqlalchemy_models directory inside of workspace: {str(e)}")
            return False

    def create_sql_alchemy_model_file(self, model_name):
        try:
            with open(os.path.join(self.workspace_path, 'sqlalchemy_models', f'{model_name}.py'), 'w') as f:
                f.write(f"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class {model_name}(Base):
    __tablename__ = '{model_name.lower()}'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return f'<{model_name}(name={{self.name}}, description={{self.description}})>'
""")

            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create SQLAlchemy model file: {str(e)}")
            return False
    @with_spinner(
        message="Creating SQLAlchemy model for workspace...",
        failure_message="Failed to create SQLAlchemy model for workspace.",
        success_message="SQLAlchemy model for workspace created successfully."
    )
    def create_workspace_details_table_sqlalchemy_model(self):
        try:
            self.console.display_step('Creating SQLAlchemy Model', 'Creating a SQLAlchemy model for the workspace...')
            self.create_sql_alchemy_model_file('WorkspaceDetails')
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create SQLAlchemy model for workspace details: {str(e)}")
            return False

    def create_project_table_sqlalchemy_model(self):
        try:
            self.console.display_step('Creating SQLAlchemy Model', 'Creating a SQLAlchemy model for the project table...')
            self.create_sql_alchemy_model_file('Project')
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to create SQLAlchemy model for project table: {str(e)}")
            return False

    @with_spinner(
        message="Creating and modifying env.py...",
        failure_message="Failed to create and modify env.py.",
        success_message="env.py created and modified successfully."
    )
    def modify_env_dot_py_to_import_models_and_configure_target_metadata(self):
        try:
            with open(os.path.join(self.workspace_path, 'env.py'), 'w') as f:
                f.write(f'''
from sqlalchemy_models import Base
from sqlalchemy import create_engine
from alembic import context
config = context.config
config.set_main_option('sqlalchemy.url', 'sqlite:///db.sqlite')
target_metadata = Base.metadata'''
                        )
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to modify env.py to import models and configure target metadata: {str(e)}")
            return False

    @with_spinner(
        message="Auto-generating initial Alembic migration script...",
        failure_message="Failed to auto-generate initial Alembic migration script.",
        success_message="Initial Alembic migration script auto-generated successfully."
    )
    def auto_generate_initial_alembic_migration_script(self):
        try:
            time.sleep(5)
            run_command('alembic revision --autogenerate -m "Initial"')
            return True
        except subprocess.CalledProcessError as e:
            self.console.display_notice(f"Failed to auto-generate initial Alembic migration script: {str(e)}")
            return False


    @with_spinner(
        message="Installing Alembic...",
        failure_message="Failed to install Alembic.",
        success_message="Alembic installed successfully."
    )
    def install_alembic(self):
        """ Installs Alembic. """
        try:
            subprocess.run(['pip', 'install', 'alembic'], cwd=self.workspace_path, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.console.display_notice(f"Failed to install Alembic: {str(e)}")
            return False


    @with_spinner(
        message="Initializing Alembic...",
        failure_message="Failed to initialize Alembic.",
        success_message="Alembic initialized successfully."
    )
    def initialize_alembic(self):
        try:
            subprocess.run(['alembic', 'init', 'migrations'], cwd=self.workspace_path, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.console.display_notice(f"Failed to initialize Alembic: {str(e)}")
            return False

    def setup_alembic(self):
        """ Fully sets up Alembic in the workspace. """
        self.install_alembic()
        self.initialize_alembic()
        self.update_sqlalchemy_uri()

    @with_spinner(
        message="Updating SQLAlchemy URI...",
        failure_message="Failed to update SQLAlchemy URI.",
        success_message="SQLAlchemy URI updated successfully."
    )
    def change_sqlalchemy_uri(self, uri):
        """ Changes the SQLAlchemy URI in the Alembic configuration file. """
        try:
            with open(os.path.join(self.workspace_path, 'alembic.ini'), 'r') as f:
                lines = f.readlines()
            with open(os.path.join(self.workspace_path, 'alembic.ini'), 'w') as f:
                for line in lines:
                    if line.startswith('sqlalchemy.url'):
                        f.write(f'sqlalchemy.url = {uri}\n')
                    else:
                        f.write(line)
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to update SQLAlchemy URI: {str(e)}")
            return False

    def does_sqlalchemy_dot_url_line_exist(self):
        """ Checks if the 'sqlalchemy.url' line exists in the Alembic configuration file. """
        try:
            with open(self.get_alembic_ini_path(), 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('sqlalchemy.url'):
                    return True
        except Exception as e:
            self.console.display_notice(f"Failed to check if the 'sqlalchemy.url' line exists: {str(e)}")
            return False

    def get_alembic_ini_path(self):
        """ Gets the path to the Alembic configuration file. """
        return os.path.join(self.workspace_path, 'alembic.ini')

    @with_spinner(
            message="Getting Alembic ini path...",
            failure_message="Failed to get Alembic ini path.",
            success_message="Alembic ini path successfully retrieved."
    )
    def check_alembic_ini_path(self):
        try:
            alembic_ini_path = self.get_alembic_ini_path()
            self.console.print(f"Alembic ini path: {str(alembic_ini_path)} ")
            return True
        except Exception as e:
            self.console.display_notice(f"Failed to get Alembic ini path: {str(e)}")
            return False

    def update_sqlalchemy_uri(self):
        """ Updates the SQLAlchemy URI in the Alembic configuration file. """
        self.console.display_step('Updating SQLAlchemy URI', 'Updating the SQLAlchemy URI in the Alembic configuration file...')
        self.check_alembic_ini_path()
        self.does_sqlalchemy_dot_url_line_exist()
        self.change_sqlalchemy_uri(self.db_manager.get_sqlalchemy_uri())

    # I want to add alembic into the workspace directory, but im unsure how i should go about this, because i dont want create it without virtualenv. or maybe i shouldnt care because the user should already be installing blitzxkrieg in a venv?
