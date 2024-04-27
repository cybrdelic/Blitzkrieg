from sqlalchemy.orm import Session
from ..models.project import Project
from ..crud.project_crud import ProjectCRUD

class ProjectService:
    @staticmethod
    def create_project(
        session: Session,
        id: {'str'},
        name: {'str'},
        description: {'str'},
        github_repo: {'str'},
        directory_path: {'str'},
        is_deployed: {'str'},
        deployment_date: {'str'},
        pip_package_name: {'str'},
        parent_id: {'str'}
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
    def get_next_index(session: Session):
        return ProjectCRUD.get_next_index(session)

    @staticmethod
    def get_project_by_name(session: Session, project_name: str):
        return ProjectCRUD.get_project_by_name(session, project_name)
