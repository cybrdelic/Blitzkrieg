import asyncio
import logging
from jinja2 import Template
from rich.console import Console
import os
from fuzzywuzzy import process

logger = logging.getLogger(__name__)

class PostgreSQLManager:

    @staticmethod
    def handle_error(message):
        console = Console()
        console.print("[bold red]Error: [/bold red][italic yellow]{}[/italic yellow]".format(message))

    async def _generate_docker_compose_file(self, project_name, db_user, db_password, admin_email, admin_password):
        try:
            input_template_path = 'templates/docker-compose-template.yml'  # Replace with your input or wrong path
            directory, filename = os.path.split(input_template_path)

            # If directory is empty, it means we are looking in the current directory
            if not directory:
                directory = '.'

            # List all files in the given directory
            available_files = os.listdir(directory)

            # Perform fuzzy search to find the closest matching file
            best_match, score = process.extractOne(filename, available_files)

            # You can set a threshold score to consider it a good match
            if score > 80:
                template_path = os.path.join(directory, best_match)
            else:
                self.handle_error(f"No close match found for: {input_template_path}")
                return None

            output_path = f'docker-compose-{project_name}.yml'  # Replace with your actual path

            with open(template_path, 'r') as f:
                template = Template(f.read())

            rendered = template.render(
                PROJECT_NAME=project_name,
                POSTGRES_USER=db_user,
                POSTGRES_PASSWORD=db_password,
                POSTGRES_DB=project_name,
                PGADMIN_EMAIL=admin_email,
                PGADMIN_PASSWORD=admin_password
            )

            with open(output_path, 'w') as f:
                f.write(rendered)

            return output_path
        except FileNotFoundError:
            self.handle_error(f"File not found: {template_path}")
            return None
        except Exception as e:
            self.handle_error(f"An exception occurred: {e}")
            return None
    async def _run_command_async(self, cmd):
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                self.handle_error(f"Command failed with error: {stderr.decode()}")
                return None

            return stdout.decode().strip()
        except Exception as e:
            self.handle_error(f"An exception occurred: {e}")
            return None

    async def start_containers_async(self, project_name, db_user, db_password, admin_email, admin_password):
        compose_file_path = await self._generate_docker_compose_file(project_name, db_user, db_password, admin_email, admin_password)
        if compose_file_path:
            cmd = f"docker-compose -f {compose_file_path} up -d"
            await self._run_command_async(cmd)
            logger.info("Containers started.")

    async def stop_containers_async(self, project_name):
        cmd = f"docker-compose -f docker-compose-{project_name}.yml down"  # Replace with your actual path
        await self._run_command_async(cmd)
        logger.info("Containers stopped.")

    async def is_container_ready(self, container_name):
        cmd = f"docker inspect --format='{{json .State.Status}}' {container_name}"
        status = await self._run_command_async(cmd)
        return status == "running"

    async def initialize_database(self, db_name, user, password, container_name):
    # Check if the container exists
        check_cmd = f"docker ps -a -q --filter name=^/{container_name}$"
        existing_containers = await self._run_command_async(check_cmd)

        # If the container doesn't exist, create it
        if not existing_containers:
            create_cmd = f"docker run --name {container_name} -e POSTGRES_USER={user} -e POSTGRES_PASSWORD={password} -d postgres"
            await self._run_command_async(create_cmd)
            logger.info(f"Container {container_name} created.")

        # Initialize the database
        cmd = f"docker exec {container_name} psql -U {user} -c 'CREATE DATABASE {db_name};'"
        await self._run_command_async(cmd)

        # Alter the user with the encrypted password
        cmd = f"docker exec {container_name} psql -U {user} -d {db_name} -c \"ALTER USER {user} WITH ENCRYPTED PASSWORD '{password}';\""
        await self._run_command_async(cmd)
        logger.info(f"Database {db_name} initialized.")

    async def initialize_with_persistence_check(self, project_name: str, container_name: str, db_user: str = "admin", db_password: str = "admin", admin_email: str = "admin@admin.com", admin_password: str = "admin", init_mode: bool = False) -> None:
        try:
            full_container_name = f"{container_name}-{project_name}"

            if not await self.is_container_ready(full_container_name):
                logger.info(f"Container {full_container_name} is not running. Starting containers.")
                await self.start_containers_async(project_name, db_user, db_password, admin_email, admin_password)

            await self.initialize_database(project_name, db_user, db_password, container_name)

            if init_mode:
                await self.initialize_database("meta_db", db_user, db_password, container_name)
        except Exception as e:
            self.handle_error(f"An error occurred during initialization: {e}")
