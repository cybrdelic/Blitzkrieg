import json
import json
import os

from blitzkrieg.initialization.project_init import run_command
from blitzkrieg.networking.port_allocation import find_available_port

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

    pgadmin_run_command = (
        f"docker run -d --name {project_name}-pgadmin -p {pgadmin_port}:80 "
        f"-e 'PGADMIN_DEFAULT_EMAIL=admin@example.com' "
        f"-e 'PGADMIN_DEFAULT_PASSWORD=0101' "
        f"--network {network_name} "
        "-v $(pwd)/servers.json:/pgadmin4/servers.json "
        "dpage/pgadmin4"
    )
    run_command(pgadmin_run_command)
