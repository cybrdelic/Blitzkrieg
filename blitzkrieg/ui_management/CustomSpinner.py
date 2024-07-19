import logging
import time
import sys
import threading
import itertools
from termcolor import colored
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler

# Setup structured and colored logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

class CustomSpinner:
    def __init__(self, text='Loading...', spinner_chars='|/-\\', interval=0.1):
        self.text = text
        self.spinner_chars = itertools.cycle(spinner_chars)
        self.interval = interval
        self.stop_running = False
        self.thread = threading.Thread(target=self._spin)
        self.lock = threading.Lock()

    def start(self):
        self.stop_running = False
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self._spin)
            self.thread.start()

    def stop(self):
        self.stop_running = True
        self.thread.join()
        self._clear_line()

    def succeed(self, message):
        self.stop()
        self._print_with_animation(message, 'green')

    def fail(self, message):
        self.stop()
        self._print_with_animation(message, 'red')

    def info(self, message):
        self.stop()
        self._print_with_animation(message, 'cyan')

    def _spin(self):
        while not self.stop_running:
            with self.lock:
                spinner_char = next(self.spinner_chars)
                sys.stdout.write(f'\r{spinner_char} {self.text}')
                sys.stdout.flush()
            time.sleep(self.interval)

    def _clear_line(self):
        sys.stdout.write('\r' + ' ' * (len(self.text) + 3) + '\r')
        sys.stdout.flush()

    def _print_with_animation(self, message, color):
        colored_message = colored(message, color)
        for char in colored_message:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write('\n')

class ConsoleInterface:
    def __init__(self):
        self.rich_console = Console()
        self.spinner = CustomSpinner(text='Initializing...', spinner_chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
        self.processes = []
        self.current_task = None

    def create_workflow(self, process_name):
        process = {'name': process_name, 'groups': []}
        self.processes.append(process)
        return process

    def create_phase(self, process, title):
        group = {'title': title, 'tasks': []}
        process['groups'].append(group)
        return group

    def add_action(self, group, name, func, **kwargs):
        task = {
            'name': name,
            'func': func,
            'args': kwargs,
            'messages': []
        }
        group['tasks'].append(task)
        return task

    def handle_success(self, message):
        self.spinner.succeed(colored(f"{message}", 'green'))

    def handle_error(self, message):
        self.spinner.fail(colored(f"{message}", 'red'))

    def handle_info(self, message):
        self.spinner.info(colored(f"{message}", 'cyan'))

    def log(self, message):
        logging.info(message)
        print(message)

    def run_workflow(self, process):
        for group in process['groups']:
            self.display_banner(group['title'])
            for task in group['tasks']:
                self.display_subgroup(task['name'])
                self.run_task(task)

    def run_task(self, task):
        self.current_task = task
        self.spinner.text = task['name']
        self.spinner.start()
        try:
            result = task['func'](**task['args'])
            self.handle_success(f"Task '{task['name']}' completed successfully.")
        except Exception as e:
            self.handle_error(f"Task '{task['name']}' failed: {str(e)}")
        finally:
            self.spinner.stop()
            self.current_task = None

    def display_banner(self, text):
        colored_text = Text(text, style="bold magenta")
        banner_panel = Panel(colored_text, border_style="magenta", expand=False)
        self.rich_console.print("\n")
        self.rich_console.print(banner_panel)

    def display_subgroup(self, text):
        colored_text = colored(f"\n{text}\n", color="blue", attrs=['bold'])
        print(colored_text)

# Example usage:
