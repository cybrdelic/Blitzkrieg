from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from blitzkrieg.project_management.db.models.Base import Base
class Task(Base):
    __tablename__ = 'task'
    __table_args__ = {'schema': 'project_management'}

    id = Column(Integer, primary_key=True)
    description = Column(String)
    project_id = Column(Integer, ForeignKey('project_management.project.id'))
    is_completed = Column(Boolean, default=False)  # Whether the task is completed
    completion_date = Column(DateTime)  # The date and time of task completion

    project = relationship("Project", back_populates="tasks")
