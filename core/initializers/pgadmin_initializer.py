from rundbfast.cli.ui import print_header, print_message, print_success, print_warning, print_error
from rundbfast.cli.user_input import get_pgadmin_credentials
from rundbfast.shared.utils import wait_for_container
from rundbfast.managers.manager import DockerManager, PgAdminManager

class PgAdminInitializer:
    @staticmethod
    def initialize(project_name, postgres):
        print_header("PgAdmin Initialization")
        docker = DockerManager()
        pgadmin_email, pgadmin_password = get_pgadmin_credentials(postgres, f"{project_name}-postgres")
        pgadmin = PgAdminManager(project_name)
        pgadmin_port = pgadmin.start_container(pgadmin_email, pgadmin_password)

        if wait_for_container(docker, f"{project_name}-PgAdmin"):
            print_success(f"pgAdmin is now running. Access it at http://localhost:{pgadmin_port} using the email and password provided.")
        else:
            print_error("Failed to start the pgAdmin container.")

        return pgadmin, pgadmin_email
