# file_utils.py

import os

def get_files(directory, suffix):
    return [file for file in os.listdir(directory) if file.endswith(suffix)]

def add_uuid_to_file(file_path, uuid_str):
    with open(file_path, 'r+') as file:
        content = file.read()
        file.seek(0, 0)
        file.write(f'{uuid_str}\n{content}')
