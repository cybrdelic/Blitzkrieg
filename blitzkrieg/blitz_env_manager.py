import os

from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface


class BlitzEnvManager:
    def __init__(self, console: ConsoleInterface, workspace_name: str):
        self.env_vars = []
        self.console: ConsoleInterface = console
        self.workspace_name = workspace_name
        self.file_name = '.blitz.env'
        self.file_path = None

    def __get_env_var_line_value(self, key: str, value: str) -> str:
        return f"{key.capitalize()}={value}\n"

    def get_env_var_value(self, key: str) -> str:
        try:
            with open(self.file_path, 'r') as env_file:
                for line in env_file:
                    if key in line:
                        return line.split('=')[1].strip()
                    else:
                        self.console.handle_error(f"Could not find the environment variable {key} in the .blitz.env file")
                        return None
        except FileNotFoundError:
            self.console.handle_error(
                f"Could not find the .blitz.env file at {self.file_path}. Please create one using the 'create' command"
            )
            return None
        except Exception as e:
            self.console.handle_error(f"An error occurred while reading the .blitz.env file: {e}")
            return None

    def add_env_var_to_file(self, key: str, value: str) -> None:
        line_value = self.__get_env_var_line_value(key, value)

        with open(self.file_path, 'a') as env_file:
            env_file.write(line_value)
            self.console.handle_info(
                f"Adding the following environment variable to the .blitz.env file at {self.file_path}: {line_value}"
            )

    def create_blitz_dot_env_file(self, dir_path) -> None:
        self.console.handle_info(f"Creating a .blitz.env file in the {dir_path} directory")
        self.file_path = os.path.join(dir_path, self.file_name)
        with open(self.file_path, 'w') as env_file:
            env_file.write("// This file contains environment variables for the Blitzkrieg CLI\n")
        self.console.display_file_content(self.file_path)
