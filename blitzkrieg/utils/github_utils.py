import json
import os
from urllib.parse import urlparse
from blitzkrieg.db.models.project import Project
from blitzkrieg.ui_management.console_instance import console
import click
import requests

from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager
from blitzkrieg.utils.run_command import run_command

def create_github_repo(project: Project):
    """Create a new github repo."""
    github_token = load_github_token()
    project_name = project.name
    project_description = project.description

    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": project_name,
        "description": project_description,
        "private": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        console.handle_success(f'Successfully created repository "{project_name}"')
        repo_url = response.json()['html_url']
        project.github_repo = repo_url
        console.handle_info(f'You can access it at {repo_url}')
    elif response.status_code == 422:
        console.handle_error(f'Repository "{project_name}" already exists')
    elif response.status_code == 403:
        console.handle_error('Permission denied. Check your GitHub token')
    else:
        console.handle_error(f'Failed to create repository "{project_name}". Status code: {response.status_code}')

def load_github_token():
    github_token = blitz_env_manager.get_global_env_var('GITHUB_TOKEN')
    if not github_token:
        blitz_env_manager.set_global_env_var('GITHUB_TOKEN', click.prompt("Enter your Github Authentification token"))
        github_token = blitz_env_manager.get_global_env_var('GITHUB_TOKEN')
    return github_token

def push_project_to_repo(project: Project):
    workspace_dir_path = blitz_env_manager.get_active_workspace_dir()
    project_dir_path = os.path.join(workspace_dir_path, 'projects', project.name)
    # initlialize git within the project directory

    github_token = blitz_env_manager.get_global_env_var('GITHUB_TOKEN')
    if not github_token:
        blitz_env_manager.set_global_env_var('GITHUB_TOKEN', click.prompt("Enter your Github Authentification token"))
        github_token = blitz_env_manager.get_global_env_var('GITHUB_TOKEN')


    parsed_url = urlparse(project.github_repo)
    repo_url = f"https://{github_token}@{parsed_url.netloc}{parsed_url.path}.git"

    try:
        console.handle_wait(f"initializing git within the project directory: {project_dir_path}")
        run_command(f'cd {project_dir_path} && git init')
        run_command(f'cd {project_dir_path} && git add .')
        run_command(f'cd {project_dir_path} && git commit -m "Initial commit"')
        run_command(f'cd {project_dir_path} && git branch -M master')
        run_command(f'cd {project_dir_path} && git remote add origin {repo_url}')
        run_command(f'cd {project_dir_path} && git push -u origin master')
        console.handle_success(f"Successfully pushed project to GitHub")
    except Exception as e:
        console.handle_error(f"An error occurred while initializing git within the project directory: {str(e)}")

# create test PYPI project for TestPYPI site
def create_test_pypi_project(project: Project):
    project_name = project.name
    project_description = project.description

    try:
        console.handle_wait(f"Creating test PYPI project for {project_name}")
        project_dir_path = blitz_env_manager.get_active_project_dir(project_name)
        run_command(f'cd {project_dir_path} && poetry init -n')
        console.handle_success(f"Successfully created test PYPI project for {project_name}")
    except Exception as e:
        console.handle_error(f"An error occurred while creating test PYPI project for {project_name}: {str(e)}")
