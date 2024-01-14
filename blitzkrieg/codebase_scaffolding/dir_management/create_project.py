import os
from blitzkrieg.codebase_scaffolding.script_management.create_activate_venv_script import create_activate_venv_script
from blitzkrieg.codebase_scaffolding.script_management.create_cli_test_script import create_cli_test_script

from blitzkrieg.codebase_scaffolding.config.config import load_user_details
from blitzkrieg.codebase_scaffolding.dependency_management.install_dependencies import install_dependencies
from blitzkrieg.codebase_scaffolding.dir_management.setup_cli_dir import setup_cli_dir

import subprocess

def create_project_dir(project_name: str):
    print("Creating project directory...")
    try:
        os.mkdir(project_name)
        os.listdir()
        project_dir = os.path.abspath(project_name)
        print(f"Successfully created project directory: {project_dir}")
        return project_dir
    except Exception as e:
        print(f"Error creating project directory: {e}")

def create_venv(project_dir: str):
    print("Creating virtual environment...")
    os.chdir(project_dir)
    result = subprocess.run(['python3', '-m', 'venv', '.venv'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error creating virtual environment: {result.stderr}")
        return
    print("Successfully created virtual environment.")

def create_gitignore(project_dir: str):
    print("Creating .gitignore...")
    os.chdir(project_dir)
    try:
        with open('.gitignore', 'w') as f:
            f.write(".venv/\n__pycache__/\n.pytest_cache/\n")
        print("Successfully created .gitignore.")
    except Exception as e:
        print(f"Error creating .gitignore: {e}")

def create_readme(project_dir: str):
    print("Creating README.md...")
    os.chdir(project_dir)
    try:
        with open('README.md', 'w') as f:
            f.write(f"# README {project_dir}\n")
        print("Successfully created README.md.")
    except Exception as e:
        print(f"Error creating README.md: {e}")

def create_setup(project_name: str, email: str, github_username: str, description: str, project_dir: str):
    print("Creating setup.py...")
    os.chdir(project_dir)
    setup_content = f"""
# setup.py
from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    author="{email}",
    author_email="{email}",
    description="{description}",
    url="https://github.com/{github_username}/{project_name}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={{"": "src"}},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "click",
        "blitzkrieg"
    ],
    entry_points={{
        'console_scripts': [
            '{project_name}={project_name}.core.{project_name}:main',
        ],
    }},
)
"""
    try:
        with open('setup.py', 'w') as f:
            f.write(setup_content.strip())
        print("Successfully created setup.py.")
    except Exception as e:
        print(f"Error creating setup.py: {e}")

def create_new_project():
    details = load_user_details()
    project_name = details['project_name']
    email = details['email']
    github_username = details['github_username']
    description = details['description']

    project_dir = create_project_dir(project_name)
    if project_dir is None:
        return
    create_venv(project_dir=project_dir)
    create_cli_test_script(project_dir=project_dir)
    create_activate_venv_script(project_dir=project_dir)
    create_gitignore(project_dir=project_dir)
    create_readme(project_dir=project_dir)
    create_setup(project_name=project_name, email=email, github_username=github_username, description=description, project_dir=project_dir)
    setup_cli_dir(project_dir=project_dir, project_name=project_name)
    install_dependencies(project_dir, details)
