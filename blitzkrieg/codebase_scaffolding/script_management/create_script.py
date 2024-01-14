import os

def make_script_executable(script_path):
    os.chmod(script_path, 0o755)

def get_script_path(project_dir, script_name):
    # make scripts dir if not created
    if not os.path.isdir(os.path.join(project_dir, 'scripts')):
        os.mkdir(os.path.join(project_dir, 'scripts'))
    return os.path.join(project_dir, 'scripts',script_name)

def write_script(script_path, script_content):
    with open(script_path, 'w') as f:
        f.write(script_content)

def write_bash_script(script_path, script_content):
    write_script(script_path, f"""#!/bin/bash
{script_content}
    """)

# function that takes list of commands and creates bash script from it:
def create_bash_script_from_commands(commands, script_path):
    script_content = '\n'.join(commands)
    write_bash_script(script_path, script_content)
