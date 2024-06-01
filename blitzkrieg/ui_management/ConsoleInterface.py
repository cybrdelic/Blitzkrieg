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
    handlers=[RichHandler(rich_tracebacks=True)]
)

class CustomSpinner:
    def __init__(self, text='Loading...', spinner_chars=None, interval=0.1):
        self.text = text
        self.spinner_chars = spinner_chars if spinner_chars else ['-', '\\', '|', '/']
        self.interval = interval
        self.stop_running = threading.Event()
        self.thread = threading.Thread(target=self._spin)
        self.lock = threading.Lock()

    def start(self):
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self._spin)
            self.thread.start()

    def stop(self):
        self.stop_running.set()
        self.thread.join()
        self._clear_line()

    def succeed(self, message):
        self.stop()
        self._animate_message(message, "✔", "green")

    def fail(self, message):
        self.stop()
        self._animate_message(message, "✖", "red")

    def info(self, message):
        self.stop()
        self._animate_message(message, "ℹ", "cyan")

    def _spin(self):
        self.stop_running.clear()
        for char in itertools.cycle(self.spinner_chars):
            if self.stop_running.is_set():
                break
            with self.lock:
                sys.stdout.write(f'\r{colored(char, "cyan")} {self.text}')
                sys.stdout.flush()
            time.sleep(self.interval)

    def _clear_line(self):
        sys.stdout.write('\r' + ' ' * (len(self.text) + 3) + '\r')
        sys.stdout.flush()

    def _animate_message(self, message, symbol, color):
        sys.stdout.write(colored(f"\r{symbol} {message}\n", color))
        sys.stdout.flush()

class ConsoleInterface:
    def __init__(self):
        self.console = Console()
        self.spinner = CustomSpinner(text='Initializing...')
        self.processes = []
        self.current_task = None
    def create_process(self, process_name):
        process = {'name': process_name, 'groups': []}
        self.processes.append(process)
        return process

    def create_group(self, process, title):
        group = {'title': title, 'tasks': []}
        process['groups'].append(group)
        return group

    def add_task(self, group, name, func, **kwargs):
        task = {
            'name': name,
            'func': func,
            'args': kwargs,
            'messages': [],
            'status': 'pending'
        }
        group['tasks'].append(task)
        return task

    def handle_success(self, message):
        self.spinner.succeed(message)

    def handle_error(self, message):
        self.spinner.fail(message)

    def handle_info(self, message):
        self.spinner.info(message)

    def handle_wait(self, message):
        self.spinner.text = message


    def log(self, message):
        logging.info(message)

    def run_process(self, process):
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
            self.handle_success(f"{task['name']} completed successfully.")
        except Exception as e:
            self.handle_error(f"{task['name']} failed: {str(e)}")
        finally:
            self.current_task.status = 'completed'
            self.current_task = None
            self.spinner.stop()

    def display_banner(self, text):
        banner_panel = Panel(Text(text, style="bold magenta"), border_style="magenta", expand=False)
        self.console.print("\n")
        self.console.print(banner_panel)

    def display_subgroup(self, text):
        self.console.print(Text(text, style="bold blue"))
