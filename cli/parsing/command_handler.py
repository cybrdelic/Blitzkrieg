from rundbfast.cli.ui import pause_for_user, print_cli_footer, print_label
from rundbfast.cli.user_input import get_project_name
from rundbfast.core.initializers.pgadmin_initializer import PgAdminInitializer
from rundbfast.core.managers.docker_manager import DockerManager
from rundbfast.core.managers.postgres_manager import PostgreSQLManager


class CommandHandler:
    def __init__(self):
        self.docker = DockerManager()
        self.postgres = PostgreSQLManager()
        self.pgadmin = PgAdminInitializer()

    @staticmethod
    def setup(self, args):
        project_name = get_project_name()
        print_label(f"Setting up for project: {project_name}")
        pause_for_user()
        self.docker.install()
        self.postgres.initialize_with_persistence_check(project_name)
        self.pgadmin.initialize(project_name, self.postgres)
        print_cli_footer()



    @staticmethod
    def setup_meta(self, args):
        print_label(f"Setting up meta database for RunDBFast")
        self.postgres.setup_meta_database(self.docker)
