#!/bin/bash

# Fail on any error
set -e

# Navigate to the application directory
cd /app

# List the contents of /app
ls -la /app

# Create necessary directories
mkdir -p /app/sqlalchemy_models

# Initialize Alembic
alembic init migrations
ls -la /app

# Ensure the correct permissions for the migrations directory
chown -R 1000:1000 /app/migrations
chmod -R 775 /app/migrations

ls -la /app

# replace env.py at /app/migrations/env.py with the one from /app/env.py
cp /app/env.py /app/migrations/env.py

# Update alembic.ini with the correct database URL
sed -i "s|^sqlalchemy.url = .*|sqlalchemy.url = postgresql+psycopg2://$*workspace_name*$-db-user:pw@$*workspace_name*$-postgres:5432/$*workspace_name*$|g" /app/alembic.ini

# Create necessary migration files
cat <<EOL > /app/env.py
from sqlalchemy import create_engine, text
from alembic import context
import os
import sys
import importlib.util

sys.path.append(".")

def load_models():
    models_path = os.path.join('sqlalchemy_models')
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(models_path, filename))
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)

load_models()

from sqlalchemy_models.base import Base

metadata = Base.metadata
for cls in Base.__subclasses__():
    cls.__table__.metadata = metadata

url = 'postgresql+psycopg2://$*workspace_name*$-db-user:pw@$*workspace_name*$-postgres:5432/$*workspace_name*$'
config = context.config
config.set_main_option('sqlalchemy.url', url)

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
EOL

# Run initial migration
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
