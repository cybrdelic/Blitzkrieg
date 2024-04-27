import os
from contextlib import contextmanager

class ProjectManager:
    def __init__(self):
        self.project_root = None

    def find_project_root(self, marker='.git'):
        current_dir = os.getcwd()
        while True:
            if os.path.isdir(os.path.join(current_dir, marker)):
                self.project_root = current_dir
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                raise FileNotFoundError(f"Could not find the {marker} to identify the project root.")
            current_dir = parent_dir

    @contextmanager
    def temporary_directory_change(self, path):
        original_path = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(original_path)
