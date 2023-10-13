import asyncio
from rundbfast.cli.ui import print_warning

class LifeCycleManagement:
    def __init__(self, runner, container_name):
        self.runner = runner
        self.container_name = container_name

    async def start_container_async(self, start_command):
        if await self.container_exists_async():
            await self.remove_container_async()
        await self.runner.run_command_async(start_command)

    async def stop_container_async(self):
        if await self.container_exists_async():
            await self.runner.run_command_async(f"docker stop {self.container_name}")

    async def remove_container_async(self):
        if await self.container_exists_async():
            print_warning(f"Container with name {self.container_name} already exists. Removing...")
            await self.runner.run_command_async(f"docker rm -f {self.container_name}")

    async def container_exists_async(self):
        existing_containers = await self.runner.run_command_async(f"docker ps -a -q -f name={self.container_name}")
        return bool(existing_containers)

    async def is_container_running_async(self):
        output = await self.runner.run_command_async(f"docker inspect -f '{{.State.Running}}' {self.container_name}")
        return output.strip() == 'true'
