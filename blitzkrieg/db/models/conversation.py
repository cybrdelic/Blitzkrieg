from blitzkrieg.db.models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String, UUID
import uuid

class Conversation(Base):
    __tablename__ = 'conversation'
    __table_args__ = {'schema': 'project_management'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
