import asyncio
import logging
from typing import Optional, Tuple
from rundbfast.config import load_configurations
from rundbfast.core.cli.ui import print_success, print_warning
from rundbfast.core.managers.container_manager import ContainerManager
import time

# Load configurations
config = load_configurations()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load constants from config
TIMEOUT = int(config['TIMEOUT'])
SLEEP_INTERVAL = int(config['SLEEP_INTERVAL'])
WAIT_AFTER_CONTAINER_REMOVE = int(config["WAIT_AFTER_CONTAINER_REMOVE"])

class PostgreSQLManager(ContainerManager):
    def __init__(self, runner):
        super().__init__(runner)

    def start_container(self, password: str, volume_name: Optional[str] = None) -> int:
        port = self.find_available_port()
        volume_option = self.get_volume_option(volume_name)
        self.run_docker_command(password, volume_option, port)
        logger.info(f"Started PostgreSQL container on port {port}")
        self.sleep_after_start()
        return port

    def find_available_port(self) -> int:
        return self.runner.find_available_port(config.get("DEFAULT_PORT"))

    def get_volume_option(self, volume_name: Optional[str]) -> str:
        return f"-v {volume_name}:/var/lib/postgresql/data" if volume_name else ""

    def run_docker_command(self, password: str, volume_option: str, port: int):
        self.runner.run_command(f"docker run --name {self.container_name} -e POSTGRES_PASSWORD={password} {volume_option} -p {port}:{port} -d postgres:latest")

    def sleep_after_start(self):
        time.sleep(config.get("WAIT_AFTER_CONTAINER_START"))

    async def is_ready_async(self) -> bool:
        try:
            output = await self._run_command_async(f"docker exec {self.container_name} pg_isready")
            return "accepting connections" in output
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error while checking PostgreSQL readiness: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def wait_for_ready_async(self) -> bool:
        start_time = time.time()
        while True:
            if await self.is_ready_async():
                return True
            elif time.time() - start_time > TIMEOUT:
                raise TimeoutError("Timed out waiting for PostgreSQL to be ready")
            await asyncio.sleep(SLEEP_INTERVAL)

    async def setup_database_async(self, project_name: str):
        quoted_project_name = f"\"{project_name}\""
        if not await self.database_exists_async(project_name):
            await self._run_command_async(f"docker exec {self.container_name} psql -U postgres -c 'CREATE DATABASE {quoted_project_name};'")
        await self._run_command_async(f"docker exec {self.container_name} psql -U postgres -d {project_name} -c 'CREATE EXTENSION IF NOT EXISTS cube;'")

    async def database_exists_async(self, db_name: str) -> bool:
        result = await self._run_command_async(f"docker exec {self.container_name} psql -U postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='{db_name}'\"")
        return bool(result)

    async def initialize_async(self, db_name: str, password: str, volume_name: Optional[str] = None) -> int:
        if self.container_exists():
            await self.remove_container_async()
        port = await self.start_container_async(password, volume_name)
        return port

    async def start_with_check_async(self, db_name: str, password: str, volume_name: Optional[str] = None) -> int:
        port = await self.initialize_async(db_name, password, volume_name)
        if not await self.wait_for_ready_async():
            raise Exception("Failed to initialize PostgreSQL container.")
        print_success("PostgreSQL container initialized successfully!")
        return port

    async def remove_container_async(self):
        if self.container_exists():
            print_warning(f"Container with name {self.container_name} already exists. Removing...")
            await self._run_command_async(f"docker stop {self.container_name}")
            await self._run_command_async(f"docker rm {self.container_name}")
            await asyncio.sleep(WAIT_AFTER_CONTAINER_REMOVE)
