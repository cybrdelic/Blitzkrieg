import subprocess
from blitzkrieg.ui_management.console_instance import console

def install_package(package_name):
    """Install a package using pip."""
    try:
        console.handle_wait(f"Installing package: {package_name}")
        subprocess.run(["pip", "install", package_name], check=True)
        # if run smoothly
        console.handle_success(f"Successfully installed package: {package_name}")
    except subprocess.CalledProcessError as e:
        console.handle_error(f"Failed to install package: {package_name}. Exception e has occurred: {str(e)}")
        # break the program
        raise SystemExit
