# rundbfast/managers/initializer/postgresql_initializer.py

from rundbfast.shared.utils import get_postgres_password

from rundbfast.core.cli.ui import print_error, print_header, print_message, print_success, print_warning, show_progress
from rundbfast.core.managers.initializers import DOCKER_IMAGE_POSTGRES
from rundbfast.core.managers.postgres_manager import PostgreSQLManager
from rundbfast.core.shared.utils import wait_for_container

def initialize_postgresql(docker, project_name):
    print_header("PostgreSQL Initialization")

    pg_password = get_postgres_password()
    docker_image = DOCKER_IMAGE_POSTGRES

    _pull_postgres_image(docker, docker_image)
    container_name, volume_name = _prepare_postgres_container(docker, project_name, pg_password)
    _start_and_setup_postgres_container(docker, container_name, volume_name, pg_password, project_name)

def _pull_postgres_image(docker, docker_image):
    if not docker.image_exists(docker_image):
        with show_progress(f"Pulling {docker_image}...") as progress:
            for percentage in docker.pull_image(docker_image):
                progress.completed = percentage
            print_success(f"{docker_image} pulled successfully!")

def _prepare_postgres_container(docker, project_name, pg_password):
    container_name = f"{project_name}-postgres"
    if docker.container_exists(container_name):
        print_warning(f"Container with name {container_name} already exists. Stopping and removing...")
        docker.remove_container(container_name)

    volume_name = f"{project_name}-postgres-volume"
    if not docker.volume_exists(volume_name):
        docker.create_volume(volume_name)

    return container_name, volume_name

def _start_and_setup_postgres_container(docker, container_name, volume_name, pg_password, project_name):
    postgres = PostgreSQLManager(container_name)
    print_message(f"Starting container {container_name} with data persistence...")
    used_port = postgres.start_container(pg_password, volume_name)

    if wait_for_container(docker, container_name):
        print_success(f"PostgreSQL is now running with data persistence on port {used_port}.")
        postgres.setup_database(project_name)
    else:
        print_error(f"Failed to start the {container_name} container.")
