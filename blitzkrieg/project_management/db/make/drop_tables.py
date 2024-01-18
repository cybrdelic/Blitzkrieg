from blitzkrieg.project_management.db.connection import get_db_engine
from blitzkrieg.project_management.db.models.Base import Base

engine = get_db_engine()

# drop all tables in the database
Base.metadata.drop_all(bind=engine)
