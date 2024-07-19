from concurrent.futures import ThreadPoolExecutor
from blitzkrieg.codebase_scaffolding.config.config import load_user_details
import socket
import json
import os
import subprocess
from blitzkrieg.codebase_scaffolding.dir_management.create_project import create_new_project
from blitzkrieg.codebase_scaffolding.github.github import create_github_repo, delete_github_repo
from blitzkrieg.codebase_scaffolding.github.connect_to_github_repo import connect_to_github_repo
from blitzkrieg.utils.port_allocation import find_available_port
import shutil

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

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def remove_project(project):
    os.system(f"docker stop {project}-postgres")
    os.system(f"docker stop {project}-pgadmin")
    os.system(f"docker rm {project}-postgres")
    os.system(f"docker rm {project}-pgadmin")
    os.system(f"docker network rm {project}-network")

def create_servers_json(project_name_1, project_name_2):
    # Create password files and write passwords to them
    with open(f"{project_name_1}_passfile.txt", 'w') as f:
        f.write("0101")  # Replace with actual password
    with open(f"{project_name_2}_passfile.txt", 'w') as f:
        f.write("0101")  # Replace with actual password

    servers = {
        "Servers": {
            "1": {
                "Name": f"{project_name_1}-postgres",
                "Group": "Servers",
                "Host": f"{project_name_1}-postgres",
                "Port": 5432,
                "MaintenanceDB": project_name_1,
                "Username": f"{project_name_1}-db-user",
                "SSLMode": "prefer",
                "PassFile": "/var/lib/pgadmin/pgpassfile"
            },
            "2": {
                "Name": f"{project_name_2}-postgres",
                "Group": "Servers",
                "Host": f"{project_name_2}-postgres",
                "Port": 5432,
                "MaintenanceDB": project_name_2,
                "Username": f"{project_name_2}-db-user",
                "SSLMode": "prefer",
                "PassFile": "/var/lib/pgadmin/pgpassfile"
            }
        }
    }

    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)


    # rest of your code
def handle_remover_postgres_pgadmin_command():
    """Initialize the application."""
    with ThreadPoolExecutor() as executor:
        executor.map(remove_project, projects)

def handle_remove_postgres_pgadmin_command(project_name):
    """Initialize the application."""
    remove_project(project_name)

def handle_link_pgadmin_postgres_command(
        project_name_1,
        project_name_2,
        parent_name
):
    """Link two projects and add both PostgreSQL servers to a single parent pgAdmin."""
    # Create the servers.json file that contains both projects' PostgreSQL servers
    create_servers_json(project_name_1, project_name_2)
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
    # Choose a port for pgAdmin. Make sure this port is not being used by another service.
    pgadmin_port = find_available_port(5050)

    pgadmin_run_command = (
        f"docker run -d --name {parent_name}-pgadmin "
        f"--network={network_name} "
        f'-e "PGADMIN_DEFAULT_EMAIL"=admin@example.com '
        f'-e "PGADMIN_DEFAULT_PASSWORD=0101" '
        f"-p {pgadmin_port}:80 "  # Map the host port to the container's port 80
        f"-v $(pwd)/servers.json:/pgadmin4/servers.json "
        f"dpage/pgadmin4"
    )

    # Print the Docker command
    print(f"Docker command: {pgadmin_run_command}")

    os.system(pgadmin_run_command)

    print(f"pgAdmin setup complete. Access it at http://localhost:{pgadmin_port}")

def handle_create_project_command():
    """Create a new project."""
    create_new_project()
    create_github_repo()
    connect_to_github_repo()
    pass

def handle_delete_project_command():
    """Delete a project."""
    details = load_user_details()
    project_name = details['project_name']
    os.system('ls')

    if os.path.isdir(project_name):
        try:
            shutil.rmtree(project_name)
            print(f'Successfully removed directory "{project_name}"')
        except Exception as e:
            print(f'Error while removing directory "{project_name}": {e}')
    else:
        print(f'Directory "{project_name}" does not exist')

    delete_github_repo()
