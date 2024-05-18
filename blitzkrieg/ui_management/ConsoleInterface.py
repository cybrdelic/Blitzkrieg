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

    def display_step(self, title, x=""):
        # Display step with color parsing
        colored_title, _ = self.parse_colors(title)
        step_text = colored(f"\n=== {colored_title} ===\n", 'cyan', attrs=['bold'])
        print(step_text)

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

    def run_tasks(self, tasks, title, task_progress_message_map):
        self.display_banner(title)

        for task in tasks:
            func, args = task if len(task) > 1 else (task[0], {})
            task_name = func.__name__
            task_progress_message = task_progress_message_map.get(task_name, "Executing task")

            colored_task_message, is_error = self.parse_colors(task_progress_message)
            self.spinner.start(colored_task_message)  # Start spinner with colored message

            try:
                task_output = func(**args)
                success_message, is_task_error = self.parse_colors(f"SUCCESS: {task_output}")
                if is_task_error:
                    self.spinner.fail(success_message)  # Fail spinner on task errors
                else:
                    self.spinner.succeed(success_message)  # Succeed spinner on task completion
            except Exception as e:
                error_message, _ = self.parse_colors(f"ERROR: {str(e)}")
                self.spinner.fail(error_message)  # Fail spinner on exceptions
                self.log(error_message, level="error")
                break  # Exit loop on error
