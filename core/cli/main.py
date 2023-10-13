import argparse

from rundbfast.shared.utils import wait_for_container
from rundbfast.cli.user_input import get_project_name, get_postgres_password, get_persistence_choice, get_pgadmin_credentials
from rundbfast.managers.initializers import initialize_docker, initialize_postgresql, initialize_pgadmin
from rundbfast.cli.ui import (
    print_success,
    pause_for_user,
    print_label,
    print_cli_header,
    print_error,
    print_cli_footer
)
from rundbfast.managers.helpers.metadb_helper import execute_initial_user_setup

from rundbfast.core.managers.postgres_manager import PostgreSQLManager

def setup_meta(args):
    print_label(f"Setting up meta database for RunDBFast")
    docker = initialize_docker()
    postgres = PostgreSQLManager()
    postgres.setup_meta_database(docker)

def setup(args):
    project_name = get_project_name()
    print_label(f"Setting up for project: {project_name}")
    pause_for_user()
    docker = initialize_docker()
    postgres = PostgreSQLManager()
    postgres.initialize_with_persistence_check(project_name)
    initialize_pgadmin(project_name, postgres)
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
