import argparse
from blitzkrieg.cli.asciimatics_utils import AsciimaticsManager
from blitzkrieg.core.managers.postgres_manager import PostgreSQLManager
from asciimatics.screen import Screen
import asyncio

def run():
    parser = argparse.ArgumentParser(description="Blitzkrieg CLI")
    parser.add_argument("command", choices=["init", "stop"], help="Command to run")

    args = parser.parse_args()

    postgres_manager = PostgreSQLManager()

    if args.command == "init":
        project_name = input("Enter a project name:")

        asyncio.run(postgres_manager.initialize_with_persistence_check(project_name=project_name, init_mode=True, container_name=f"{project_name}-postgres"))
    elif args.command == "stop":
        asyncio.run(postgres_manager.stop_containers_async())

if __name__ == "__main__":
    run()
