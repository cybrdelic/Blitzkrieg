from sqlalchemy import create_engine, MetaData, Integer, String, Boolean, Float, DateTime
import os
from colorama import Fore, Style
from halo import Halo
import textwrap

from blitzkrieg.project_management.db.connection import get_db_engine

# Mapping from SQLAlchemy types to Python types
type_mapping = {
    Integer: 'int',
    String: 'str',
    Boolean: 'bool',
    Float: 'float',
    DateTime: 'datetime.datetime'
    # Add more types as needed
}

print(Fore.RESET + "Connecting to the database..." + Style.RESET_ALL)
engine = get_db_engine()

print(Fore.RESET + "Reflecting tables from the database..." + Style.RESET_ALL)
metadata = MetaData()
metadata.reflect(bind=engine, schema="project_management")

print(Fore.RESET + f"Found {len(metadata.tables)} tables." + Style.RESET_ALL)

spinner = Halo(text='Generating services', spinner='dots')
spinner.start()

for table in metadata.tables.values():
    with open(f"{table.name}_service.py", "w") as file:
        class_name = table.name.capitalize()
        python_type = {type_mapping.get(type(column.type), 'str') for column in table.columns}
        parameters = ",\n".join(f"{column.name}: {python_type}" for column in table.columns)
        parameters = textwrap.indent(parameters, ' ' * 8)  # Indent each line in parameters
        attributes = ", ".join(f"{column.name}={column.name}" for column in table.columns)

        # get model_name as table.name.lower() with the s at the end removed if it exitst
        model_name = table.name.lower().rstrip('s')

        file.write(textwrap.dedent(f"""\
from sqlalchemy.orm import Session
from ..models.{model_name} import {model_name.capitalize()}
from ..crud.{model_name}_crud import {model_name.capitalize()}CRUD

class {model_name.capitalize()}Service:
    @staticmethod
    def create_{model_name}(
        session: Session,
{parameters}
    ):
        {table.name.lower()} = {model_name.capitalize()}(
            {attributes}
        )
        return {model_name.capitalize()}CRUD.create_{table.name.lower()}(session, {table.name.lower()})

    @staticmethod
    def get_{table.name.lower()}(
        session: Session,
        {table.name.lower()}_id: int
    ):
        return {model_name.capitalize()}CRUD.get_{table.name.lower()}(session, {table.name.lower()}_id)

    @staticmethod
    def get_all_{table.name.lower()}s(session: Session):
        return {model_name.capitalize()}CRUD.get_all_{table.name.lower()}s(session)

    @staticmethod
    def get_next_index(session: Session):
        return {model_name.capitalize()}CRUD.get_next_index(session)
            """))
# Add similar static methods for update, delete, etc.
print(Fore.RESET + f"Service for {table.name} generated successfully." + Style.RESET_ALL)
# Add similar static methods for update, delete, etc.

spinner.stop()
print(Fore.GREEN + "All services generated successfully." + Style.RESET_ALL)
