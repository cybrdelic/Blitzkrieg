from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from blitzkrieg.project_management.db.models.Base import Base
class Project(Base):
    __tablename__ = 'project'
    __table_args__ = {'schema': 'project_management'}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    github_repo = Column(String)  # GitHub repository URL
    directory_path = Column(String)  # Path to the project directory
    is_deployed = Column(Boolean, default=False)  # Whether the project is deployed
    deployment_date = Column(DateTime)  # The date and time of deployment
    pip_package_name = Column(String)  # The name of the pip package
    parent_id = Column(Integer, ForeignKey('project_management.project.id'))  # ID of the parent project

    # Relationship to self to allow nested projects
    children = relationship('Project', backref='parent', remote_side=[id])

    # Assuming a project can have multiple tasks
    tasks = relationship("Task", back_populates="project")
    deployments = relationship("Deployment", back_populates="project")
    issues = relationship('Issue', back_populates='project')
