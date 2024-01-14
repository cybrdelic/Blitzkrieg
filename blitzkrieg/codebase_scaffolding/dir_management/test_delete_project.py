import os
import shutil

from blitzkrieg.codebase_scaffolding.config.config import load_user_details
from blitzkrieg.github.github import delete_github_repo

if __name__ == '__main__':
    details = load_user_details()
    project_name = details['project_name']

    os.system('ls')

    if os.path.isdir(project_name):
        try:
            shutil.rmtree(project_name)
            print(f'Successfully removed directory "{project_name}"')
        except Exception as e:
            print(f'Error while removing directory "{project_name}": {e}')
    else:
        print(f'Directory "{project_name}" does not exist')

    delete_github_repo()
