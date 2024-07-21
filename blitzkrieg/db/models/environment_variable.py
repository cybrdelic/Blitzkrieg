from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from blitzkrieg.db.models.base import Base

class EnvironmentVariable(Base):
    __tablename__ = 'environment_variable'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    value = Column(String)
    workspace_id = Column(UUID, ForeignKey('project_management.workspace.id'))

    workspace = relationship('Workspace')
