from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.project import Project
from blitzkrieg.project_management.db.crud.project_crud import ProjectCRUD

class ProjectService:
    @staticmethod
    def create_project(session: Session, name: str, description: str, github_repo: str, directory_path: str, is_deployed: bool, deployment_date: str, pip_package_name: str, parent_id: str):
        project = Project(
            name=name,
            description=description,
            github_repo=github_repo,
            directory_path=directory_path,
            is_deployed=is_deployed,
            deployment_date=deployment_date,
            pip_package_name=pip_package_name,
            parent_id=parent_id
        )
        return ProjectCRUD.create_project(session, project)

    @staticmethod
    def get_project(session: Session, project_id: int):
        return ProjectCRUD.get_project(session, project_id)

    # Add similar static methods for update, delete, etc.
