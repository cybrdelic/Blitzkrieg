from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()



    # Additional database interaction methods can be added here
