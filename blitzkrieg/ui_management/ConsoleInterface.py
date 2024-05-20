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
        colored_text= self.parse_colors(text)
        banner_text = colored(f"\n{colored_text}\n", color="magenta", attrs=['bold'])
        print(banner_text)

    def parse_colors(self, message):
        output = []
        color_stack = []  # Stack to hold current active colors
        i = 0
        last_pos = 0  # Tracks the start of the next plain text segment

        while i < len(message):
            if message.startswith('[/', i):
                # Check for a closing tag
                close_bracket = message.find(']', i)
                if close_bracket != -1:
                    # Apply the color to the text up to this tag
                    if color_stack:
                        # Only color the text if there is an active color
                        output.append(colored(message[last_pos:i], color_stack[-1]))
                    else:
                        # Append without coloring if the stack is empty
                        output.append(message[last_pos:i])
                    # Remove the last color from the stack
                    color_stack.pop()
                    # Update last_pos to be after the current tag
                    last_pos = close_bracket + 1
                    i = close_bracket
            elif message.startswith('[', i):
                # Check for an opening tag
                close_bracket = message.find(']', i)
                if close_bracket != -1:
                    color = message[i+1:close_bracket]
                    color_stack.append(color)  # Push the new color onto the stack
                    # Apply the text up to this tag with the current color
                    if last_pos < i:
                        if color_stack and len(color_stack) > 1:
                            # Ensure to apply the previous color, not the current one
                            output.append(colored(message[last_pos:i], color_stack[-2]))
                        else:
                            output.append(message[last_pos:i])
                    # Update last_pos to be after the current tag
                    last_pos = close_bracket + 1
                    i = close_bracket
            i += 1

        # After exiting the loop, check if there's remaining text to output
        if last_pos < len(message):
            if color_stack:
                output.append(colored(message[last_pos:], color_stack[-1]))
            else:
                output.append(message[last_pos:])

        return ''.join(output)

    def log(self, message, level="info"):
        # Logging method to use spinner for displaying logs
        colored_message = self.parse_colors(message)
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
                colored_progress_message = self.parse_colors(progress_message)
                self.spinner.start(colored_progress_message)
                try:
                    func, args = func_tuple
                    task_output = func(**args)
                    success_message = self.parse_colors(f"{task_output}")
                    is_task_error = False if success_message.find("ERROR") == -1 else True
                    if is_task_error:
                        self.spinner.fail(success_message)
                    else:
                        self.spinner.succeed(success_message)
                except Exception as e:
                    error_message = f"run_tasks broken: {e}"
                    self.spinner.fail(error_message)
                    self.log(error_message, level="error")
                    break
