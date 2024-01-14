from colorama import Fore, Style
import os
import sys
from contextlib import contextmanager
from colorama import Fore, init

init(autoreset=True)  # Automatically reset the color to the default after printing


@contextmanager
def change_dir(destination):
    try:
        cwd = os.getcwd()
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)

def check_project_dir(project_name):
    project_dir = os.path.dirname(os.path.dirname(os.getcwd()))
    print(f"Initial project_dir in check_project_dir: {project_dir}")  # Debug print

    while True:
        # Break if we've reached the filesystem root or found the project directory
        if project_dir == '/' or os.path.basename(project_dir) == project_name:
            break

        # Check if the parent directory is 'src' and its parent is the project_name
        parent_dir = os.path.dirname(project_dir)
        if os.path.basename(parent_dir) == 'src' and os.path.basename(os.path.dirname(parent_dir)) == project_name:
            # Set project_dir to the grandparent directory
            project_dir = os.path.dirname(parent_dir)
            print(f"Updated project_dir in check_project_dir: {project_dir}")  # Debug print
            break
        else:
            # Move up one directory
            project_dir = parent_dir

    # Check if the final directory is the project_name
    if os.path.basename(project_dir) == project_name:
        return project_dir
    else:
        print(f"Could not find project root directory for project {project_name}.")
        return None


def activate_venv(project_dir, attempt=1):
    init(autoreset=True)  # Automatically reset the color to the default after printing

    if project_dir is None:
        print("Project directory not specified. Cannot activate virtual environment.")
        return

    print(f"Attempt {attempt} to activate virtual environment in: {project_dir}")

    venv_path = os.path.join(project_dir, '.venv')
    activation_script = os.path.join(project_dir, 'scripts', 'activate_venv.sh')
    scaleton_dir = "/home/cybrdelic/alexf/software-projects/automation/scaleton"  # replace with the actual path to scaleton

    # Change the current working directory to the project directory
    os.chdir(project_dir)

    # prints if activation script does or does not exist. prints in red
    print(f"Activation script {activation_script} exists: {Fore.RED}{os.path.exists(activation_script)}{Style.RESET_ALL}")

    if not os.path.exists(activation_script):
        if attempt > 10:  # stop the recursion after 10 attempts
            print("Failed to find the activation script after multiple attempts.")
            return

        print(f"Activation script {activation_script} does not exist. Moving up {attempt} directories.")
        project_dir = os.path.dirname(project_dir)  # move up one directory
        activate_venv(project_dir, attempt + 1)
        return

    with change_dir(project_dir):
        command = f'bash {activation_script}'
        try:
            if 'VIRTUAL_ENV' not in os.environ:
                print('Re-running this script in the virtual environment...')
                os.system(f'bash -c "source {activation_script} && pip install -e {scaleton_dir} && python {" ".join(sys.argv)}"')
                sys.exit(0)
            else:
                print(Fore.GREEN + f'Successfully activated virtual environment in: {project_dir}')
        except Exception as e:
            print(f'Failed to activate virtual environment in: {project_dir}')
            print(f'Error: {e}')
            sys.exit(1)

def install_dependencies(project_dir, details, attempt=0):
    project_name = details['project_name']
    print(f"Loaded user details for project: {project_name}")

    project_dir = check_project_dir(project_name)
    print(f"Project_dir in install_dependencies: {project_dir}")  # Debug print
    activate_venv(project_dir)
