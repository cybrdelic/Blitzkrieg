from blitzkrieg.cli.cli_interface import handle_create_project_command, handle_delete_project_command
import click
import subprocess
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface
from blitzkrieg.workspace_manager import WorkspaceManager
from blitzkrieg.db.class_generation.DBClassGenerator import DBClassGenerator

console_interface = ConsoleInterface()
@click.group()
def main():
    pass

@main.command('create-workspace')
@click.argument("workspace_name")
def create_workspace(workspace_name):

    # read email and password from file in cwd titled blitz.env. if they dont exist prompt user for them, then save them in a file called blitz.env.
    try:
        env_file = open('blitz.env', 'r')
        if env_file:
            env_vars = env_file.readlines()
            env_file.close()
            # find the lines with 'email'
            email = env_vars[0].split('=')[1].strip()
            # find the lines with 'password'
            password = env_vars[1].split('=')[1].strip()
            if not email:
                email = input('Enter your email: ')
                # store email in blitz.env
                env_vars[0] = f'email={email}\n'
                # write to file
                env_file = open('blitz.env', 'w')
                env_file.writelines(env_vars)
                env_file.close()
            if not password:
                password = input('Enter your password: ')
                # store password in blitz.env
                env_vars[1] = f'password={password}\n'
                # write to file
                env_file = open('blitz.env', 'w')
                env_file.writelines(env_vars)
                env_file.close()
        else:
            email = input('Enter your email: ')
            password = input('Enter your password: ')
            # store email and password in blitz.env
            env_file = open('blitz.env', 'w')
            env_file.write(f'email={email}\n')
            env_file.write(f'password={password}\n')
            env_file.close()
    except FileNotFoundError as e:
        email = input('Enter your email: ')
        password = input('Enter your password: ')
        # store email and password in blitz.env
        env_file = open('blitz.env', 'w')
        env_file.write(f'email={email}\n')
        env_file.write(f'password={password}\n')
        env_file.close()



    WorkspaceManager(
        workspace_name=workspace_name,
        console=console_interface,
        email=email,
        password=password
    ).blitz_init()

@main.command('delete-workspace')
@click.argument("workspace_name")
def delete_workspace(workspace_name):
    email=''
    password=''
    WorkspaceManager(
        workspace_name=workspace_name,
        console=console_interface,
        email=email,
        password=password
    ).teardown_workspace()

# @main.command("show")
# @click.argument("workspace_name")
# def show(workspace_name):
#     WorkspaceManager(workspace_name=workspace_name, console=console_interface, email="dfsfdsd", password='').show_workspace_details()

# @main.command('delete')
# @click.argument('entity_type')
# def delete(entity_type):
#     if entity_type == 'project':
#         handle_delete_project_command()
#     if entity_type == 'issue':
#         pass

@main.command('setup-test')
def setup_test():
    """Run the setup_test_env.sh script."""
    subprocess.run(['../../bash/setup_test_env.sh'], check=True)

# @main.command('create')
# def create_project():
#     handle_create_project_command()

if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
