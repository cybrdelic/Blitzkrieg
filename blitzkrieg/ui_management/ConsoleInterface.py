from loguru import logger
from halo import Halo
from termcolor import colored
from datetime import datetime
import re

class ConsoleInterface:
    def __init__(self):
        logger.remove()
        logger.add(lambda msg: print(msg), colorize=True)  # Ensure basic logging setup
        self.spinner = Halo(spinner='dots')  # Initialize spinner
        self.message_colors = {
            'success': 'green',
            'warning': 'yellow',
            'error': 'red',
            'info': 'white'  # Default color
        }
        self.process_name = ''
        self.tasks = []
        self.task_groups = []
        self.current_task_key = ''

    def create_process(self, process_name):
        """Creates a new process with a name."""
        self.process_name = process_name
        self.steps = []

    def add_task(self, key, func_tuple, progress_message, error_message):
        """Adds a task to the process."""
        self.tasks.append({
            'key': key,
            'func_tuple': func_tuple,
            'progress_message': progress_message,
            'error_message': error_message
        })

    def add_task_group(self, title, task_keys):
        """Adds a task group to the process."""
        self.task_groups.append({
            'title': title,
            'task_keys': task_keys
        })


    def display_step(self, title, message, status="info"):
        """Displays a message with a title for each step with color based on the status."""
        color = self.get_color(status)
        colored_title = colored(title, color, attrs=['bold'])
        prefix = self.get_prefix(status)
        colored_prefix = colored(prefix, color, attrs=['bold'])

        # Display formatted step information
        print(f"\n=== {colored_title} ===\n{colored_prefix}{message}\n")

    def get_color(self, status):
        """Returns the color associated with the message status."""
        return {
            'success': 'green',
            'warning': 'yellow',
            'error': 'red',
            'info': 'cyan'
        }.get(status, 'white')

    def get_prefix(self, status):
        """Returns the prefix based on the status."""
        return {
            'success': 'SUCCESS: ',
            'error': 'ERROR: ',
            'warning': 'WARNING: ',
            'info': ''
        }.get(status, '')

    def handle_error(self, exception):
        """Handles errors by logging them and displaying an error message in the console."""
        task = next((task for task in self.tasks if task['key'] == self.current_task_key), None)
        if task:
            error_message = f"[red]ERROR: {exception}[/red]"
            return error_message
        else:
            return f"[red]ERROR: task_key not related to Task{exception}[/red]"

    def handle_success(self, message):
        """Handles success by logging it and displaying a success message in the console."""
        task = next((task for task in self.tasks if task['key'] == self.current_task_key), None)
        if task:
            success_message = f"[green]SUCCESS: {message}[/green]"
            return success_message
        else:
            return f"[red]ERROR: task_key not related to Task{message}[/red]"

    def display_banner(self, text):
        # Display banner with color parsing
        colored_text, _ = self.parse_colors(text)
        banner_text = colored(f"\n{colored_text}\n", color="magenta", attrs=['bold'])
        print(banner_text)



    def parse_colors(self, message):
        # Regex to parse color tags and apply colors dynamically
        pattern = r'\[(\w+)\](.*?)\[\/\w+\]'
        matches = re.finditer(pattern, message)
        is_error = False

        for match in matches:
            color = match.group(1).lower()
            text = match.group(2)
            if color == "red":
                is_error = True  # Detect errors by red color usage
            colored_text = colored(text, color)
            message = message.replace(match.group(0), colored_text)

        return message, is_error

    def log(self, message, level="info"):
        # Logging method to use spinner for displaying logs
        colored_message, is_error = self.parse_colors(message)
        level_icon = {
            "info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"
        }
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        final_message = f"{level_icon[level]} [{timestamp}] {colored_message}" # Print final message
    def index_tasks_by_task_groups(self):
        # Index tasks by task groups
        for task_group in self.task_groups:
            task_group['tasks'] = [task for task in self.tasks if task['key'] in task_group['task_keys']]

    def run_tasks(self):
        self.index_tasks_by_task_groups()
        for task_group in self.task_groups:
            self.display_banner(task_group['title'])
            for task in task_group['tasks']:
                self.current_task_key = task['key']
                key, func_tuple, progress_message, error_message = task.values()
                colored_progress_message, _ = self.parse_colors(progress_message)
                self.spinner.start(colored_progress_message)
                try:
                    func, args = func_tuple
                    task_output = func(**args)
                    success_message, is_task_error = self.parse_colors(f"{task_output}")
                    if is_task_error:
                        self.spinner.fail(success_message)
                    else:
                        self.spinner.succeed(success_message)
                except Exception as e:
                    error_message = "run_tasks broken"
                    self.spinner.fail(error_message)
                    self.log(error_message, level="error")
                    break
