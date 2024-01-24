import os
from rich import print as rprint

class DirectoryManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def create_directory(self, directory_path):
        os.makedirs(directory_path, exist_ok=True)

    def validate_directory_presence(self, directory, error_message):
        if not os.path.isdir(directory):
            rprint(f'[bold red]Error:[/bold red] {error_message}')
            raise FileNotFoundError(error_message)
