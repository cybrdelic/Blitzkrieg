from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
import os

class AlembicCommandRunner:
    def __init__(self, console: ConsoleInterface, workspace_name: str):
        self.console = console
        self.workspace_name = workspace_name
        self.workspace_path = os.path.join(os.getcwd(), workspace_name)

    def install_alembic(self):
        self.console.handle_wait("Installing Alembic...")
        self.console.execute_command(['pip', 'install', 'alembic'], self.workspace_name, "Installing Alembic via pip...")

    def install_psycopg2_binary(self):
        self.console.execute_command(['pip', 'install', 'psycopg2-binary'], self.workspace_path, "Installing psycopg2-binary via pip...")

    def initialize_alembic(self):
        self.console.execute_command(['alembic', 'init', 'alembic'], self.workspace_path, "Initializing Alembic...")

    def auto_generate_initial_alembic_migration_script(self):
        self.console.execute_command(['alembic', 'revision', '--autogenerate', '-m', 'Initial'], self.workspace_path, "Generating initial migration script...")

    def generate_blank_migration(self, label):
        command = ['alembic', 'revision', '--autogenerate', '-m', label]
        self.console.execute_command(command, self.workspace_path, f"Generating blank migration for {label}.")

    def run_migrations(self):
        self.console.execute_command(['alembic', 'upgrade', 'head'], self.workspace_path, "Running migrations...")

    def generate_initial_migrations(self):
        self.console.execute_command(
            ['alembic', 'revision', '--autogenerate', '-m', 'initial'],
            self.workspace_path,
            "Generating initial migrations..."
        )
