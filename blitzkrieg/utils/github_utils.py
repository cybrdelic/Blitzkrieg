import json
import os
from blitzkrieg.ui_management.console_instance import console
import click
import requests

from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager

def create_github_repo(project_name: str, project_description: str):
    """Create a new github repo."""
    github_token = load_github_token()

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
