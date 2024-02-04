from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.base import Base
class BaseCRUD:
    @staticmethod
    def create_base(session: Session, base: Base):
        session.add(base)
        session.commit()
        session.refresh(base)
        return base

    @staticmethod
    def create_bases(session: Session, bases: list):
        session.add_all(bases)
        session.commit()
        return bases

    @staticmethod
    def get_base_by_id(session: Session, base_id: int):
        return session.query(Base).filter(Base.id == base_id).first()

    @staticmethod
    def get_bases_by_ids(session: Session, base_ids: list):
        return session.query(Base).filter(Base.id.in_(base_ids)).all()

    @staticmethod
    def get_base_by_index(session: Session, base_index: int):
        return session.query(Base).filter(Base.index == base_index).first()

    @staticmethod
    def get_bases_by_indices(session: Session, base_indices: list):
        return session.query(Base).filter(Base.index.in_(base_indices)).all()

    @staticmethod
    def get_all_bases(session: Session):
        return session.query(Base).all()

    @staticmethod
    def get_all_paginated_bases(session: Session, page: int, per_page: int):
        return session.query(Base).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def get_base_with_relations(session: Session, base_id: int, relations: list):
        query = session.query(Base).options(joinedload(*relations))
        return query.filter(Base.id == base_id).first()

    @staticmethod
    def get_bases_with_relations(session: Session, base_ids: list, relations: list):
        query = session.query(Base).options(joinedload(*relations))
        return query.filter(Base.id.in_(base_ids)).all()


    @staticmethod
    def update_base(session: Session, base: Base):
        session.merge(base)
        session.commit()
        return base

    @staticmethod
    def update_bases(session: Session, bases: list):
        session.bulk_update_mappings(Base, bases)
        session.commit()
        return bases

    @staticmethod
    def delete_base(session: Session, base_id: int):
        base = session.query(Base).filter(Base.id == base_id).first()
        if base:
            session.delete(base)
            session.commit()
        return base

    @staticmethod
    def delete_bases(session: Session, base_ids: list):
        bases = session.query(Base).filter(Base.id.in_(base_ids)).all()
        if bases:
            session.delete(bases)
            session.commit()
        return bases

    @staticmethod
    def get_next_index(session: Session):
        base = session.query(Base).order_by(Base.index.desc()).first()
        if base:
            return base.index + 1
        else:
            return 1