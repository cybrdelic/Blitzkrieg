import os
import json

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def create_template():
    base_path = os.path.join('blitzkrieg', 'templates', 'poetry-cli-template')
    create_directory(base_path)

    # Create cookiecutter.json
    cookiecutter_json = {
        "project_name": "My Awesome CLI Tool",
        "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_') }}",
        "project_description": "A description of your awesome CLI tool",
        "author_name": "Your Name",
        "author_email": "your.email@example.com"
    }
    create_file(os.path.join(base_path, 'cookiecutter.json'), json.dumps(cookiecutter_json, indent=4))

    # Create project structure
    project_path = os.path.join(base_path, '{{cookiecutter.project_slug}}')
    create_directory(project_path)
    create_directory(os.path.join(project_path, '{{cookiecutter.project_slug}}'))
    create_directory(os.path.join(project_path, 'tests'))

    # Create __init__.py files
    create_file(os.path.join(project_path, '{{cookiecutter.project_slug}}', '__init__.py'), '''
import click

@click.command()
def main():
    """{{cookiecutter.project_description}}"""
    click.echo("Hello from {{cookiecutter.project_name}}!")

if __name__ == "__main__":
    main()
''')
    create_file(os.path.join(project_path, 'tests', '__init__.py'), '')

    # Create .gitignore
    create_file(os.path.join(project_path, '.gitignore'), '''
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
dist/
''')

    # Create pyproject.toml
    create_file(os.path.join(project_path, 'pyproject.toml'), '''
[tool.poetry]
name = "{{cookiecutter.project_slug}}"
version = "0.1.0"
description = "{{cookiecutter.project_description}}"
authors = ["{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>"]

[tool.poetry.dependencies]
python = "^3.8"
click = "^8.0.0"

[tool.poetry.dev-dependencies]
pytest = "^6.2.5"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
{{cookiecutter.project_slug}} = "{{cookiecutter.project_slug}}.cli:main"
''')

    # Create README.md
    create_file(os.path.join(project_path, 'README.md'), '''
# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run {{cookiecutter.project_slug}}
```
''')

    print(f"Cookiecutter template created at: {base_path}")

if __name__ == "__main__":
    create_template()
