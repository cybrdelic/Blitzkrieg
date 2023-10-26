import argparse
from config import load_configurations
from cli.parsing.command_handler import CommandHandler
from core.shared.command_runner import CommandRunner


class ParserManager:
    def __init__(self, wake_word="blitz"):
        self.wake_word = wake_word
        self.parser = argparse.ArgumentParser(prog=self.wake_word, description=f"{self.wake_word} command-line tool.")
        self.subparsers = self.parser.add_subparsers()
        self.runner =CommandRunner()
        self.command_handler = CommandHandler(self.runner)

    def register_setup_command(self):
        parser_setup = self.subparsers.add_parser('setup', help='Setup databases.')
        parser_setup.add_argument('database', choices=['postgres'], help='The database to setup.')
        parser_setup.set_defaults(func=self.command_handler.setup)

    def register_setup_meta_command(self):
        parser_setup_meta = self.subparsers.add_parser('setup-meta', help="Setup RunDBFast meta database")
        parser_setup_meta.set_defaults(func=self.command_handler.setup_meta)


    def run(self):
        args = self.parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            print("No command provided. Use --help for usage information.")

def main():
    config = load_configurations()
    wake_word = config.get("WAKE_WORD", "db")
    parser_manager = ParserManager(wake_word=wake_word)
    parser_manager.register_setup_command()
    parser_manager.register_setup_meta_command()
    parser_manager.run()

if __name__ == "__main__":
    main()
