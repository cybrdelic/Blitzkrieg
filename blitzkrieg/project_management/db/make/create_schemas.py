from blitzkrieg.db.connection import get_db_engine, get_db_session, execute_db_operation

def create_schemas():
    return "CREATE SCHEMA IF NOT EXISTS project_management"

engine = get_db_engine()
execute_db_operation(engine, create_schemas())
