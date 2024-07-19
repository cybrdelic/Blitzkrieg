from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blitzkrieg.ui_management.decorators import with_spinner

class DatabaseManager:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    def get_db_uri(self):
        db_uri = f'postgresql+psycopg2://{self.db_user}:{self.db_password}@alexfigueroa-postgres:{self.db_port}/{self.db_name}'
        return db_uri

    def get_engine(self, db_uri):
        engine = create_engine(db_uri)
        return engine

    def get_session(self, engine):
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def create_schema(self, schema_name, engine):
        # creates schema
        with engine.connect() as connection:
            connection.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name}')







    # Additional database interaction methods can be added here
