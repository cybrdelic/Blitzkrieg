import os
import subprocess
import sys

def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.output}")
        sys.exit(1)
    return output.strip()

# Check which Python and Pip are being used
print(f"Using Python: {run_command('which python')}")
print(f"Using Pip: {run_command('which pip')}")

# Check installed packages and look for RunDBFast
installed_packages = run_command("pip list")
if "RunDBFast" in installed_packages:
    print("RunDBFast is installed.")
else:
    print("RunDBFast is NOT installed.")
    sys.exit(1)

# Check Python's sys.path to see where it's looking for modules
sys_path = run_command("python -c 'import sys; print(sys.path)'")
print(f"Python sys.path: {sys_path}")

# Check if the entry script exists
entry_script = os.path.expanduser("~/.venv/bin/db")
if os.path.exists(entry_script):
    print(f"Entry script exists: {entry_script}")
else:
    print(f"Entry script does NOT exist: {entry_script}")
    sys.exit(1)

print("All checks passed.")
