from rundbfast.core.cli.ui import print_error, print_header, print_message, print_success
from rundbfast.core.cli.user_input import get_pgadmin_credentials
from rundbfast.core.managers.manager import DockerManager, PgAdminManager
from rundbfast.core.shared.utils import wait_for_container


def initialize_pgadmin(project_name, postgres):
    print_header("PgAdmin Initialization")
    pgadmin = PgAdminManager(project_name)
    docker = DockerManager()
    pgadmin_email, pgadmin_password = get_pgadmin_credentials(postgres, f"{project_name}-postgres")
    print_message("Starting pgAdmin container...")
    pgadmin_port = pgadmin.start_container(pgadmin_email, pgadmin_password)

    if wait_for_container(docker, f"{project_name}-PgAdmin"):
        print_success(f"pgAdmin is now running. Access it at http://localhost:{pgadmin_port} using the email and password provided.")
    else:
        print_error("Failed to start the pgAdmin container.")

    return pgadmin, pgadmin_email
