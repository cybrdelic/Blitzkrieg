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

@main.command('init')
@click.argument("workspace_name")
@click.argument("is_reverse")
def init(workspace_name, is_reverse):
    if is_reverse == 'reverse':
        WorkspaceManager(
            workspace_name=workspace_name,
            console=console_interface
        ).teardown_workspace()
    else:
        WorkspaceManager(
            workspace_name=workspace_name,
            console=console_interface
        ).blitz_init()



@main.command('setup-db')
def setup_db():
    WorkspaceManager().setup_db_schema()

# command to sync db and document systems
@main.command('sync')
@click.argument('system_to_update')
def update(system_to_update):
    """Run the update.sh script."""
    if system_to_update == 'issues':
        pass

@main.command('test')
@click.argument('test_name')
def test(test_name):
    if test_name == 'create_issue_in_db':
        pass

@main.command('delete')
@click.argument('entity_type')
def delete(entity_type):
    if entity_type == 'project':
        handle_delete_project_command()
    if entity_type == 'issue':
        pass

@main.command('setup-test')
def setup_test():
    """Run the setup_test_env.sh script."""
    subprocess.run(['../../bash/setup_test_env.sh'], check=True)

@main.command('create')
def create_project():
    handle_create_project_command()


@main.command('gen')
@click.argument('what_to_generate')
def generate_classes(what_to_generate):
    """Run the generate_classes.sh script."""
    if what_to_generate == 'classes':
        generator = DBClassGenerator(models_dir='blitzkrieg/db/models/', templates_dir='blitzkrieg/db/class_generation/templates/')
        generator.generate_for_all_models()

if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
