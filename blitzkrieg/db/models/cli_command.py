from sqlalchemy import UUID, Column, ForeignKey, String
from blitzkrieg.db.models.base import Base
from sqlalchemy.orm import relationship

class CLICommand(Base):
    __tablename__ = 'cli_command'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    description = Column(String)
    command = Column(String)
    project_id = Column(UUID, ForeignKey('project_management.project.id'))
    purpose = Column(String)

    project = relationship('Project')
