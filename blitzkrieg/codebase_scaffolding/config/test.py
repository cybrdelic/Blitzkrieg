from blitzkrieg.codebase_scaffolding.config.config import load_user_details
import os

CONFIG_FILE_PATH = os.path.join(os.path.expanduser('~'), '.my_config.json')

if __name__ == '__main__':
    # Remove the config file if it exists to force prompting user details
    if os.path.exists(CONFIG_FILE_PATH):
        os.remove(CONFIG_FILE_PATH)
    details = load_user_details()
    print(details)
