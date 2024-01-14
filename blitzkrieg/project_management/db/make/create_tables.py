from blitzkrieg.project_management.db.models.project import Base
from blitzkrieg.project_management.db.connection import get_db_engine, get_db_session, close_db_session
from sqlalchemy import DDL

def create_tables(session):
    session.execute(DDL("CREATE SCHEMA IF NOT EXISTS project_management"))
    Base.metadata.create_all(session.get_bind())
session = get_db_session()
create_tables(session)
close_db_session(session)
