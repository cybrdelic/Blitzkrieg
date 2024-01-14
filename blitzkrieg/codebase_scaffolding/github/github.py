import requests
import json
from blitzkrieg.codebase_scaffolding.config.config import load_user_details

def create_github_repo():
    """Create a new github repo."""
    details = load_user_details()
    project_name = details['project_name']
    token = details['github_token']

    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": project_name,
        "description": "This is a repository created by Python script.",
        "private": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print(f'Successfully created repository "{project_name}"')
        repo_url = response.json()['html_url']
        print(f'You can access it at {repo_url}')
    elif response.status_code == 422:
        print(f'Repository "{project_name}" already exists')
    elif response.status_code == 403:
        print('Permission denied. Check your GitHub token')
    else:
        print(f'Failed to create repository "{project_name}". Status code: {response.status_code}')

def delete_github_repo():
    """Delete a github repo."""
    details = load_user_details()
    github_username = details['github_username']
    project_name = details['project_name']
    token = details['github_token']

    url = f"https://api.github.com/repos/{github_username}/{project_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f'Successfully deleted repository "{project_name}"')
    elif response.status_code == 404:
        print(f'Repository "{project_name}" not found')
    elif response.status_code == 403:
        print('Permission denied. Check your GitHub token')
    elif response.status_code == 401:
            print("Failed to delete the GitHub repository due to an authorization error. Please check your GitHub access token.")

    else:
        print(f'Failed to delete repository "{project_name}". Status code: {response.status_code}')
