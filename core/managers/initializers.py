from rundbfast.cli.user_input import get_pgadmin_credentials, get_postgres_password
from rundbfast.managers.manager import DockerManager, PostgreSQLManager, PgAdminManager
from rundbfast.cli.ui import (print_message, show_progress, print_header, show_spinner,
                      print_success, print_warning, print_error)
from rundbfast.shared.utils import wait_for_container

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

    # Get password for PostgreSQL
    pg_password = get_postgres_password()

    # Adjust the image pulling process in your main code
    if not docker.image_exists(DOCKER_IMAGE_POSTGRES):
        with show_progress(f"Pulling {DOCKER_IMAGE_POSTGRES}...") as progress:
            for percentage in docker.pull_image(DOCKER_IMAGE_POSTGRES):
                progress.completed = percentage
            print_success(f"{DOCKER_IMAGE_POSTGRES} pulled successfully!")


    # Handle existing containers
    container_name = f"{project_name}-postgres"
    if docker.container_exists(container_name):
        print_warning(f"Container with name {container_name} already exists. Stopping and removing...")
        docker.remove_container(container_name)

    # Handle data persistence by setting up a Docker volume
    volume_name = f"{project_name}-postgres-volume"
    if not docker.volume_exists(volume_name):
        docker.create_volume(volume_name)

    # Initialize and start the PostgreSQL container
    postgres = PostgreSQLManager(container_name)
    print_message(f"Starting container {container_name} with data persistence...")
    used_port = postgres.start_container(pg_password, volume_name)

    # Check and handle the container's status
    if wait_for_container(docker, container_name):
        print_success(f"PostgreSQL is now running with data persistence on port {used_port}.")
        postgres.setup_database(project_name)
    else:
        print_error(f"Failed to start the {container_name} container.")

    return postgres, pg_password, used_port


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
