import os

class FileManager:
    @staticmethod
    def read_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def write_file(file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)

    @staticmethod
    def list_files_with_suffix(directory, suffix):
        return [file for file in os.listdir(directory) if file.endswith(suffix)], directory
