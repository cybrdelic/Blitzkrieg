# sql alchemy model for project issues called issues

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from blitzkrieg.project_management.db.models.Base import Base
class Issue(Base):
    __tablename__ = 'issues'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    project_id = Column(Integer, ForeignKey('projects.id'))

    project = relationship('Project', back_populates='issues')
