
import click
import subprocess
from blitzkrieg.blitz_env_manager import BlitzEnvManager
from packaging import version as packaging_version
import os

@click.group()
def main():
    """{{cookiecutter.project_description}}"""
    click.echo("Hello from {{cookiecutter.project_name}}!")

if __name__ == "__main__":
    main()
