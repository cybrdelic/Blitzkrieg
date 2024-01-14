from blitzkrieg.codebase_scaffolding.script_management.paths import TEST_CLI_PATH
from blitzkrieg.codebase_scaffolding.script_management.create_script import create_bash_script_from_commands, get_script_path, make_script_executable
from blitzkrieg.codebase_scaffolding.config.config import load_user_details


def create_cli_test_script(project_dir):
    details = load_user_details()
    project_name = details['project_name']
    script_path = get_script_path(project_dir, TEST_CLI_PATH)
    create_bash_script_from_commands([
        f"pip uninstall {project_name}",
        f"pip install -e .",
        f"{project_name} --help",
    ], script_path)

    make_script_executable(script_path)
