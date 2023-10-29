from blitzkrieg.cli.logging_config import apply_logger_to_all_functions, setup_logging
from blitzkrieg.cli.parsing.parser_manager import run

backend_logger, ui_logger, console = setup_logging()
apply_logger_to_all_functions(backend_logger)

def main():
    run()

if __name__ == "__main__":
    main()
