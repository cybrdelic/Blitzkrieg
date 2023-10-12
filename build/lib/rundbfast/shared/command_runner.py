import subprocess
import socket
from rich.console import Console

console = Console()

class CommandRunner:
    @staticmethod
    def run_command(command):
        try:
            return subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout.strip()
        except subprocess.CalledProcessError as e:
            console.print(f"Error executing '{command}':", e.stderr, style="bold red")
            raise
    @staticmethod
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    @staticmethod
    def find_available_port(starting_port=5432):
        port = starting_port
        while CommandRunner.is_port_in_use(port):
            port += 1  # try the next port
        return port
