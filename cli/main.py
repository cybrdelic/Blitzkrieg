from rundbfast.cli.parsing.parser_manager import ParserManager
from rundbfast.config import load_configurations


def main():
    config = load_configurations()
    wake_word = config.get("WAKE_WORD", "RunDBFast")
    parser_manager = ParserManager(wake_word=wake_word)
    parser_manager.register_setup_command()
    parser_manager.register_setup_meta_command()
    parser_manager.run()

if __name__ == "__main__":
    main()
