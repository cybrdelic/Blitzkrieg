from sqlalchemy import create_engine, text
from alembic import context
import os
import sys
import importlib.util

sys.path.append(".")

# Load all models dynamically
def load_models():
    models_path = os.path.join('sqlalchemy_models')
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(models_path, filename))
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)

load_models()

# Import the Base class after loading the models
from sqlalchemy_models.base import Base

# Reflect the metadata
metadata = Base.metadata
for cls in Base.__subclasses__():
    cls.__table__.metadata = metadata

url = '{self.db_manager.get_sqlalchemy_uri()}'
config = context.config
config.set_main_option('sqlalchemy.url', url)

from sqlalchemy_models.base import Base  # Replace 'myapp.models' with the actual path to your models
target_metadata = Base.metadata

def create_schemas(connection):
    connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS project_management'))
    connection.commit()  # Ensure the schema creation is committed
    print('Created schema: project_management')


def run_migrations_offline():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(url)
    with connectable.connect() as connection:
        create_schemas(connection)  # Create necessary schemas before running migrations
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
