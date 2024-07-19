from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

def get_db_engine():
    engine = create_engine('postgresql+psycopg2://alexfigueroa-db-user:pw@localhost:5432/alexfigueroa')
    return engine

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
