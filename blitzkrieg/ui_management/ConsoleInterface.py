import itertools
import sys
import threading
import time
import logging
from typing import Any, Dict, List, Callable
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from termcolor import colored
import shutil

# Setup structured and colored logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(level=logging.INFO)]
)

class CustomSpinner:
    def __init__(self, text='Loading...', spinner_chars=None, interval=0.1, glare_interval=0.05):
        self.text = text
        self.spinner_chars = spinner_chars if spinner_chars else [
            "⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓",
            "⠙⠚⠞⠖⠦⠴⠲⠳⠓⠋",
            "⠚⠞⠖⠦⠴⠲⠳⠓⠋⠙",
            "⠞⠖⠦⠴⠲⠳⠓⠋⠙⠚",
            "⠖⠦⠴⠲⠳⠓⠋⠙⠚⠞",
            "⠦⠴⠲⠳⠓⠋⠙⠚⠞⠖",
            "⠴⠲⠳⠓⠋⠙⠚⠞⠖⠦",
            "⠲⠳⠓⠋⠙⠚⠞⠖⠦⠴",
            "⠳⠓⠋⠙⠚⠞⠖⠦⠴⠲",
            "⠓⠋⠙⠚⠞⠖⠦⠴⠲⠳",
        ]
        self.interval = interval  # Interval for spinner animation
        self.glare_interval = glare_interval  # Interval for glare animation
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
        self._animate_message(message, "ℹ", "grey")

    def _spin(self):
        self.stop_running.clear()
        frame_iter = itertools.cycle(self.spinner_chars)
        glare_index = 0
        glare_length = len(self.text)
        color_pattern = ['grey'] * glare_length

        while not self.stop_running.is_set():
            with self.lock:
                for i in range(glare_length):
                    if i == glare_index % glare_length:
                        color_pattern[i] = 'white'
                    else:
                        color_pattern[i] = 'grey'

                styled_text = ''.join(colored(char, color) for char, color in zip(self.text, color_pattern))
                sys.stdout.writelines([
                    f"\r{colored(next(frame_iter), 'blue')} ",
                    f"{styled_text}"
                ])
                sys.stdout.flush()

                glare_index += 1
                if glare_index >= glare_length:
                    glare_index = 0

            time.sleep(self.interval)  # Spinner interval
            time.sleep(self.glare_interval)  # Glare interval

    def _clear_line(self):
        columns = shutil.get_terminal_size().columns
        sys.stdout.write('\r' + ' ' * columns + '\r')
        sys.stdout.flush()

    def _animate_message(self, message, symbol, color):
        sys.stdout.write(colored(f"     {symbol} {message}\n", color))
        sys.stdout.flush()

class ConsoleInterface:
    def __init__(self):
        self.console = Console()
        self.spinner = CustomSpinner(text='Initializing...', interval=0.1, glare_interval=0.02)  # Adjust glare_interval here
        self.processes: List[Dict[str, Any]] = []
        self.current_group = None

    def create_process(self, process_name: str) -> Dict[str, Any]:
        process = {'name': process_name, 'groups': []}
        self.processes.append(process)
        return process

    def create_group(self, process: Dict[str, Any], title: str) -> Dict[str, Any]:
        group = {'title': title, 'tasks': [], 'status': 'pending'}
        process['groups'].append(group)
        return group

    def add_task(self, group: Dict[str, Any], name: str, func: Callable, **kwargs) -> Dict[str, Any]:
        task = {
            'name': name,
            'func': func,
            'args': kwargs,
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

    def run_process(self, process: Dict[str, Any]):
        for group in process['groups']:
            self.current_group = group
            self.display_banner(group['title'])
            for task in group['tasks']:
                self.run_task(task)
        self.current_group['status'] = 'completed'

    def run_task(self, task: Dict[str, Any]):
        self.spinner.text = task['name']
        self.spinner.start()
        try:
            result = task['func'](**task['args'])
            self.handle_success(f"{task['name']} completed successfully.")
        except Exception as e:
            self.handle_error(f"{task['name']} failed: {str(e)}")
        finally:
            task['status'] = 'completed'
            self.spinner.stop()

    def display_banner(self, text):
        banner_panel = Panel(Text(text, style="bold magenta"), border_style="magenta", expand=False)
        self.console.print("\n")
        self.console.print(banner_panel)

    def display_subgroup(self, text):
        self.console.print(Text(text, style="bold blue"))
