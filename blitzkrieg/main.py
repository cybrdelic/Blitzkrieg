from blitzkrieg.cli_interface import handle_create_project_command, handle_delete_project_command, handle_link_pgadmin_postgres_command, handle_pgadmin_postgres_init_all_command, handle_pgadmin_postgres_init_command, handle_remove_postgres_pgadmin_command, handle_remover_postgres_pgadmin_command
import click
import subprocess
import os

from blitzkrieg.db.class_generation.DBClassGenerator import DBClassGenerator
@click.group()
def main():
    pass

@main.command('pg')
@click.argument('project_name')
def init(project_name):
    handle_pgadmin_postgres_init_command(project_name)

@main.command("pg-all")
def all():
    handle_pgadmin_postgres_init_all_command()

@main.command('remover-pg')
def remover():
    handle_remover_postgres_pgadmin_command()

@main.command('remove-pg')
@click.argument('project_name')
def remove(project_name):
    handle_remove_postgres_pgadmin_command(project_name)

@main.command('link-pg')
@click.argument('project_name_1')
@click.argument('project_name_2')
@click.argument('parent_name')
def link(project_name_1, project_name_2, parent_name):
    handle_link_pgadmin_postgres_command(project_name_1, project_name_2, parent_name)

# command to sync db and document systems
@main.command('sync')
@click.argument('system_to_update')
def update(system_to_update):
    """Run the update.sh script."""
    if system_to_update == 'issues':
        os.system("python3 blitzkrieg/project_management/db/make/create_issues.py")

@main.command('setup-test')
def setup_test():
    """Run the setup_test_env.sh script."""
    subprocess.run(['../../bash/setup_test_env.sh'], check=True)

@main.command('create')
def create_project():
    handle_create_project_command()

@main.command('delete')
def delete_project():
    handle_delete_project_command()

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
