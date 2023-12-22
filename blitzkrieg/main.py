import click
from blitzkrieg.config import get_config
from blitzkrieg.initialization.create_pgadmin_server import create_pgadmin_server_json, run_pgadmin_container
from blitzkrieg.initialization.project_init import initialize_project
import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
import socket

projects = [
    'blitzkrieg',
    'jjugg',
    'nxiqai',
    'codegyp',
    'alexfigueroatech',
    'economaestro',
    'profilomesh',
    'termifolio',
]
@click.group()
def main():
    pass

@main.command()
@click.argument('project_name')
def init(project_name):
    """Initialize the application."""
    initialize_project(project_name)
    # rest of your code

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@main.command()
def all():
    """Initialize the application."""
    base_postgres_port = 5432
    base_pg_admin_port = 5050
    with ThreadPoolExecutor() as executor:
        for i, project in enumerate(projects):
            postgres_port = base_postgres_port + i
            while is_port_in_use(postgres_port):
                postgres_port += 1

            pg_admin_port = base_pg_admin_port + i
            while is_port_in_use(pg_admin_port):
                pg_admin_port += 1

            executor.submit(initialize_project, project, postgres_port, pg_admin_port)
    # rest of your code
    # rest of your code
@main.command()
def remover():
    """Initialize the application."""
    for project in projects:
        os.system(f"docker stop {project}-postgres")
        os.system(f"docker stop {project}-pgadmin")
        os.system(f"docker rm {project}-postgres")
        os.system(f"docker rm {project}-pgadmin")
        os.system(f"docker network rm {project}-network")
    # rest of your code
@main.command()
@click.argument('project_name')
def remove(project_name):
    """Remove the application."""

    os.system(f"docker stop {project_name}-postgres")
    os.system(f"docker stop {project_name}-pgadmin")
    os.system(f"docker rm {project_name}-postgres")
    os.system(f"docker rm {project_name}-pgadmin")
    os.system(f"docker network rm {project_name}-network")

@main.command()
@click.argument('project_name_1')
@click.argument('project_name_2')
@click.argument('parent_name')
def link(project_name_1, project_name_2, parent_name):
    """Link two projects and add both PostgreSQL servers to a single parent pgAdmin."""
    # Create the servers.json file for each project
    create_pgadmin_server_json(project_name_1, 1)
    create_pgadmin_server_json(project_name_2, 2)

    # Create a new Docker network
    network_name = f'{parent_name}-network'
    try:
        subprocess.run(['docker', 'network', 'inspect', network_name], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        subprocess.run(['docker', 'network', 'create', network_name], check=True)

    # Connect the projects to the network
    subprocess.run(['docker', 'network', 'connect', network_name, f"{project_name_1}-postgres"], check=True)
    subprocess.run(['docker', 'network', 'connect', network_name, f"{project_name_2}-postgres"], check=True)

    # Run the pgAdmin container with Docker, not Docker Compose
    os.system(f'docker run -d --name {parent_name}-pgadmin --network={network_name} -v ./{project_name_1}_servers.json:/pgadmin4/servers.json -v ./{project_name_2}_servers.json:/pgadmin4/servers.json dpage/pgadmin4')

if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
