import argparse
import asyncio
from asciimatics.screen import Screen

from blitzkrieg.core.managers.postgres.postgres_manager import initialize_with_persistence_check, stop_containers_async
from blitzkrieg.core.shared.utils.config import generate_project_config, ProjectConfig

def run():
    parser = argparse.ArgumentParser(description="Blitzkrieg CLI")
    parser.add_argument("command", choices=["init", "stop"], help="Command to run")

    args = parser.parse_args()

    if args.command == "init":
        project_config: ProjectConfig = generate_project_config()
        asyncio.run(initialize_with_persistence_check(
            project_config=project_config
        ))
    elif args.command == "stop":
        asyncio.run(stop_containers_async())

if __name__ == "__main__":
    run()
