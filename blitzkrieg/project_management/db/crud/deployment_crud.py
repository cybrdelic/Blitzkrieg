
from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.deployment import Deployment
class DeploymentCRUD:
    @staticmethod
    def create_deployment(session: Session, deployment: Deployment):
        session.add(deployment)
        session.commit()
        session.refresh(deployment)
        return deployment

    @staticmethod
    def get_deployment_by_id(session: Session, deployment_id: int):
        return session.query(Deployment).filter(Deployment.id == deployment_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Deployment).all()

    @staticmethod
    def get_all_paginated_deployment(session: Session, page: int, per_page: int):
        return session.query(Deployment).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_deployment(session: Session, deployment: Deployment):
        session.merge(deployment)
        session.commit()
        return deployment

    @staticmethod
    def delete_deployment(session: Session, deployment_id: int):
        deployment = session.query(Deployment).filter(Deployment.id == deployment_id).first()
        if deployment:
            session.delete(deployment)
            session.commit()
        return deployment

    @staticmethod
    def get_next_index(session: Session):
        deployment = session.query(Deployment).order_by(Deployment.index.desc()).first()
        if deployment:
            return deployment.index + 1
        else:
            return 1


from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.deployment import Deployment
class DeploymentCRUD:
    @staticmethod
    def create_deployment(session: Session, deployment: Deployment):
        session.add(deployment)
        session.commit()
        session.refresh(deployment)
        return deployment

    @staticmethod
    def get_deployment_by_id(session: Session, deployment_id: int):
        return session.query(Deployment).filter(Deployment.id == deployment_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Deployment).all()

    @staticmethod
    def get_all_paginated_deployment(session: Session, page: int, per_page: int):
        return session.query(Deployment).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_deployment(session: Session, deployment: Deployment):
        session.merge(deployment)
        session.commit()
        return deployment

    @staticmethod
    def delete_deployment(session: Session, deployment_id: int):
        deployment = session.query(Deployment).filter(Deployment.id == deployment_id).first()
        if deployment:
            session.delete(deployment)
            session.commit()
        return deployment

    @staticmethod
    def get_next_index(session: Session):
        deployment = session.query(Deployment).order_by(Deployment.index.desc()).first()
        if deployment:
            return deployment.index + 1
        else:
            return 1

