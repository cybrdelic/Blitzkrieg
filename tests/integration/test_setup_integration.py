import subprocess
import os

def create_venv():
    """Create a new virtual environment and return its path."""
    venv_dir = ".test_venv"
    subprocess.check_call(['python3','-m', 'venv', venv_dir])
    subprocess.check_call([f'{venv_dir}/bin/activate'])
    return venv_dir

def test_cli_installation_and_execution():
    # Step 1: Create a new virtual environment
    venv_dir = create_venv()
    venv_bin_dir = os.path.join(venv_dir, 'bin')
    pip = os.path.join(venv_bin_dir, 'pip')
    python = os.path.join(venv_bin_dir, 'python')

    # Step 2: Install our package in the new virtual environment
    subprocess.check_call([pip, 'install', '-e', '.'])

    # Step 3: Check if the 'db' command got installed
    db_command = os.path.join(venv_bin_dir, 'db')
    assert os.path.exists(db_command), "'db' command was not installed."

    # Step 4: Test the behavior of the 'db' command
    result = subprocess.run([db_command, 'setup', 'postgres'])
    assert result.returncode == 0, f"'db setup postgres' command failed with exit code {result.returncode}."

    # Cleanup
    subprocess.check_call(['rm', '-r', venv_dir])
