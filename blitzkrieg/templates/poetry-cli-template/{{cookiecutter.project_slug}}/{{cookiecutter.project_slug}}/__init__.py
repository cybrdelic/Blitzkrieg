
import click

@click.command()
def main():
    """{{cookiecutter.project_description}}"""
    click.echo("Hello from {{cookiecutter.project_name}}!")

if __name__ == "__main__":
    main()
