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
    def create_document_types(session: Session, document_types: list):
        session.add_all(document_types)
        session.commit()
        return document_types

    @staticmethod
    def get_document_type_by_id(session: Session, document_type_id: int):
        return session.query(DocumentType).filter(DocumentType.id == document_type_id).first()

    @staticmethod
    def get_document_types_by_ids(session: Session, document_type_ids: list):
        return session.query(DocumentType).filter(DocumentType.id.in_(document_type_ids)).all()

    @staticmethod
    def get_document_type_by_index(session: Session, document_type_index: int):
        return session.query(DocumentType).filter(DocumentType.index == document_type_index).first()

    @staticmethod
    def get_document_types_by_indices(session: Session, document_type_indices: list):
        return session.query(DocumentType).filter(DocumentType.index.in_(document_type_indices)).all()

    @staticmethod
    def get_all_document_types(session: Session):
        return session.query(DocumentType).all()

    @staticmethod
    def get_all_paginated_document_types(session: Session, page: int, per_page: int):
        return session.query(DocumentType).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def get_document_type_with_relations(session: Session, document_type_id: int, relations: list):
        query = session.query(DocumentType).options(joinedload(*relations))
        return query.filter(DocumentType.id == document_type_id).first()

    @staticmethod
    def get_document_types_with_relations(session: Session, document_type_ids: list, relations: list):
        query = session.query(DocumentType).options(joinedload(*relations))
        return query.filter(DocumentType.id.in_(document_type_ids)).all()


    @staticmethod
    def update_document_type(session: Session, document_type: DocumentType):
        session.merge(document_type)
        session.commit()
        return document_type

    @staticmethod
    def update_document_types(session: Session, document_types: list):
        session.bulk_update_mappings(DocumentType, document_types)
        session.commit()
        return document_types

    @staticmethod
    def delete_document_type(session: Session, document_type_id: int):
        document_type = session.query(DocumentType).filter(DocumentType.id == document_type_id).first()
        if document_type:
            session.delete(document_type)
            session.commit()
        return document_type

    @staticmethod
    def delete_document_types(session: Session, document_type_ids: list):
        document_types = session.query(DocumentType).filter(DocumentType.id.in_(document_type_ids)).all()
        if document_types:
            session.delete(document_types)
            session.commit()
        return document_types

    @staticmethod
    def get_next_index(session: Session):
        document_type = session.query(DocumentType).order_by(DocumentType.index.desc()).first()
        if document_type:
            return document_type.index + 1
        else:
            return 1