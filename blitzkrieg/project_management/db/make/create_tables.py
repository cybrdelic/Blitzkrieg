import os
import glob
import importlib.util
import logging
from sqlalchemy import DDL
from sqlalchemy.exc import SQLAlchemyError
from blitzkrieg.project_management.db.models.Base import Base
from blitzkrieg.project_management.db.connection import close_db_session, get_db_session

logging.basicConfig(level=logging.INFO)

# Import all models
models_dir = '../models'
model_files = glob.glob(models_dir + '/*.py')

# Find the Project model and import it first
project_model_file = next((f for f in model_files if 'project.py' in f), None)
if project_model_file:
    model_files.remove(project_model_file)
    spec = importlib.util.spec_from_file_location("models", project_model_file)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)

# Import the rest of the models
for model_file in model_files:
    spec = importlib.util.spec_from_file_location("models", model_file)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)

session = get_db_session()

def create_tables(session):
    try:
        schema_name = "project_management"
        logging.info(f"Creating schema '{schema_name}'...")
        session.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        logging.info(f"Schema '{schema_name}' created successfully.")

        logging.info("Creating tables...")
        for table in Base.metadata.tables.values():
            logging.info(f"Creating table '{table.name}'..")
        logging.info("Tables created successfully.")
    except SQLAlchemyError as e:
        logging.error("An error occurred while creating tables: %s", e)

try:
    create_tables(session)
    logging.info("Operation completed successfully.")
except SQLAlchemyError as e:
    logging.error("An error occurred: %s", e)
finally:
    close_db_session(session)

create_tables(session)
