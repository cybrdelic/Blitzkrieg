import json
import os
import subprocess
from docker import APIClient
from docker.errors import APIError

class DockerComposeManager:
    def __init__(self, directory):
        self.directory = directory
        self.compose_file = os.path.join(self.directory, 'docker-compose.yml')
        self.client = APIClient(base_url='unix://var/run/docker.sock')

    def create_compose_file(self):
        compose_content = {
            'version': '3.8',
            'services': {
                'postgres': {
                    'image': 'postgres:latest',
                    'environment': {
                        'POSTGRES_DB': 'blitzkrieg',
                        'POSTGRES_USER': 'blitzkrieg-db-user',
                        'POSTGRES_PASSWORD': '0101'
                    },
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data'
                    ],
                    'networks': ['blitzkrieg-net']
                },
                'pgadmin': {
                    'image': 'dpage/pgadmin4',
                    'environment': {
                        'PGADMIN_DEFAULT_EMAIL': 'admin@example.com',
                        'PGADMIN_DEFAULT_PASSWORD': 'admin'
                    },
                    'depends_on': ['postgres'],
                    'volumes': [
                        'pgadmin_data:/var/lib/pgadmin',
                        './servers.json:/pgadmin4/servers.json'
                    ],
                    'networks': ['blitzkrieg-net'],
                    'ports': ['5050:80']
                }
            },
            'volumes': {
                'postgres_data': None,
                'pgadmin_data': None
            },
            'networks': {
                'blitzkrieg-net': None
            }
        }
        with open(self.compose_file, 'w') as file:
            json.dump(compose_content, file, indent=4)

    def deploy_services(self):
        self.configure_pgadmin()
        os.chdir(self.directory)
        subprocess.run(['docker-compose', 'up', '-d'], check=True)

    def configure_pgadmin(self):
        # Create servers.json in the current directory
        servers_config = {
            "Servers": {
                "1": {
                    "Name": "Blitzkrieg PostgreSQL",
                    "Host": "postgres",
                    "Group": "Servers",
                    "Port": 5432,
                    "MaintenanceDB": "blitzkrieg",
                    "Username": "blitzkrieg-db-user",
                    "SSLMode": "prefer",
                    "PassFile": "/pgadmin4/.pgpass"
                }
            }
        }
        with open('servers.json', 'w') as file:
            json.dump(servers_config, file, indent=4)

    def down_services(self):
        os.chdir(self.directory)
        subprocess.run(['docker-compose', 'down'], check=True)
