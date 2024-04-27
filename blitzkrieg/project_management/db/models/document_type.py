import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from blitzkrieg.project_management.db.models.Base import Base

class DocumentType(Base):
    __tablename__ = 'document_type'
    __table_args__ = {'schema': 'document_management'}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())

    def __repr__(self):
        return f"<DocumentType(id={self.id}, name={self.name}, description={self.description}, created_at={self.created_at}, updated_at={self.updated_at})>"
