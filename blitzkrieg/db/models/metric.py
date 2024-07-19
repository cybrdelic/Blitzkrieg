from sqlalchemy import UUID, Column, ForeignKey, String
from blitzkrieg.db.models.base import Base
from sqlalchemy.orm import relationship

class Metric(Base):
    __tablename__ = 'metric'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    description = Column(String)
    project_id = Column(UUID, ForeignKey('project_management.project.id'))
    formula = Column(String)
    input_parameters = Column(String)
    value = Column(String)

    project = relationship('Project')
