from sqlalchemy import UUID, Column, DateTime, ForeignKey, String
from blitzkrieg.db.models.base import Base
from sqlalchemy.orm import relationship


class Feature(Base):
    __tablename__ = 'feature'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    description = Column(String)
    project_id = Column(UUID, ForeignKey('project_management.project.id'))
    implementation_date = Column(DateTime)

    project = relationship('Project')
