import os
import uuid

class FileManager:
    def __init__(self):
        pass

    def read_file(self, file_path):
        """Read and return the content of a file, given its path."""
        if os.path.isfile(file_path):  # Check if the path is actually a file
            with open(file_path, 'r') as file:
                return file.read()
        else:
            raise ValueError(f"The path {file_path} is not a file.")

    @staticmethod
    def write_file(file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)

    @staticmethod
    def list_files_with_suffix(directory, suffix):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(suffix)]

    def delete_file(self, file_path):
        os.remove(file_path)

    def append_uuid_to_file(self, file_path, id_uuid):
        # Assuming you want to rename the file to include the UUID at the beginning
        directory, filename = os.path.split(file_path)
        suffix = filename.split('.')[-1]
        if not id_uuid:
            id_uuid = str(uuid.uuid4())
        filename_without_suffix = filename.split('.')[0]
        new_filename = f"{filename_without_suffix}_{id_uuid}.{suffix}"
        new_file_path = os.path.join(directory, new_filename)
        os.rename(file_path, new_file_path)

    def chmod_permissions(self, file_path, mode):
        os.chmod(file_path, mode)

    def replace_text_in_file(self, file_path, old_text, new_text):
        with open(file_path, 'r') as file:
            file_content = file.read()
        new_file_content = file_content.replace(old_text, new_text)
        with open(file_path, 'w') as file:
            file.write(new_file_content)
