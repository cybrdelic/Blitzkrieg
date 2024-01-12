
import subprocess

def run_command(command, capture_output=False):
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE if capture_output else None)
        return result.stdout.decode('utf-8') if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        exit(1)
