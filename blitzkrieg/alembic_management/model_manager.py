from typing import Dict, List, Optional, TypedDict
from blitzkrieg.ui_management.ConsoleInterface import ConsoleInterface

class ColumnDefinition(TypedDict):
    column_name: str
    column_type: str
    nullable: bool
    default: Optional[str]
    is_foreign_key: Optional[bool]
    foreign_key_model_and_schema: Optional[str]

class RelationshipDefinition(TypedDict):
    relationship_name: str
    relationship_type: str
    related_table: str
    related_column: str

class ModelDefinition(TypedDict):
    model_name: str
    schema_name: str
    column_definitions: List[ColumnDefinition]
    relationship_definitions: List[RelationshipDefinition]

class ModelManager:
    def __init__(self, console: ConsoleInterface, workspace_name: str):
        self.console: ConsoleInterface = console
        self.workspace_name: str = workspace_name
        self.model_name: Optional[str] = None
        self.schema_name: Optional[str] = None
        self.column_definitions: List[ColumnDefinition] = []
        self.relationship_definitions: List[RelationshipDefinition] = []

    def create_model(self, model_definition: ModelDefinition) -> None:
        table_name = model_definition.get('model_name')
        schema_name = model_definition.get('schema_name')
        column_definitions = model_definition.get('column_definitions')
        relationship_definitions = model_definition.get('relationship_definitions')

        self.console.handle_wait(f"Creating model for table {table_name} in schema {schema_name}...")
        self.set_model_name(table_name)
        self.set_schema_name(schema_name)
        self.set_column_definitions(column_definitions)
        self.set_relationship_definitions(relationship_definitions if relationship_definitions else [])
        model_file_path = f"{self.workspace_name}/sqlalchemy_models/{table_name}.py"
        model_data = self.generate_model_file_data()
        self.write_to_model_file(model_file_path, model_data)
        self.write_base_model_file()

        self.console.handle_success(f"Model created successfully at {model_file_path}")

    def set_relationship_type(self, relationship_type: str) -> None:
        if relationship_type not in ['one_to_one', 'one_to_many', 'many_to_one', 'many_to_many', 'nested']:
            self.console.handle_error(f"Invalid relationship type: {relationship_type}")
            return
        self.relationship_definitions.append({'relationship_type': relationship_type})

    def set_model_name(self, model_name: str) -> None:
        self.model_name = model_name

    def set_schema_name(self, schema_name: str) -> None:
        self.schema_name = schema_name

    def set_column_definitions(self, column_definitions: List[ColumnDefinition]) -> None:
        for column in column_definitions:
            if not self.verify_column_definition(column):
                return
        self.column_definitions = column_definitions

    def set_relationship_definitions(self, relationship_definitions: List[RelationshipDefinition]) -> None:
        for relationship in relationship_definitions:
            if not self.verify_relationship_definition(relationship):
                return
        self.relationship_definitions = relationship_definitions

    def ensure_camelcase(self, string: str) -> str:
        return string.replace('_', ' ').title().replace(' ', '')

    def verify_column_definition(self, column_definition: ColumnDefinition) -> bool:
        required_keys = ['column_name', 'column_type', 'nullable']
        for key in required_keys:
            if key not in column_definition:
                self.console.handle_error(f"Column definition must contain a {key} key")
                return False
        if column_definition.get('is_foreign_key') and 'foreign_key_model_and_schema' not in column_definition:
            self.console.handle_error("Column definition must contain a foreign_key_model_and_schema key if it is a foreign key")
            return False
        self.console.handle_info(f"Column definition for {column_definition['column_name']} verified successfully.")
        return True

    def verify_relationship_definition(self, relationship_definition: RelationshipDefinition) -> bool:
        required_keys = ['relationship_name', 'relationship_type', 'related_table', 'related_column']
        for key in required_keys:
            if key not in relationship_definition:
                self.console.handle_error(f"Relationship definition must contain a {key} key")
                return False
        self.console.handle_info(f"Relationship definition for {relationship_definition['relationship_name']} verified successfully.")
        return True

    def generate_import_lines(self) -> str:
        return (
            "from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum, func\n"
            "from sqlalchemy.orm import relationship\n"
            "import sys\n"
            "import os\n"
            "import datetime\n\n"
            "sys.path.append(os.path.realpath(os.path.dirname(__file__)))\n\n"
            "project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\n"
            "sys.path.append(project_dir)\n"
            f"from sqlalchemy_models.base import Base\n\n"
        )

    def generate_column_line(self, column: ColumnDefinition) -> str:
        default = column.get('default')
        is_primary_key = column.get('column_name') == 'id'


        if column.get('is_foreign_key'):
            return f"    {column['column_name']} = Column({column['column_type']}, ForeignKey('{column['foreign_key_model_and_schema']}'))\n"

        if is_primary_key:
            return f"    {column['column_name']} = Column({column['column_type']}, primary_key=True)\n"

        if default:
            return f"    {column['column_name']} = Column({column['column_type']}, nullable={column['nullable']}, default={column['default']})\n"
        else:
            return f"    {column['column_name']} = Column({column['column_type']}, nullable={column['nullable']})\n"

    def generate_relationship_line(self, relationship: RelationshipDefinition) -> str:
        related_table = self.ensure_camelcase(relationship['related_table'])
        if relationship['relationship_type'] == 'one_to_one':
            return f"    {relationship['relationship_name']} = relationship('{related_table}', back_populates='{relationship['related_column']}')\n"
        elif relationship['relationship_type'] == 'one_to_many':
            return f"    {relationship['relationship_name']} = relationship('{related_table}', back_populates='{relationship['related_column']}', uselist=True)\n"
        elif relationship['relationship_type'] == 'many_to_one':
            return f"    {relationship['relationship_name']} = relationship('{related_table}', back_populates='{relationship['related_column']}')\n"
        elif relationship['relationship_type'] == 'many_to_many':
            return f"    {relationship['relationship_name']} = relationship('{related_table}', back_populates='{relationship['related_column']}', uselist=True)\n"
        elif relationship['relationship_type'] == 'nested':
            return f"    {relationship['relationship_name']} = relationship('{related_table}', back_populates='{relationship['related_column']}')\n"

    def generate_class_definition_line(self, table_name: str) -> str:
        return f"class {self.ensure_camelcase(table_name)}(Base):\n"

    def generate_table_name_line(self, table_name: str) -> str:
        return f"    __tablename__ = '{table_name}'\n"

    def generate_schema_name_line(self, schema_name: str) -> str:
        return f"    __table_args__ = {{'schema': '{schema_name}'}}\n"

    def generate_model_file_data(self) -> str:
        model_data = self.generate_import_lines()
        model_data += self.generate_class_definition_line(self.model_name)
        model_data += self.generate_table_name_line(self.model_name)
        if self.schema_name:
            model_data += self.generate_schema_name_line(self.schema_name)
        else:
            self.console.handle_error("Must provide a schema name for the model")
        for column_definition in self.column_definitions:
            model_data += self.generate_column_line(column_definition)
        for relationship_definition in self.relationship_definitions:
            model_data += self.generate_relationship_line(relationship_definition)
        return model_data

    def write_to_model_file(self, model_file_path: str, data: str) -> None:
        with open(model_file_path, 'w') as model_file:
            model_file.write(data)
        self.console.handle_success(f"Model updated successfully at {model_file_path}")

    def write_base_model_file(self) -> None:
        base_model_path = f"{self.workspace_name}/sqlalchemy_models/base.py"
        import_declaration = "from sqlalchemy.orm import declarative_base\n\n"
        base_assignment = "Base = declarative_base()\n"
        metadata_assignment = "metadata = Base.metadata\n"
        with open(base_model_path, 'w') as base_model_file:
            base_model_file.write(import_declaration)
            base_model_file.write(base_assignment)
            base_model_file.write(metadata_assignment)
