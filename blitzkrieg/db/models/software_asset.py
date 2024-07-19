from sqlalchemy import UUID, Column, ForeignKey, String
from blitzkrieg.db.models.base import Base
from sqlalchemy.orm import relationship


class SoftwareAsset(Base):
    __tablename__ = 'software_asset'
    __table_args__ = {'schema': 'project_management'}

    id = Column(UUID, primary_key=True)
    name = Column(String)
    purpose = Column(String)
    project_id = Column(UUID, ForeignKey('project_management.project.id'))

    project = relationship('Project')
