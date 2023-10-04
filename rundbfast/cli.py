import argparse
from .flow.user_input import get_project_name, get_postgres_password, get_persistence_choice, get_pgadmin_credentials
from .flow.initializers import initialize_docker, initialize_postgresql, initialize_pgadmin
from .flow.ui import (
    print_success,
    pause_for_user,
    print_label,
    print_cli_header,
    print_cli_footer
)

def setup(args):
    # Print a welcome header
    print_cli_header()

    # Get project name
    project_name = get_project_name()
    print_label(f"Setting up for project: {project_name}")
    pause_for_user()

    # Initialize Docker
    docker = initialize_docker()

    postgres, pg_password = initialize_postgresql(docker, project_name)

    # Check for data persistence
    persist_data = get_persistence_choice()
    if persist_data == 'Yes':
        print_label("Ensuring data persistence...")
        postgres.ensure_data_persistence(pg_password)
        postgres.start_container(pg_password)
        print_success(f"PostgreSQL is now running with data persistence enabled.")

    initialize_pgadmin(project_name)

    print_cli_footer()

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
