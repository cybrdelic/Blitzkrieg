from ..cli.user_input import get_pgadmin_credentials, get_postgres_password
from .manager import DockerManager, PostgreSQLManager, PgAdminManager
from ..cli.ui import (print_message, show_progress, print_header, show_spinner,
                      print_success, print_warning, print_error)
from ..shared.utils import wait_for_container

DOCKER_IMAGE_POSTGRES = "postgres:latest"

def initialize_docker():
    print_header("Docker Initialization")
    docker = DockerManager()

    if not docker.is_installed():
        with show_progress("Installing Docker...") as progress:
            docker.install()
            progress.update(100)
            print_success("Docker installed successfully!")
    else:
        print_message("Docker is already installed.")

    return docker

def initialize_postgresql(docker, project_name):
    print_header("PostgreSQL Initialization")
    pg_password = get_postgres_password()
    if not docker.image_exists(DOCKER_IMAGE_POSTGRES):
        with show_progress(f"Pulling {DOCKER_IMAGE_POSTGRES}...") as progress:
            docker.pull_image(DOCKER_IMAGE_POSTGRES)
            progress.update(100)
            print_success(f"{DOCKER_IMAGE_POSTGRES} pulled successfully!")

    container_name = f"{project_name}-postgres"
    if docker.container_exists(container_name):
        print_warning(f"Container with name {container_name} already exists. Stopping and removing...")
        docker.remove_container(container_name)

    postgres = PostgreSQLManager(container_name)
    print_message(f"Starting container {container_name}...")
    used_port = postgres.start_container(pg_password)
    if wait_for_container(docker, container_name):
        print_success(f"PostgreSQL is now running on port {used_port}.")
        # Set up the project database
        postgres.setup_database(project_name)
    else:
        print_error(f"Failed to start the {container_name} container.")

    return postgres, pg_password

def initialize_pgadmin(project_name):
    print_header("PgAdmin Initialization")
    pgadmin = PgAdminManager(project_name)
    docker = DockerManager()
    pgadmin_email = None  # Initialize to None

    if pgadmin.container_exists():
        if pgadmin.is_container_running():
            print_message("pgAdmin container is already running.")
        else:
            print_warning("pgAdmin container exists but is not running. Restarting...")
            docker.runner.run_command(f"docker start {pgadmin.container_name}")
    else:
        pgadmin_email, pgadmin_password = get_pgadmin_credentials()
        print_message("Starting pgAdmin container...")
        pgadmin_port = pgadmin.start_container(pgadmin_email, pgadmin_password)

        if wait_for_container(docker, f"{project_name}-PgAdmin"):
            print_success(f"pgAdmin is now running. Access it at http://localhost:{pgadmin_port} using the email and password provided.")
        else:
            print_error("Failed to start the pgAdmin container.")

    return pgadmin, pgadmin_email
