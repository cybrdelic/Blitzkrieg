from ..core.manager import DockerManager, PostgreSQLManager, PgAdminManager
from .ui import print_message, show_progress

def initialize_docker():
    docker = DockerManager()
    if not docker.is_installed():
        with show_progress("Installing Docker...") as progress:
            docker.install()
            progress.update(100)
        print_message("Docker installed successfully!", style="bold green")
    else:
        print_message("Docker is already installed.", style="bold blue")
    return docker

def initialize_postgresql(docker, project_name, pg_password):
    docker.pull_image("postgres:latest")

    container_name = f"{project_name}-postgres"
    if docker.container_exists(container_name):
        print_message(f"Container with name {container_name} already exists. Stopping and removing...", style="bold yellow")
        docker.remove_container(container_name)

    postgres = PostgreSQLManager(container_name)
    print_message(f"Starting container {container_name}...", style="bold yellow")
    used_port = postgres.start_container(pg_password)
    print_message(f"PostgreSQL is now running on port {used_port}.", style="bold green")

    print_message("Waiting for PostgreSQL to be ready...", style="bold yellow")
    postgres.wait_for_ready()
    postgres.setup_database(project_name)

    return postgres

def initialize_pgadmin(project_name):
    pgadmin = PgAdminManager(project_name)
    if pgadmin.container_exists():
        print_message("pgAdmin container already exists. Stopping and removing...", style="bold yellow")
        pgadmin.remove_container()

    print_message("Starting pgAdmin container...", style="bold yellow")
    pgadmin_port = pgadmin.start_container()
    print_message(f"pgAdmin is now running. Access it at http://localhost:{pgadmin_port} using the credentials provided.", style="bold green")

    return pgadmin
