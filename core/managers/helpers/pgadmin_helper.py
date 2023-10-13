from ...cli.ui import print_success, print_error, show_choices, print_warning
import subprocess
import os

NETWORK_NAME = "pgadmin_postgres_network"

def add_server(self, server_name, db_name, password, pgadmin_email, port):
    """
    Adds a server configuration to the PgAdmin container.
    """
    # Ensure the PostgreSQL configuration allows external connections
    _setup_postgres_config(self, db_name)

    # Ensure both containers are on the same network
    _ensure_network_setup(self, db_name)

    if not _should_add_server(self):
        return

    server_config = self._generate_server_config(server_name, db_name, password, port)
    temp_file_path = _create_temp_file(self,server_config)

    # Set the file permissions
    os.chmod(temp_file_path, 0o644)

    try:
        _transfer_config_to_container(self, temp_file_path)
        _setup_server_in_container(self, pgadmin_email, server_name, temp_file_path)
    finally:
        _cleanup_temp_file(self, temp_file_path)


def _ensure_network_setup(self, db_name):
    """
    Ensures both PgAdmin and PostgreSQL containers are on the same network.
    """
    # Check if the network exists
    network_exists_cmd = f"docker network ls --filter name={NETWORK_NAME} -q"
    network_exists = self.runner.run_command(network_exists_cmd)
    if not network_exists:
        # Create the network
        self.runner.run_command(f"docker network create {NETWORK_NAME}")

    # Connect PostgreSQL container to the network
    self.runner.run_command(f"docker network connect {NETWORK_NAME} {db_name}-postgres")

    # Connect PgAdmin container to the network
    self.runner.run_command(f"docker network connect {NETWORK_NAME} {self.container_name}")


def _setup_postgres_config(self, db_name):
    """
    Set up PostgreSQL to allow external connections and create the required database.
    """
    # Append to the pg_hba.conf file
    config_cmd = 'echo "host    all             all             0.0.0.0/0               trust" >> /var/lib/postgresql/data/pg_hba.conf'
    self.runner.run_command(f"docker exec {db_name}-postgres bash -c '{config_cmd}'")

    # Reload PostgreSQL configuration
    self.runner.run_command(f"docker exec -u postgres {db_name}-postgres pg_ctl reload")

    # Create the 'meta' database if it doesn't exist
    create_db_cmd = f"psql -U postgres -tc \"SELECT 1 FROM pg_database WHERE datname='{db_name}'\" | grep -q 1 || psql -U postgres -c \"CREATE DATABASE {db_name};\""
    self.runner.run_command(f"docker exec {db_name}-postgres bash -c '{create_db_cmd}'")


def _should_add_server(self):
    """
    Determines if we should proceed with adding the server based on user input and existing configurations.
    Returns True if we should add the server, otherwise False.
    """
    if not self._servers_config_exists():
        return True

    choice = show_choices("servers.json already exists in the container. Overwrite?", ["Yes", "No"])
    if choice == "No":
        print_warning("Server addition aborted by user.")
        return False
    return True


def _create_temp_file(self, server_config):
    """
    Creates a temporary file for the server configuration.
    Returns the path to the temporary file.
    """
    return self._write_server_config_to_temp_file(server_config)


def _transfer_config_to_container(self, temp_file_path):
    """
    Transfers the server configuration from the temporary file to the container.
    """
    try:
        self._execute_transfer_command(temp_file_path)
    except FileNotFoundError:
        print_error(f"File {temp_file_path} not found.")
        raise


def _setup_server_in_container(self, pgadmin_email, server_name, temp_file_path):
    """
    Sets up the server in the PgAdmin container.
    """
    try:
        self._execute_add_server_command(temp_file_path, pgadmin_email)
        print_success(f"Server '{server_name}' added to pgAdmin successfully!")
    except subprocess.CalledProcessError as cpe:
        print_error(f"Command execution failed: {str(cpe)}")
        raise


def _cleanup_temp_file(self, temp_file_path):
    """
    Cleans up the temporary file used for the server configuration.
    """
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
