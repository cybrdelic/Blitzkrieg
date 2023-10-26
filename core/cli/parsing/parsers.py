import argparse

from Blitzkrieg import setup
from Blitzkrieg.core.cli.main import setup_meta
def handle_parsing():
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
