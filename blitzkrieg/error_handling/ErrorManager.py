import traceback
import logging
from emoji import emojize
from halo import Halo
import time
from rich.console import Console

# Ensure logging directory and file exist
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class ErrorManager:
    def __init__(self, console_manager):
        self.console_manager = console_manager
        self.console = Console()

    def display_error(self, message, exception=None, emoji=':warning:', spinner=False, category='General'):
        error_message = self.format_message(message, emoji, 'red')
        self.log_error(error_message, exception, category)

        if spinner:
            with Halo(text=error_message, spinner='dots', color='red'):
                time.sleep(2)  # Duration of the spinner
        else:
            self.console.log(error_message)

        if exception:
            self.console.log(f"[bold red]Stack Trace:[/bold red] {traceback.format_exc()}", highlight=False)

    def display_warning(self, message, emoji=':warning:'):
        warning_message = self.format_message(message, emoji, 'yellow')
        self.console.log(warning_message)

    def display_info(self, message, emoji=':information:'):
        info_message = self.format_message(message, emoji, 'cyan')
        self.console.log(info_message)

    def display_success(self, message, emoji=':check_mark:'):
        success_message = self.format_message(message, emoji, 'green')
        self.console.log(success_message)

    def format_message(self, message, emoji, color):
        return f"{emojize(emoji)} [bold {color}]{message}[/bold {color}]"

    def log_error(self, message, exception, category):
        logging.error(f'Category: {category} - Message: {message}')
        if exception:
            logging.error(f'Exception: {exception} - Traceback: {traceback.format_exc()}')
