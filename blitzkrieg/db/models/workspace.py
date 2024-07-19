from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from blitzkrieg.db.models.base import Base


class Workspace(Base):
    __tablename__ = 'workspace'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    pgadmin_port = Column(String)
    pgadmin_username = Column(String)
    pgadmin_password = Column(String)
    postgres_port = Column(String)
    postgres_username = Column(String)
    postgres_host = Column(String)
    postgres_db = Column(String)
    postgres_password = Column(String)
    description = Column(String)
    project_id = Column(UUID, ForeignKey('project_management.project.id'))
    path = Column(String)
    sqlalchemy_uri = Column(String)

    project = relationship('Project')
