# validation_utils.py

import uuid
from blitzkrieg.ui_management.console_instance import console
from packaging import version as packaging_version
import subprocess
import os

from blitzkrieg.utils.action_utils import install_package

def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

def validate_version_number(version_num):
    try:
        # Validate the version number
        packaging_version.parse(version_num)
        return True
    except packaging_version.InvalidVersion:
        console.handle_error(f"Invalid version number: {version_num}")
        return False

def validate_package_version(package_name: str):
    try:
        poetry_version = subprocess.run([package_name, '--version'], check=True, stdout=subprocess.PIPE)
        poetry_version = poetry_version.stdout.decode('utf-8').strip().split()[1]
        if not validate_version_number(poetry_version, console):
            return False
        return True
    except subprocess.CalledProcessError:
        console.handle_error("Failed to check poetry version.")
        return False

def validate_package_installation(package_name: str):
    try:
        subprocess.run([package_name, '--version'], check=True)
        return True
    except subprocess.CalledProcessError:
        # try to install poetry
        install_package('poetry')
        poetry_version_is_valid = validate_package_version('poetry')
        if not poetry_version_is_valid:
            console.handle_error("Failed to install poetry. Check the validate_poetry_installation() function.")
            return False
        console.handle_success("Poetry installed successfully.")

def validate_file_exists_in_cwd(file_name: str):
    if not os.path.exists(file_name):
        console.handle_error(f"File {file_name} not found in directory {os.getcwd()}")
        return False
    return True
