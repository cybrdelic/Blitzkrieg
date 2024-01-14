from blitzkrieg.codebase_scaffolding.script_management.paths import ACTIVATE_VENV_PATH
from blitzkrieg.codebase_scaffolding.script_management.create_script import create_bash_script_from_commands, get_script_path, make_script_executable
from blitzkrieg.codebase_scaffolding.config.config import load_user_details


def create_activate_venv_script(project_dir):
    details = load_user_details()
    project_name = details['project_name']
    script_path = get_script_path(project_dir, ACTIVATE_VENV_PATH)
    create_bash_script_from_commands([
        ". .venv/bin/activate",
        "pip install -e .",
        "pip freeze > requirements.txt",
    ], script_path)

    make_script_executable(script_path)
