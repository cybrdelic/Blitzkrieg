from sqlalchemy import String
from sqlalchemy.orm import Session

from ..crud.project_crud import ProjectCRUD
from ..models.project import Project

class ProjectService:
    @staticmethod
    def create_project(
        session: Session,
        id: String,
        name: String,
        description: String,
        github_repo: String,
        directory_path: String,
        is_deployed: String,
        deployment_date: String,
        pip_package_name: String,
        parent_id: String
    ):
        project = Project(
            id=id, name=name, description=description, github_repo=github_repo, directory_path=directory_path, is_deployed=is_deployed, deployment_date=deployment_date, pip_package_name=pip_package_name, parent_id=parent_id
        )
        return ProjectCRUD.create_project(session, project)

    @staticmethod
    def get_project(
        session: Session,
        project_id: int
    ):
        return ProjectCRUD.get_project(session, project_id)

    @staticmethod
    def get_project_by_name(
        session: Session,
        project_name: str
    ):
        return ProjectCRUD.get_project_by_name(session, project_name)

    @staticmethod
    def get_next_index(session: Session):
        return ProjectCRUD.get_next_index(session)
