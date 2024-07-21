from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from blitzkrieg.db.models.base import Base

from sqlalchemy.dialects.postgresql import UUID


class Workspace(Base):
    __tablename__ = 'workspace'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    description = Column(String)
    path = Column(String)
