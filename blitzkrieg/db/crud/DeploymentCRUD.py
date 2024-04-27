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
    def create_deployments(session: Session, deployments: list):
        session.add_all(deployments)
        session.commit()
        return deployments

    @staticmethod
    def get_deployment_by_id(session: Session, deployment_id: int):
        return session.query(Deployment).filter(Deployment.id == deployment_id).first()

    @staticmethod
    def get_deployments_by_ids(session: Session, deployment_ids: list):
        return session.query(Deployment).filter(Deployment.id.in_(deployment_ids)).all()

    @staticmethod
    def get_deployment_by_index(session: Session, deployment_index: int):
        return session.query(Deployment).filter(Deployment.index == deployment_index).first()

    @staticmethod
    def get_deployments_by_indices(session: Session, deployment_indices: list):
        return session.query(Deployment).filter(Deployment.index.in_(deployment_indices)).all()

    @staticmethod
    def get_all_deployments(session: Session):
        return session.query(Deployment).all()

    @staticmethod
    def get_all_paginated_deployments(session: Session, page: int, per_page: int):
        return session.query(Deployment).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def get_deployment_with_relations(session: Session, deployment_id: int, relations: list):
        query = session.query(Deployment).options(joinedload(*relations))
        return query.filter(Deployment.id == deployment_id).first()

    @staticmethod
    def get_deployments_with_relations(session: Session, deployment_ids: list, relations: list):
        query = session.query(Deployment).options(joinedload(*relations))
        return query.filter(Deployment.id.in_(deployment_ids)).all()


    @staticmethod
    def update_deployment(session: Session, deployment: Deployment):
        session.merge(deployment)
        session.commit()
        return deployment

    @staticmethod
    def update_deployments(session: Session, deployments: list):
        session.bulk_update_mappings(Deployment, deployments)
        session.commit()
        return deployments

    @staticmethod
    def delete_deployment(session: Session, deployment_id: int):
        deployment = session.query(Deployment).filter(Deployment.id == deployment_id).first()
        if deployment:
            session.delete(deployment)
            session.commit()
        return deployment

    @staticmethod
    def delete_deployments(session: Session, deployment_ids: list):
        deployments = session.query(Deployment).filter(Deployment.id.in_(deployment_ids)).all()
        if deployments:
            session.delete(deployments)
            session.commit()
        return deployments

    @staticmethod
    def get_next_index(session: Session):
        deployment = session.query(Deployment).order_by(Deployment.index.desc()).first()
        if deployment:
            return deployment.index + 1
        else:
            return 1