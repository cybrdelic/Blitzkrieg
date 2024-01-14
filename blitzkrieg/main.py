from blitzkrieg.cli_interface import handle_create_project_command, handle_delete_project_command, handle_link_pgadmin_postgres_command, handle_pgadmin_postgres_init_all_command, handle_pgadmin_postgres_init_command, handle_remove_postgres_pgadmin_command, handle_remover_postgres_pgadmin_command
import click
import subprocess
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

if __name__ == "__main__":
    click.echo("Starting the application...")
    main()
