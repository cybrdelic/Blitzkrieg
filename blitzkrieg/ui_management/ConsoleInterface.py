import itertools
import json
import subprocess
import sys
import threading
import time
import logging
from typing import Any, Dict, List, Callable
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.syntax import Syntax
from termcolor import colored
import shutil
from rich.table import Table
import pyperclip
import io

# Setup structured and colored logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(level=logging.INFO)]
)

class CustomSpinner:
    def __init__(self, text='Loading...', spinner_chars=None, interval=0.1, glare_interval=0.05):
        self._text = text
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
        self.glare_length = self._calculate_glare_length()

    def _calculate_glare_length(self):
        return len(self._text) + len(self.spinner_chars[0])

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
        self._animate_message(message, "ℹ", "royal blue")

    def _spin(self):
        self.stop_running.clear()
        frame_iter = itertools.cycle(self.spinner_chars)
        glare_index = 0

        sys.stdout.write("\n")  # Add a newline here for initial space

        while not self.stop_running.is_set():
            with self.lock:
                self.glare_length = self._calculate_glare_length()
                color_pattern = ['grey'] * self.glare_length
                for i in range(self.glare_length):
                    if i == glare_index % self.glare_length:
                        color_pattern[i] = 'white'
                    else:
                        color_pattern[i] = 'grey'

                styled_text = ''.join(colored(char, color) for char, color in zip(self._text.ljust(self.glare_length), color_pattern))
                sys.stdout.write(
                    f"\r{colored(next(frame_iter), 'blue')} {styled_text}"
                )
                sys.stdout.flush()

                glare_index += 1
                if glare_index >= self.glare_length:
                    glare_index = 0

            time.sleep(self.interval)

    def _clear_line(self):
        columns = shutil.get_terminal_size().columns
        sys.stdout.write('\r' + ' ' * columns + '\r')
        sys.stdout.flush()

    def _animate_message(self, message, symbol, color):
        columns = shutil.get_terminal_size().columns
        sys.stdout.write('\r' + ' ' * columns + '\r')  # Clear the current line

        if color == "dark green":
            sys.stdout.write(f"\033[38;2;0;100;0m{symbol} {message}\033[0m\n")
        elif color == "royal blue":
            sys.stdout.write(f"\033[38;2;65;105;225m{symbol} {message}\033[0m\n")
        else:
            sys.stdout.write(colored(f"{symbol} {message}\n", color))

        sys.stdout.flush()


    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.glare_length = self._calculate_glare_length()

class ConsoleInterface:
    def __init__(self):
        self.console = Console()
        self.spinner = CustomSpinner(text='Initializing...', interval=0.1, glare_interval=0.0)  # Adjust glare_interval here
        self.workflowes: List[Dict[str, Any]] = []
        self.current_phase = None
        self.output_buffer = io.StringIO()  # Buffer to capture output

    def create_workflow(self, workflow_name: str) -> Dict[str, Any]:
        workflow = {'name': workflow_name, 'phases': []}
        self.workflowes.append(workflow)
        return workflow

    def create_phase(self, workflow: Dict[str, Any], title: str) -> Dict[str, Any]:
        phase = {'title': title, 'actions': [], 'status': 'pending'}
        workflow['phases'].append(phase)
        return phase

    def add_action(self, phase: Dict[str, Any], name: str, func: Callable, **kwargs) -> Dict[str, Any]:
        action = {
            'name': name,
            'func': func,
            'args': kwargs,
            'status': 'pending'
        }
        phase['actions'].append(action)
        return action

    def handle_success(self, message):
        self.spinner.succeed(message)
        self.output_buffer.write(f"✔ {message}\n")

    def handle_error(self, message, error_object=None):
        self.spinner.fail(message)
        self.output_buffer.write(f"✖ {message}\n")
        if error_object:
            error_details = json.dumps(error_object, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            error_syntax = Syntax(error_details, "json", theme="monokai", line_numbers=True)
            error_panel = Panel(
                error_syntax,
                title="Error Details",
                title_align="left",
                border_style="red",
                expand=False,
                box=box.DOUBLE,
            )
            self.console.print(error_panel)
        else:
            self.console.print(Panel(f"[bold red]{message}", border_style="red"))


    def handle_info(self, message):
        self.spinner.info(message)
        self.output_buffer.write(f"ℹ {message}\n")

    def handle_wait(self, message):
        self.spinner.stop()
        self.spinner.text = message
        self.spinner.start()
        self.output_buffer.write(f"... {message}\n")


    def display_file_content(self, file_path):
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()

        # Determine the file type based on the file extension
        file_extension = file_path.split('.')[-1]
        lexer = {
            'py': 'python',
            'json': 'json',
            'md': 'markdown',
            'sh': 'bash',
            'html': 'html',
            'css': 'css',
            'js': 'javascript'
        }.get(file_extension, 'text')

        # Create a Syntax object for syntax highlighting
        syntax = Syntax(content, lexer, theme='monokai', line_numbers=True)

        # Display the file content with syntax highlighting
        self.console.print(syntax)
        self.output_buffer.write(content + "\n")

    def log(self, message):
        logging.info(message)
        self.output_buffer.write(f"{message}\n")

    def run_workflow(self, workflow: Dict[str, Any]):
        for phase in workflow['phases']:
            self.current_phase = phase
            self.display_banner(phase['title'])
            for action in phase['actions']:
                self.run_action(action)
        self.current_phase['status'] = 'completed'
        self.copy_to_clipboard()

    def run_action(self, action: Dict[str, Any]):
        self.spinner.text = action['name']
        self.spinner.start()
        try:
            result = action['func'](**action['args'])
        except Exception as e:
            self.handle_error(f"An error has occurred while {action['name']}: {str(e)}")
        finally:
            action['status'] = 'completed'
            self.spinner.stop()

    def display_banner(self, text):
        banner_panel = Panel(Text(text, style="bold magenta"), border_style="magenta", expand=False, box=box.ROUNDED)
        self.console.print("\n")
        self.console.print(banner_panel)
        self.output_buffer.write(f"### {text} ###\n")

    def display_subphase(self, text):
        self.console.print(Text(text, style="bold blue"))
        self.output_buffer.write(f"--- {text} ---\n")

    def display_action_status(self, action_name, status, symbol, color):
        status_panel = Panel(Text(f"{symbol} {action_name} - {status}", style=f"bold {color}"), border_style=color, box=box.SQUARE)
        self.console.print(status_panel)
        self.output_buffer.write(f"{symbol} {action_name} - {status}\n")

    def log_json(self, title: str, data: Any, style: str = "bold green"):
        json_str = json.dumps(data, indent=4, sort_keys=True)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title=title, border_style=style, expand=True)
        self.console.print(panel)
        self.output_buffer.write(f"{title}: {json_str}\n")

    def log_error(self, message: str, data: Any = None):
        if data:
            json_str = json.dumps(data, indent=4, sort_keys=True)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            panel = Panel(syntax, title=message, border_style="red", expand=True)
        else:
            panel = Panel(message, title="Error", border_style="red", expand=True)
        self.console.print(panel)
        self.output_buffer.write(f"Error: {message}\n{json_str if data else ''}\n")

    def execute_command(self, command, directory, message=None):
        """Execute a shell command in a given directory and handle errors."""
        self.handle_wait(message if message else f"Executing command: {' '.join(command)}")

        # Constructing the command based on whether it's a pip operation
        if command[0] == 'pip':
            # Use sys.executable to ensure the correct pip is called
            full_command = [sys.executable, '-m'] + command
        else:
            full_command = command

        try:
            result = subprocess.run(
                full_command, cwd=directory, shell=False, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            command_output = {
                "args": result.args,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

            self.log_json("Command Output", command_output, style="grey")

            return result
        except subprocess.CalledProcessError as e:
            # Pretty print the CalledProcessError
            error_details = {
                "returncode": e.returncode,
                "cmd": e.cmd,
                "output": e.output,
                "stderr": e.stderr
            }
            self.log_error(f"Command {command} failed with error", error_details)
            return self.handle_error(f"Command {command} failed with error.")
        except Exception as e:
            self.log_error("Unexpected Error", str(e))
            return self.handle_error(f"Unexpected error: {str(e)}")


    def check_containers(self):
        """Check the status of Docker containers."""
        try:
            containers = subprocess.check_output(['docker', 'ps'], text=True).strip()
            self.print_container_status(containers)
        except subprocess.CalledProcessError as e:
            self.handle_error(f"Failed to check Docker containers: {str(e)}")

    def print_container_status(self, status):
        """Helper method to print container status."""
        self.console.print(Panel(status, title="Docker Containers", border_style="blue", expand=True))
        self.output_buffer.write(status + "\n")

    def copy_to_clipboard(self):
        """Copy the entire output buffer to the clipboard."""
        pyperclip.copy(self.output_buffer.getvalue())
        self.handle_info("Output copied to clipboard.")
