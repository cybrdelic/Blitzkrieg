from blitzkrieg.project_management.db.enums.project_management.deployment_type_enum import DeploymentType
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from blitzkrieg.project_management.db.models.Base import Base
class Deployment(Base):
    __tablename__ = 'deployment'
    __table_args__ = {'schema': 'project_management'}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project_management.project.id'))
    deployment_date = Column(DateTime)  # The date and time of deployment
    type = Column(Enum(*DeploymentType.__members__.keys(), name="deployment_type"))

    project = relationship("Project", back_populates="deployments")
