#!/bin/bash

# Fail on any error and print each command as it's executed
set -ex

# Redirect stderr to stdout
exec 2>&1

echo "Navigating to the application directory"
cd /app

echo "Listing contents of /app"
ls -la /app

echo "Creating sqlalchemy_models directory"
mkdir -p /app/sqlalchemy_models

echo "Initializing Alembic"
alembic init migrations

echo "Listing contents of /app after Alembic initialization"
ls -la /app

echo "Showing the contents of the migrations/env.py file"
cat /app/migrations/env.py

echo "Setting permissions for directories"
chown -R 1000:1000 /app/migrations
chmod -R 775 /app/migrations
chown -R 1000:1000 /app
chmod -R 775 /app


echo "Listing contents of /app after setting permissions"
ls -la /app

echo "Updating alembic.ini with correct database URL"
sed -i "s|^sqlalchemy.url = .*|sqlalchemy.url = postgresql+psycopg2://$*workspace_name*$-db-user:pw@$*workspace_name*$-postgres:5432/$*workspace_name*$|g" /app/alembic.ini

echo "Creating env.py file..."
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
    print("Attempting to create schema: project_management")
    connection.execute(text('CREATE SCHEMA IF NOT EXISTS project_management'))
    connection.commit()
    print('Created schema: project_management')

def run_migrations_offline():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(url)
    with connectable.connect() as connection:
        create_schemas(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=lambda obj, name, type_, reflected, compare_to: obj.schema != 'public' if type_ == 'table' else True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    print('Running migrations offline...')
    run_migrations_offline()
else:
    print('Running migrations online...')
    run_migrations_online()
EOL

echo "env.py file created. Contents:"
cat /app/env.py

echo "Copying env.py to migrations directory..."
rm -f /app/migrations/env.py
cp /app/env.py /app/migrations/env.py

echo "Verifying env.py copy..."
if cmp -s /app/env.py /app/migrations/env.py; then
    echo "env.py successfully copied to migrations directory"
else
    echo "Failed to copy env.py to migrations directory"
    exit 1
fi

echo "Contents of /app/migrations/env.py:"
cat /app/migrations/env.py

echo "Running initial migration..."
alembic revision --autogenerate -m "initial migration"

echo "Upgrading to head..."
alembic upgrade head

echo "Setting permissions for directories"
chown -R 1000:1000 /app/migrations/__pycache__ || true
chmod -R 775 /app/migrations/__pycache__ || true
chown -R 1000:1000 /app/sqlalchemy_models/__pycache__ || true
chmod -R 775 /app/sqlalchemy_models/__pycache__ || true
chmod -R 1000:1000 /app/migrations/versions || true
chmod -R 775 /app/migrations/versions || true

echo "Script completed successfully"
