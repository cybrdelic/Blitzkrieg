
from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.project import Project
class ProjectCRUD:
    @staticmethod
    def create_project(session: Session, project: Project):
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    @staticmethod
    def get_project_by_id(session: Session, project_id: int):
        return session.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Project).all()

    @staticmethod
    def get_all_paginated_project(session: Session, page: int, per_page: int):
        return session.query(Project).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_project(session: Session, project: Project):
        session.merge(project)
        session.commit()
        return project

    @staticmethod
    def delete_project(session: Session, project_id: int):
        project = session.query(Project).filter(Project.id == project_id).first()
        if project:
            session.delete(project)
            session.commit()
        return project

    @staticmethod
    def get_next_index(session: Session):
        project = session.query(Project).order_by(Project.index.desc()).first()
        if project:
            return project.index + 1
        else:
            return 1


from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.project import Project
class ProjectCRUD:
    @staticmethod
    def create_project(session: Session, project: Project):
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    @staticmethod
    def get_project_by_id(session: Session, project_id: int):
        return session.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Project).all()

    @staticmethod
    def get_all_paginated_project(session: Session, page: int, per_page: int):
        return session.query(Project).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_project(session: Session, project: Project):
        session.merge(project)
        session.commit()
        return project

    @staticmethod
    def delete_project(session: Session, project_id: int):
        project = session.query(Project).filter(Project.id == project_id).first()
        if project:
            session.delete(project)
            session.commit()
        return project

    @staticmethod
    def get_next_index(session: Session):
        project = session.query(Project).order_by(Project.index.desc()).first()
        if project:
            return project.index + 1
        else:
            return 1

    @staticmethod
    def get_project_by_name(session: Session, project_name: str):
        return session.query(Project).filter(Project.name == project_name).first()
