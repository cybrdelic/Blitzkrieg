import asyncio
import logging
from pathlib import Path
from jinja2 import Template
from fuzzywuzzy import process
from pyfiglet import Figlet
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup console and ASCII Art for branding
console = Console()
f = Figlet(font='slant')
console.print(f.renderText('BLITZKRIEG'))

def logger_decorator(func):
    """Decorator for logging function execution."""
    async def wrapper(*args, **kwargs):
        logger.info(f"Entering {func.__name__}")
        result = await func(*args, **kwargs)
        logger.info(f"Exiting {func.__name__}")
        return result
    return wrapper

class PostgreSQLManager:

    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent / "templates"

    def handle_error(self, message: str):
        """Centralized error handling."""
        console.print("[bold red]Error: [/bold red][italic yellow]{}[/italic yellow]".format(message))

    def confirm_action(self, message: str) -> bool:
        """Get user confirmation."""
        return Prompt.ask(message, choices=["yes", "no"], default="no") == "yes"

    @logger_decorator
    async def _get_template_path(self, input_template_name):
        """Fetch the closest matching template path based on the input."""
        try:
            available_files = [f.name for f in self.template_dir.iterdir() if f.is_file()]
            best_match, score = process.extractOne(input_template_name, available_files)
            if score > 80:
                return self.template_dir / best_match
            else:
                self.handle_error(f"No close match found for: {input_template_name}")
                return None
        except Exception as e:
            self.handle_error(f"An exception occurred: {e}")
            return None

    @logger_decorator
    async def _generate_docker_compose_file(self, project_name, db_user, db_password, admin_email, admin_password):
        """Generate a Docker Compose file from a template."""
        with Progress() as progress:
            task1 = progress.add_task("[cyan]Generating Docker Compose File...", total=100)
            try:
                input_template_name = 'docker-compose-template.yml'
                template_path = await self._get_template_path(input_template_name)
                if template_path is None:
                    return None

                output_path = Path(f"docker-compose-{project_name}.yml")
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
                progress.update(task1, completed=100)
                console.print("[green]Docker compose file generated successfully![/green]")
                return output_path
            except Exception as e:
                self.handle_error(f"An exception occurred: {e}")
                return None

    @logger_decorator
    async def _run_command_async(self, cmd):
        """Run shell commands asynchronously."""    @logger_decorator
        try:
            with Progress() as progress:  # Using rich's Progress
                task = progress.add_task("[cyan]Executing...[/cyan]", total=100)
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                progress.update(task, completed=100)

            if process.returncode != 0:
                self.handle_error(f"Command failed with error: {stderr.decode()}")
                return None

            return stdout.decode().strip()
        except Exception as e:
            self.handle_error(f"An exception occurred: {e}")
            return None
            

    @logger_decorator
    async def start_containers_async(self, project_name: str, db_user: str, db_password: str, admin_email: str, admin_password: str):
        """Start Docker containers."""
        if self.confirm_action(f"Do you want to stop the containers for {project_name}?"):
            compose_file_path = await self._generate_docker_compose_file(project_name, db_user, db_password, admin_email, admin_password)
            if compose_file_path:
                cmd = f"docker-compose -f {compose_file_path} up -d"
                await self._run_command_async(cmd)
                logger.info("Containers started.")
            pass

    @logger_decorator
    async def stop_containers_async(self, project_name: str):
        """Stop Docker containers."""
        if self.confirm_action(f"Do you want to stop the containers for {project_name}?"):
            cmd = f"docker-compose -f docker-compose-{project_name}.yml down"
            await self._run_command_async(cmd)
            logger.info("Containers stopped.")
            pass

    @logger_decorator
    async def is_container_ready(self, container_name: str) -> bool:
        """Check if a Docker container is running."""
        cmd = f"docker inspect --format='{{json .State.Status}}' {container_name}"
        status = await self._run_command_async(cmd)
        return status == "running"
        pass

    @logger_decorator
    async def initialize_with_persistence_check(self, project_name: str, container_name: str, db_user: str = "admin", db_password: str = "admin", admin_email: str = "admin@admin.com", admin_password: str = "admin", init_mode: bool = False):
        """Initialize containers and handle persistence."""
        if self.confirm_action(f"Do you want to initialize the project {project_name}?"):
            try:
                full_container_name = f"{container_name}-{project_name}"
                if not await self.is_container_ready(full_container_name):
                    logger.info(f"Container {full_container_name} is not running. Starting containers.")
                    await self.start_containers_async(project_name, db_user, db_password, admin_email, admin_password)
            except Exception as e:
                self.handle_error(f"An error occurred during initialization: {e}")
            pass
