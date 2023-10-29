from pathlib import Path
from dataclasses import dataclass
from typing import Tuple

@dataclass
class ProjectConfig:
    project_name: str
    template_dir: Path
    instances_dir: Path
    db_user: str
    password: str
    admin_email: str
    password: str
    postgres_container_name: str
    pgadmin_container_name: str

def generate_project_config() -> ProjectConfig:
    email, password, project_name = get_project_config_input()

    # The template directory is hardcoded here, but could also be read from an env var
    template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    instances_dir = Path(__file__).parent.parent.parent.parent / "instances"

    # Generate a random DB username
    db_user = f"{project_name}-db-user"

    postgres_container_name = f"{project_name}-postgres"
    pgadmin_container_name = f"{project_name}-pgadmin"

    return ProjectConfig(
        project_name=project_name,
        template_dir=template_dir,
        instances_dir=instances_dir,
        db_user=db_user,
        admin_email=email,
        password=password,
        postgres_container_name=postgres_container_name,
        pgadmin_container_name=pgadmin_container_name
    )

def get_project_config_input() -> Tuple[str, str, str]:
    project_name = input("Enter a project name: ")
    email = input("Enter an email: ")
    password = input("Enter a password: ")

    return email, password, project_name
