from blitzkrieg.core.networking.port_allocation import find_available_port
import json

from blitzkrieg.core.shared.run_command import run_command

class BlitzkriegDbManager:
    def __init__(self):
        self.project_name = "blitzkrieg"  # Hardcoded project name
        self.db_user = 'blizkrieg-db-user'
        self.db_password = '0101'
        self.db_port = find_available_port(5432)
        self.network_name = f"{self.project_name}-network"
        self.container_name = f"{self.project_name}-postgres"
        self.image_name = "postgres:latest"

    def initialize(self):
        self.run_postgres_container()
        return self.db_port

    def teardown(self):
        self.remove_postgres_container()
        self.remove_docker_network()
        self.remove_pgadmin_server_json()

    def save_config(self):
        with open(self.config_path, 'w') as file:
            json.dump(self.servers, file, indent=4)


    def run_postgres_container(self):
        env_vars = {
            "POSTGRES_DB": self.project_name,
            "POSTGRES_USER": self.db_user,
            "POSTGRES_PASSWORD": self.db_password
        }
        env_options = " ".join([f"-e {k}={v}" for k, v in env_vars.items()])
        command = (
            f"docker run -d --name {self.container_name} {env_options} "
            f"--network {self.network_name} -p {self.db_port}:5432 {self.image_name}"
        )
        run_command(command)

    def setup_pgadmin_server_json(self):
        server_json = {
            "Servers": {
                "1": {
                    "Name": "PostgreSQL",
                    "Group": "Servers",
                    "Host": self.container_name,
                    "Port": 5432,
                    "MaintenanceDB": self.project_name,
                    "Username": self.db_user,
                    "SSLMode": "prefer",
                    "PassFile": "/var/lib/pgadmin/pgpassfile"
                }
            }
        }
        with open('servers.json', 'w') as f:
            json.dump(server_json, f)

    def remove_postgres_container(self):
        command = f"docker stop {self.container_name} && docker rm {self.container_name}"
        run_command(command)

    def remove_docker_network(self):
        command = f"docker network rm {self.network_name}"
        run_command(command)

    def remove_pgadmin_server_json(self):
        run_command("rm servers.json")
