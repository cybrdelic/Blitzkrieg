import argparse
from .flow.user_input import get_project_name, get_postgres_password, get_persistence_choice, get_pgadmin_credentials
from .flow.initializers import initialize_docker, initialize_postgresql, initialize_pgadmin
from .flow.ui import print_message

def setup(args):
    # Get project name
    project_name = get_project_name()
    print_message(f"Welcome to RunDBFast, setting up for {project_name}!", style="bold blue")

    # Initialize Docker
    docker = initialize_docker()

    # Initialize PostgreSQL
    pg_password = get_postgres_password()
    postgres = initialize_postgresql(docker, project_name, pg_password)

    # Check for data persistence
    persist_data = get_persistence_choice()
    if persist_data == 'Yes':
        postgres.ensure_data_persistence(pg_password)
        postgres.start_container(pg_password)
        print_message(f"PostgreSQL is now running with data persistence enabled.", style="bold green")

    # Initialize pgAdmin
    pgadmin_email, pgadmin_password = get_pgadmin_credentials()
    pgadmin = initialize_pgadmin(project_name, email=pgadmin_email, password=pgadmin_password)
    pgadmin.start_container(pgadmin_email, pgadmin_password)
    print_message(f"pgAdmin is now running. Access it at http://localhost using the provided credentials.", style="bold green")

    print_message("Thank you for using our setup tool! See you next time!", style="bold blue")

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
