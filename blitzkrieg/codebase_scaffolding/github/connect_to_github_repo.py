from colorama import Fore, Style
from blitzkrieg.codebase_scaffolding.config.config import load_user_details
import os
import subprocess

def run_command(command, success_msg, error_msg):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{error_msg}: {result.stderr}")
        return False
    print(success_msg)
    return True

def get_user_details():
    """Load user details."""
    return load_user_details()

def change_working_directory():
    """Change the current working directory to the parent directory."""
    try:
        # Save the current working directory
        current_dir = os.getcwd()

        # Change to the parent directory
        os.chdir(os.path.dirname(current_dir))
        print(f"Changed working directory from {current_dir} to {os.getcwd()}")

        # Change to the grandparent directory
        current_dir = os.getcwd()
        os.chdir(os.path.dirname(current_dir))
        print(f"Changed working directory from {current_dir} to {os.getcwd()}")

    except Exception as e:
        print(f"{Fore.RED}Error changing working directory: {e}{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}Current working directory: {os.getcwd()}{Style.RESET_ALL}")
    return True

def initialize_git():
    """Initialize the local directory as a Git repository."""
    return run_command(['git', 'init'], "Initializing git repository...", "Error initializing git repository")

def add_remote_repo(github_username, project_name):
    """Add the remote repository."""
    # First, remove any existing remote repository named "origin"
    run_command(['git', 'remote', 'remove', 'origin'], "Removing existing remote repository...", "Error removing existing remote repository")

    # Then, add the new remote repository
    return run_command(['git', 'remote', 'add', 'origin', f"https://github.com/{github_username}/{project_name}.git"], "Adding remote repository...", "Error adding remote repository")

def add_files_to_repo():
    """Add all the files in the local repository to staging."""
    return run_command(['git', 'add', '.'], "Adding files to git repository...", "Error adding files to git repository")

def show_git_status():
    """Show the status of the git repository."""
    return run_command(['git', 'status'], "Showing git status...", "Error showing git status")

def ask_user_to_proceed():
    """Ask the user if they want to proceed with the commit."""
    proceed = input("Do you want to proceed with the commit? (yes/no): ")
    return proceed.lower() in ['yes', 'y']

def commit_files():
    """Commit the files that you've staged in your local repository."""
    return run_command(['git', 'commit', '-m', 'Initial commit'], "Committing files...", "Error committing files")

def push_to_repo(github_username, project_name):
    try:
        subprocess.check_output(['git', 'remote', 'remove', 'origin'])
    except subprocess.CalledProcessError:
        pass  # Ignore the error if 'origin' remote doesn't exist

    try:
        subprocess.check_output(['git', 'remote', 'add', 'origin', f'https://github.com/{github_username}/{project_name}.git'])
        subprocess.check_output(['git', 'push', '-u', 'origin', 'master'])
    except subprocess.CalledProcessError as e:
        print(f"Error pushing to repository: {str(e)}")
        return False

    return True

def connect_to_github_repo():
    """Connect to a github repo using remote add origin."""
    details = get_user_details()
    github_username = details['github_username']
    project_name = details['project_name']

    if not initialize_git():
        return

    if not add_remote_repo(github_username, project_name):
        return

    if not add_files_to_repo():
        return

    if not show_git_status():
        return

    if not ask_user_to_proceed():
        return

    if not commit_files():
        return

    if not push_to_repo(github_username, project_name):
        return

    print(f"Successfully created and pushed to GitHub repository: https://github.com/{github_username}/{project_name}")
    return f"https://github.com/{github_username}/{project_name}"
