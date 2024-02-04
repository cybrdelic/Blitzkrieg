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
    def create_projects(session: Session, projects: list):
        session.add_all(projects)
        session.commit()
        return projects

    @staticmethod
    def get_project_by_id(session: Session, project_id: int):
        return session.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_projects_by_ids(session: Session, project_ids: list):
        return session.query(Project).filter(Project.id.in_(project_ids)).all()

    @staticmethod
    def get_project_by_index(session: Session, project_index: int):
        return session.query(Project).filter(Project.index == project_index).first()

    @staticmethod
    def get_projects_by_indices(session: Session, project_indices: list):
        return session.query(Project).filter(Project.index.in_(project_indices)).all()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Project).all()

    @staticmethod
    def get_all_paginated_projects(session: Session, page: int, per_page: int):
        return session.query(Project).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def get_project_with_relations(session: Session, project_id: int, relations: list):
        query = session.query(Project).options(joinedload(*relations))
        return query.filter(Project.id == project_id).first()

    @staticmethod
    def get_projects_with_relations(session: Session, project_ids: list, relations: list):
        query = session.query(Project).options(joinedload(*relations))
        return query.filter(Project.id.in_(project_ids)).all()


    @staticmethod
    def update_project(session: Session, project: Project):
        session.merge(project)
        session.commit()
        return project

    @staticmethod
    def update_projects(session: Session, projects: list):
        session.bulk_update_mappings(Project, projects)
        session.commit()
        return projects

    @staticmethod
    def delete_project(session: Session, project_id: int):
        project = session.query(Project).filter(Project.id == project_id).first()
        if project:
            session.delete(project)
            session.commit()
        return project

    @staticmethod
    def delete_projects(session: Session, project_ids: list):
        projects = session.query(Project).filter(Project.id.in_(project_ids)).all()
        if projects:
            session.delete(projects)
            session.commit()
        return projects

    @staticmethod
    def get_next_index(session: Session):
        project = session.query(Project).order_by(Project.index.desc()).first()
        if project:
            return project.index + 1
        else:
            return 1