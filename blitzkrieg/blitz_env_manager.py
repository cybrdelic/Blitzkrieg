import os
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface, FileManager

class BlitzEnvManager:
    def __init__(self, workspace_name: str):
        self.console = console
        self.workspace_name = workspace_name
        self.file_name = '.blitz.env'
        self.workspace_file_path = os.path.join(os.getcwd(), self.workspace_name, self.file_name)
        self.global_env_file_path = os.path.join(os.getcwd(), self.file_name)
        self.file_manager = FileManager()

    def __get_env_var_line_value(self, key: str, value: str) -> str:
        return f"{key.upper()}={value}\n"

    def __get_env_var_value_from_line(self, line: str) -> str:
        return line.split('=')[1].strip()

    def __get_env_var_value(self, key: str, path) -> str:
        try:
            if not path:
                raise FileNotFoundError("File path is not set.")
            with open(path, 'r') as env_file:
                for line in env_file:
                    if key.upper() in line:
                        return self.__get_env_var_value_from_line(line)
            return None
        except FileNotFoundError:
            self.console.handle_error(f"Could not find the .blitz.env file at {path}. Please create one using the 'create' command")
            return None
        except Exception as e:
            self.console.handle_error(f"An error occurred while reading the .blitz.env file: {e}")
            return None

    def __add_env_var_line_to_file(self, key: str, value: str, path) -> None:
        try:
            with open(path, 'a') as env_file:
                line_value = self.__get_env_var_line_value(key, value)
                env_file.write(line_value)
                self.console.handle_info(f"Added the environment variable: {line_value} at the following path: {path}")
        except Exception as e:
            self.console.handle_error(f"An error occurred while writing to the .blitz.env file: {e}")

    def __env_file_exists(self, path) -> bool:
        return os.path.isfile(path)

    def __create_env_file(self, path) -> None:
        try:
            if self.__env_file_exists(path):
                self.console.handle_info(f"The .blitz.env file already exists at {path}")
            else:
                with open(path, 'w') as env_file:
                    env_file.write("# This file contains environment variables for the Blitzkrieg CLI\n")
                self.console.handle_info(f"Created a .blitz.env file at {path}")
        except Exception as e:
            self.console.handle_error(f"An error occurred while creating the .blitz.env file: {e}")

    def __ensure_env_var(self, key: str, value_prompt: str, path) -> str:
        value = self.__get_env_var_value(key, path)
        if not value:
            value = input(value_prompt)
            self.__add_env_var_line_to_file(key, value, path)
        return value

    def get_env_var_value_from_workspace_env_file(self, key: str) -> str:
        return self.__get_env_var_value(key, self.workspace_file_path)

    def get_env_var_value_from_global_env_file(self, key: str) -> str:
        return self.__get_env_var_value(key, self.global_env_file_path)

    def add_env_var_to_workspace_file(self, key: str, value: str) -> None:
        self.__add_env_var_line_to_file(key, value, self.workspace_file_path)

    def add_env_var_to_global_file(self, key: str, value: str) -> None:
        self.__add_env_var_line_to_file(key, value, self.global_env_file_path)

    def workspace_env_file_exists(self) -> bool:
        return self.__env_file_exists(self.workspace_file_path)

    def global_env_file_exists(self) -> bool:
        return self.__env_file_exists(self.global_env_file_path)

    def create_workspace_env_file(self) -> None:
        self.__create_env_file(self.workspace_file_path)

    def create_global_env_file(self) -> None:
        self.__create_env_file(self.global_env_file_path)

    def ensure_workspace_env_var(self, key: str, value_prompt: str) -> str:
        return self.__ensure_env_var(key, value_prompt, self.workspace_file_path)

    def ensure_global_env_var(self, key: str, value_prompt: str) -> str:
        return self.__ensure_env_var(key, value_prompt, self.global_env_file_path)
