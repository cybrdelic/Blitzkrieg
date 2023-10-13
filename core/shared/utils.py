from ..cli.ui import show_spinner
import time
from ..cli.ui import print_error

def wait_for_container(docker, container_name, timeout=60):
    start_time = time.time()
    with show_spinner(f"Waiting for {container_name} to start..."):
        while True:
            if docker.is_container_running(container_name):
                return True
            elif time.time() - start_time > timeout:
                print_error(f"Timed out waiting for {container_name} to start")
                raise TimeoutError(f"Timed out waiting for {container_name} to start")  # Add this line
            time.sleep(2)
