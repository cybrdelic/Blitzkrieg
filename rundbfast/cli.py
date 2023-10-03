import argparse
from .manager import CommandRunner, DockerManager, PostgreSQLManager, PgAdminManager
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import questionary

console = Console()

def setup(args):
    if args.database == 'postgres':
        welcome_message = Panel.fit("Welcome to RunDBFast!", style="bold blue")
        console.print(welcome_message)

        docker = DockerManager()
        if not docker.is_installed():
            with Progress() as progress:
                task = progress.add_task("[cyan]Installing Docker...", total=100)
                docker.install()
                while not progress.finished:
                    progress.update(task, advance=20)
                    time.sleep(0.5)
            console.print("Docker installed successfully!", style="bold green")
        else:
            console.print("Docker is already installed.", style="bold blue")

        console.print("Pulling PostgreSQL image...", style="bold yellow")
        docker.pull_image("postgres:latest")

        pg_password = questionary.password("Enter a secure password for PostgreSQL:").ask()

        container_name = "synthextra-postgres"
        if docker.container_exists(container_name):
            console.print(f"Container with name {container_name} already exists. Stopping and removing...", style="bold yellow")
            docker.remove_container(container_name)

        postgres = PostgreSQLManager(container_name)
        console.print(f"Starting container {container_name}...", style="bold yellow")
        postgres.start_container(pg_password)
        console.print("Waiting for PostgreSQL to be ready...", style="bold yellow")
        postgres.wait_for_ready()
        postgres.setup_database()

        persist_data = questionary.select("Do you want to ensure data persistence across container restarts?", choices=["Yes", "No"]).ask()
        if persist_data == 'Yes':
            postgres.ensure_data_persistence(pg_password)

        console.print("Setup completed! PostgreSQL is running with the Cube extension installed.", style="bold green")

        pgadmin_email = questionary.text("Enter an email for pgAdmin:").ask()
        pgadmin_password = questionary.password("Enter a password for pgAdmin:").ask()

        pgadmin = PgAdminManager()
        if pgadmin.container_exists():
            console.print("pgAdmin container already exists. Stopping and removing...", style="bold yellow")
            pgadmin.remove_container()

        console.print("Starting pgAdmin container...", style="bold yellow")
        pgadmin.start_container(pgadmin_email, pgadmin_password)

        console.print(f"pgAdmin is now running. Access it at http://localhost using the email and password provided.", style="bold green")
        console.print(Panel.fit("Thank you for using our setup tool! See you next time!", style="bold blue"))

def main():
    parser = argparse.ArgumentParser(description='RunDBFast command-line tool.')
    subparsers = parser.add_subparsers()

    # 'setup' command
    parser_setup = subparsers.add_parser('setup', help='Setup databases.')
    parser_setup.add_argument('database', choices=['postgres'], help='The database to setup.')
    parser_setup.set_defaults(func=setup)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
