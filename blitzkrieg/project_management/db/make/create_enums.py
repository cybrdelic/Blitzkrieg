import os
import importlib.util
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import ENUM

from blitzkrieg.project_management.db.connection import get_db_engine

engine = get_db_engine()

# Get the path of the enums/enums folder
enums_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'enums', 'project_management')

# Get all the .py files in the enums/enums folder
enum_files = [f for f in os.listdir(enums_path) if f.endswith('.py') and f != '__init__.py']

# Create a metadata object
metadata = MetaData(schema='project_management')
for enum_file in enum_files:
    # Get the full path of the enum file
    enum_file_path = os.path.join(enums_path, enum_file)

    # Load the enum module
    spec = importlib.util.spec_from_file_location(enum_file[:-3], enum_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the enum class from the module
    enum_class = getattr(module, 'DeploymentType')

    # Create the enum in the database
    enum_type = ENUM(*enum_class.__members__.keys(), name=enum_class.__name__.lower(), create_type=False, metadata=metadata)
    enum_type.create(engine, checkfirst=True)
