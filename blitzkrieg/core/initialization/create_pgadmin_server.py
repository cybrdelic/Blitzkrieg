import json
import json
import os

from blitzkrieg.core.initialization.project_init import run_command
from blitzkrieg.core.networking.port_allocation import find_available_port

def create_pgadmin_server_json(project_name: str, server_id: int):
    file_name = f"{project_name}_servers.json"
    server_config = {
        "Name": project_name,
        "Host": f"{project_name}-postgres",
        "Port": 5432,
        "MaintenanceDB": project_name,
        "Username": f"{project_name}-db-user",
        "SSLMode": "prefer",
        "PassFile": "/var/lib/pgadmin/pgpassfile"
    }

    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            servers_json = json.load(f)
    else:
        servers_json = {"Servers": {}}

    servers_json["Servers"][str(server_id)] = server_config

    with open(file_name, 'w') as f:
        json.dump(servers_json, f)

def run_pgadmin_container(project_name: str):
    network_name = f"{project_name}-network"
    pgadmin_port = find_available_port(5050)

    # Get the absolute path of the current directory
    current_dir = os.path.abspath(os.getcwd())

    # Construct the absolute path of the servers.json file
    servers_file_path = os.path.join(current_dir, "servers.json")

    # Print the content of the servers.json file
    with open(servers_file_path, 'r') as f:
        print(f"Content of servers.json: {f.read()}")

    pgadmin_run_command = (
        f"docker run -d --name {project_name}-pgadmin -p {pgadmin_port}:80 "
        f"-e 'PGADMIN_DEFAULT_EMAIL=admin@example.com' "
        f"-e 'PGADMIN_DEFAULT_PASSWORD=0101' "
        f"--network {network_name} "
        f"-v {servers_file_path}:/pgadmin4/servers.json "
        "dpage/pgadmin4"
    )

    # Print the Docker command
    print(f"Docker command: {pgadmin_run_command}")

    run_command(pgadmin_run_command)

    # Inspect the Docker container
    inspect_command = f"docker inspect {project_name}-pgadmin"
    print(f"Inspect command: {inspect_command}")
    run_command(inspect_command)
