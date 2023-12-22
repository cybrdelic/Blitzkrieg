import os
import subprocess
import sys
from dotenv import load_dotenv

def run_command(command, error_message):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}")
        print(e)
        sys.exit(1)

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get PyPI username and API key from environment variables
    pypi_username = os.getenv("PYPI_USERNAME")
    pypi_api_key = os.getenv("PYPI_API_KEY")

    if not pypi_username or not pypi_api_key:
        print("Error: Missing PyPI username or API key in .env file.")
        sys.exit(1)

    # Increment the version in setup.py manually or programmatically here, if needed

    # Create distributions
    run_command("python setup.py sdist bdist_wheel", "Failed to create distributions.")

    # Upload to PyPI
    twine_command = (
        f"twine upload "
        f"--username '{pypi_username}' "
        f"--password '{pypi_api_key}' "
        "dist/*"
    )

    run_command(twine_command, "Failed to upload package to PyPI.")

    print("Successfully uploaded package to PyPI.")

if __name__ == "__main__":
    main()
