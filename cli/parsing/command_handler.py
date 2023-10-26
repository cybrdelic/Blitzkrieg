from cli.ui import pause_for_user, print_cli_footer, print_label
from cli.user_input import get_project_name
from core.initializers.pgadmin_initializer import PgAdminInitializer
from core.managers.docker_manager import DockerManager
from core.managers.postgres_manager import PostgreSQLManager

class CommandHandler:
    def __init__(self, runner):
        self.docker = DockerManager()
        self.postgres = PostgreSQLManager(runner)
        self.pgadmin = PgAdminInitializer()
        self.runner = runner

    def setup(self, args):
        project_name = get_project_name()
        print_label(f"Setting up for project: {project_name}")
        pause_for_user()
        self.docker.install()
        self.postgres.initialize_with_persistence_check(project_name)
        self.pgadmin.initialize(project_name, self.postgres)
        print_cli_footer()

    def setup_meta(self, args):
        print_label(f"Setting up meta database for RunDBFast")
        self.postgres.setup_meta_database(self.docker)
