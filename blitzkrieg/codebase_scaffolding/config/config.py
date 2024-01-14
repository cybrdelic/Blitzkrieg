import json
import os

CONFIG_FILE_PATH = os.path.join(os.path.expanduser('~'), '.my_config.json')

def prompt_user_details():
    details = {}
    details['project_name'] = input('Enter your project name: ')
    details['email'] = input('Enter your email: ')
    details['github_username'] = input('Enter your GitHub username: ')
    details['description'] = input('Enter a description for your project: ')
    details['github_token'] = input('Enter your GitHub token: ')

    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(details, f)

def load_user_details():
    if not os.path.exists(CONFIG_FILE_PATH):
        prompt_user_details()

    with open(CONFIG_FILE_PATH, 'r') as f:
        details = json.load(f)
    return details
