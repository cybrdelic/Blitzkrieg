from pathlib import Path
from dataclasses import dataclass
from typing import Tuple
import inquirer

@dataclass
class ProjectConfig:
    project_name: str
    template_dir: Path
    instances_dir: Path
    db_user: str
    password: str
    admin_email: str
    postgres_container_name: str
    pgadmin_container_name: str

def get_project_config_from_inquirer() -> ProjectConfig:
    questions = [
        inquirer.Text('project_name', message="What's your project name?"),
        inquirer.Text('admin_email', message="What's the admin email?"),
        inquirer.Password('password', message="Enter your password"),
    ]
    answers = inquirer.prompt(questions)

    return generate_project_config(
        answers['project_name'], answers['admin_email'], answers['password']
    )

def generate_project_config(project_name: str, admin_email: str, password: str) -> ProjectConfig:
    template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    instances_dir = Path(__file__).parent.parent.parent.parent / "instances"
    db_user = f"{project_name}-db-user"
    postgres_container_name = f"{project_name}-postgres"
    pgadmin_container_name = f"{project_name}-pgadmin"

    return ProjectConfig(
        project_name=project_name,
        template_dir=template_dir,
        instances_dir=instances_dir,
        db_user=db_user,
        admin_email=admin_email,
        password=password,
        postgres_container_name=postgres_container_name,
        pgadmin_container_name=pgadmin_container_name
    )
