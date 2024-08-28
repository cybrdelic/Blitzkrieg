from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from blitzkrieg.db.models.project import Project

def get_db_engine():
    engine = create_engine('postgresql+psycopg2://alexfigueroa-db-user:pw@localhost:5432/alexfigueroa')
    return engine

def get_docker_db_engine():
    engine = create_engine('postgresql+psycopg2://alexfigueroa-db-user:pw@host.docker.internal:5432/alexfigueroa')
    return engine

def get_docker_db_session():
    engine = get_docker_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def close_db_session(session):
    if session:
        session.close()

def execute_db_operation(engine, operation):
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text(operation))
            trans.commit()
        except SQLAlchemyError as e:
            trans.rollback()
            print(f"An error occurred in execute_db_operation: {e}")

def get_project_by_name(project_name, session):
    project = session.query(Project).filter(Project.name == project_name).first()
    return project

def save_project(project, session):
    session.add(project)
    session.commit()
