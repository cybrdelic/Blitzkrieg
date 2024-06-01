import logging
from halo import Halo
from termcolor import colored
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Setup a basic logger to output to a specific file or standard out
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

class ConsoleInterface:
    def __init__(self):
        self.rich_console = Console()
        self.spinner = Halo(spinner='dots', text='Initializing...', placement='left')
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
            'messages': []
        }
        group['tasks'].append(task)
        return task

    def handle_success(self, message):
        message = colored(f"{message}", 'green')
        self.spinner.succeed(message)

    def handle_error(self, message):
        message = colored(f"{message}", 'red')
        self.spinner.fail(message)

    def handle_info(self, message):
        message = colored(f"   {message}", 'cyan')
        self.spinner.info(message)

    def log(self, message):
        logging.info(message)
        print(message)

    def run_process(self, process):
        for group in process['groups']:
            self.display_banner(group['title'])
            for task in group['tasks']:
                self.display_subgroup(task['name'])
                self.run_task(task)

    def run_task(self, task):
        self.current_task = task
        self.spinner.start(task['name'])
        try:
            result = task['func'](**task['args'])
        except Exception as e:
            self.handle_error(f"Task failed: {str(e)}")
        finally:
            self.current_task = None
            self.spinner.stop()



    def display_banner(self, text):
        # Create styled text
        colored_text = Text(text, style="bold magenta")

        # Create a panel with the colored text
        banner_panel = Panel(colored_text, border_style="magenta", expand=False)

        # Print the banner
        self.rich_console.print("\n")
        self.rich_console.print(banner_panel)


    def display_subgroup(self, text):
        # Display subgroup with color parsing
        colored_text = text
        subgroup_text = colored(f"\n{colored_text}\n", color="blue", attrs=['bold'])
        print(subgroup_text)
