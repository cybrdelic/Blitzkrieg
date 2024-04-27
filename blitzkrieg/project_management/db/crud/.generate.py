import os
import importlib.util
from blitzkrieg.project_management.db.models.Base import Base
models_dir = '../models'  # replace with the path to your models directory
crud_template = """
from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.{model_name} import {model_class}
class {model_class}CRUD:
    @staticmethod
    def create_{model_name}(session: Session, {model_name}: {model_class}):
        session.add({model_name})
        session.commit()
        session.refresh({model_name})
        return {model_name}

    @staticmethod
    def get_{model_name}_by_id(session: Session, {model_name}_id: int):
        return session.query({model_class}).filter({model_class}.id == {model_name}_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query({model_class}).all()

    @staticmethod
    def get_all_paginated_{model_name}(session: Session, page: int, per_page: int):
        return session.query({model_class}).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_{model_name}(session: Session, {model_name}: {model_class}):
        session.merge({model_name})
        session.commit()
        return {model_name}

    @staticmethod
    def delete_{model_name}(session: Session, {model_name}_id: int):
        {model_name} = session.query({model_class}).filter({model_class}.id == {model_name}_id).first()
        if {model_name}:
            session.delete({model_name})
            session.commit()
        return {model_name}

    @staticmethod
    def get_next_index(session: Session):
        {model_name} = session.query({model_class}).order_by({model_class}.index.desc()).first()
        if {model_name}:
            return {model_name}.index + 1
        else:
            return 1

"""

for model_file in os.listdir(models_dir):
    try:
        if model_file.endswith('.py') and model_file != '__init__.py':
            model_name = model_file[:-3]  # remove .py extension
            crud_file_path = f'./{model_name}_crud.py'  # create a new CRUD file for each model

            with open(crud_file_path, 'w') as crud_file:
                spec = importlib.util.spec_from_file_location(model_name, os.path.join(models_dir, model_file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Base):  # replace Base with your base model class
                        model_class = attr
                        camel_case_model_name = ''.join([word.capitalize() for word in model_name.split('_')])
                        crud_class = crud_template.format(model_class=camel_case_model_name,
                                                          model_name=model_name)
                        crud_file.write(crud_class)
    except Exception as e:
        print(f"An error occurred while processing {model_file}: {e}")
