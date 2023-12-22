import click
from blitzkrieg.initialization.project_init import initialize_project
import os
import time
import subprocess

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

@main.command()
def all():
    """Initialize the application."""
    for project in projects:
        initialize_project(project)
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
def link_projects(project_name_1, project_name_2, parent_name):
    """Link two projects and add both PostgreSQL servers to a single parent pgAdmin."""
    # Create a new Docker network
    network_name = f'{parent_name}-network'
    subprocess.run(['docker', 'network', 'create', network_name], check=True)

    # Connect the projects to the network
    subprocess.run(['docker', 'network', 'connect', network_name, project_name_1], check=True)
    subprocess.run(['docker', 'network', 'connect', network_name, project_name_2], check=True)

    # Run pgAdmin on the same network
    subprocess.run([
        'docker', 'run', '-p', '80:80',
        '--network', network_name,
        '-e', f'PGADMIN_DEFAULT_EMAIL={parent_name}@example.com',
        '-e', 'PGADMIN_DEFAULT_PASSWORD=secret',
        '-d',
        '--name', parent_name,
        'dpage/pgadmin4'
    ], check=True)


if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
