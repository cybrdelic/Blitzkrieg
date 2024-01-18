from sqlalchemy.orm import Session
from ..models.deployment import Deployment
from ..crud.deployment_crud import DeploymentCRUD

class DeploymentService:
    @staticmethod
    def create_deployment(
        session: Session,
        id: {'str'},
        project_id: {'str'},
        deployment_date: {'str'},
        type: {'str'}
    ):
        deployment = Deployment(
            id=id, project_id=project_id, deployment_date=deployment_date, type=type
        )
        return DeploymentCRUD.create_deployment(session, deployment)

    @staticmethod
    def get_deployment(
        session: Session,
        deployment_id: int
    ):
        return DeploymentCRUD.get_deployment(session, deployment_id)

    @staticmethod
    def get_next_index(session: Session):
        return DeploymentCRUD.get_next_index(session)
