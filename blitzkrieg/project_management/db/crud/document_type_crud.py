
from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.document_type import DocumentType
class DocumentTypeCRUD:
    @staticmethod
    def create_document_type(session: Session, document_type: DocumentType):
        session.add(document_type)
        session.commit()
        session.refresh(document_type)
        return document_type

    @staticmethod
    def get_document_type_by_id(session: Session, document_type_id: int):
        return session.query(DocumentType).filter(DocumentType.id == document_type_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(DocumentType).all()

    @staticmethod
    def get_all_paginated_document_type(session: Session, page: int, per_page: int):
        return session.query(DocumentType).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_document_type(session: Session, document_type: DocumentType):
        session.merge(document_type)
        session.commit()
        return document_type

    @staticmethod
    def delete_document_type(session: Session, document_type_id: int):
        document_type = session.query(DocumentType).filter(DocumentType.id == document_type_id).first()
        if document_type:
            session.delete(document_type)
            session.commit()
        return document_type

    @staticmethod
    def get_next_index(session: Session):
        document_type = session.query(DocumentType).order_by(DocumentType.index.desc()).first()
        if document_type:
            return document_type.index + 1
        else:
            return 1


from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.document_type import DocumentType
class DocumentTypeCRUD:
    @staticmethod
    def create_document_type(session: Session, document_type: DocumentType):
        session.add(document_type)
        session.commit()
        session.refresh(document_type)
        return document_type

    @staticmethod
    def get_document_type_by_id(session: Session, document_type_id: int):
        return session.query(DocumentType).filter(DocumentType.id == document_type_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(DocumentType).all()

    @staticmethod
    def get_all_paginated_document_type(session: Session, page: int, per_page: int):
        return session.query(DocumentType).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_document_type(session: Session, document_type: DocumentType):
        session.merge(document_type)
        session.commit()
        return document_type

    @staticmethod
    def delete_document_type(session: Session, document_type_id: int):
        document_type = session.query(DocumentType).filter(DocumentType.id == document_type_id).first()
        if document_type:
            session.delete(document_type)
            session.commit()
        return document_type

    @staticmethod
    def get_next_index(session: Session):
        document_type = session.query(DocumentType).order_by(DocumentType.index.desc()).first()
        if document_type:
            return document_type.index + 1
        else:
            return 1

