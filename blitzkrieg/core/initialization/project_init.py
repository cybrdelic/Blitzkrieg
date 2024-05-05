import json
import time
from blitzkrieg.core.initialization.docker_manager import DockerManager
from blitzkrieg.core.initialization.pgadmin_manager import PgAdminManager
from blitzkrieg.core.initialization.postgres_manager import BlitzkriegDbManager
from blitzkrieg.core.networking.port_allocation import find_available_port
import requests
from blitzkrieg.core.initialization.print_connection_details import print_connection_details
from blitzkrieg.core.shared.run_command import run_command
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from .load_config import load_config

def create_pgadmin_server_json():
    server_json = {
        "Servers": {
            "1": {
            "Name": "PostgreSQL",
            "Group": "Servers",
            "Host": f"blitzkrieg-postgres",
            "Port": 5432,
            "MaintenanceDB": "blitzkrieg",
            "Username": f"blitzkrieg-db-user",
            "SSLMode": "prefer",
            "PassFile": "/var/lib/pgadmin/pgpassfile"
            }
        }
    }

    with open('servers.json', 'w') as f:
        json.dump(server_json, f)

def run_blitzkrieg_postgres_container(config):
    network_name = f"blitzkrieg-network"
    container_name = f"blitzkrieg-postgres"
    db = config['db']
    postgres_db = f"POSTGRES_DB={db}"
    user = config['user']
    postgres_user = f"POSTGRES_USER={user}"
    postgres_password = f"POSTGRES_PASSWORD={config['password']}"

    postgres_run_command = (
        f"docker run -d --name {container_name} -e {postgres_db} "
        f"-e {postgres_user} -e {postgres_password} "
        f"--network {network_name} -p {config['postgres_port']}:5432 postgres:latest"
    )
    run_command(postgres_run_command)

def run_pgadmin_container(config):
    pgadmin_run_command = (
        f"docker run -d --name blitzkrieg-pgadmin -p {config['pgadmin_port']}:80 "
        f"-e 'PGADMIN_DEFAULT_EMAIL=admin@example.com' "
        f"-e 'PGADMIN_DEFAULT_PASSWORD=0101' "
        f"--network blitzkrieg-network "
        "-v $(pwd)/servers.json:/pgadmin4/servers.json "
        "dpage/pgadmin4"
    )
    run_command(pgadmin_run_command)

def wait_for_pgadmin_to_start(pgadmin_port):
    print(f"Waiting for pgAdmin to start on port {pgadmin_port}...")
    while True:
        try:
            response = requests.get(f'http://localhost:{pgadmin_port}/')
            print(f"Received status code {response.status_code} from pgAdmin.")
            if response.status_code == 200:
                print("pgAdmin started successfully.")
                break
            else:
                print(f"Unexpected status code from pgAdmin: {response.status_code}")
        except requests.exceptions.ConnectionError:
            time.sleep(0.3)  # Adjust time as needed
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

def create_pgpass_file(config):
    host = config['host']
    db = config['db']
    user = config['user']
    password = config['password']

    pgpass_content = f"{host}:5432:{db}:{user}:{password}"

    run_command(f"docker exec -i blitzkrieg-pgadmin sh -c 'echo \"{pgpass_content}\" > /var/lib/pgadmin/pgpassfile'")

def print_initialization_complete_message(config):
    print_connection_details(config)
    print(f"pgAdmin setup complete. Access it at http://localhost:{config['pgadmin_port']}")

def setup_pgadmin(config):
    create_pgadmin_server_json()
    run_pgadmin_container(config)
    wait_for_pgadmin_to_start(config['pgadmin_port'])
    create_pgpass_file(config)
    print_initialization_complete_message(config)

def initialize_blitzkrieg():
    docker_manager = DockerManager()
    docker_manager.create_docker_network("blitzkrieg-network")
    postgres_port = BlitzkriegDbManager().initialize()
    PgAdminManager(postgres_port=postgres_port).setup_pgadmin()
