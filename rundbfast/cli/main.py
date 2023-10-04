import argparse

from ..shared.utils import wait_for_container
from .user_input import get_project_name, get_postgres_password, get_persistence_choice, get_pgadmin_credentials
from ..managers.initializers import initialize_docker, initialize_postgresql, initialize_pgadmin
from .ui import (
    print_success,
    pause_for_user,
    print_label,
    print_cli_header,
    print_error,
    print_cli_footer
)

def setup_meta(args):
    db_name = 'meta'
    print_label(f"Setting up meta database for RunDBFast")

    docker = initialize_docker()
    postgres, pg_password = initialize_postgresql(docker, db_name)
    postgres.ensure_data_persistence(pg_password)
    postgres.start_container(pg_password)

    # Wait for the PostgreSQL container to be running
    if wait_for_container(docker, f"{db_name}-postgres"):
        print_success(f"RunDbFast PostgreSQL database is now running with data persistence enabled.")
    else:
        print_error("Failed to start the PostgreSQL database.")

    pgadmin, pgadmin_email = initialize_pgadmin(db_name)
    pgadmin.add_server('RunDBFast Meta Server', db_name, pg_password, pgadmin_email)


def setup(args):
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

    parser_setup_meta_db = subparsers.add_parser('setup-meta', help="Setup RunDBFast meta database")
    parser_setup_meta_db.set_defaults(func=setup_meta)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
