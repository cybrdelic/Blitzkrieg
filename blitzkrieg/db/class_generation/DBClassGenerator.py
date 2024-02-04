import os
import importlib.util
from jinja2 import Environment, FileSystemLoader

class DBClassGenerator:
    def __init__(self, models_dir='./models', templates_dir='./templates'):
        self.models_dir = os.path.abspath(models_dir)
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        self.crud_dir = './blitzkrieg/db/crud/'
        os.makedirs(self.crud_dir, exist_ok=True)  # Create the CRUD directory if it does not exist


    def generate_for_all_models(self):
        for model_file in self._get_model_files():
            model_name = self._extract_model_name(model_file)
            model_class = self._load_model_class(model_file, model_name)
            if model_class:
                self._generate_crud(model_name, model_class)
                # Add call to _generate_service if service generation is implemented

    def _get_model_files(self):
        return [f for f in os.listdir(self.models_dir) if f.endswith('.py') and f != '__init__.py']

    def _extract_model_name(self, filename):
        return filename[:-3]

    def _load_model_class(self, model_file, model_name):
        spec = importlib.util.spec_from_file_location(model_name, os.path.join(self.models_dir, model_file))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type):
                return attr
        return None

    def _generate_crud(self, model_name, model_class):
        camel_case_name = self._camel_case_model_name(model_name)
        plural_snake_case_name = self._pluralize_model_name(model_name.lower())
        rendered_template = self._render_template('crud_template.j2', model_name=model_name.lower(), model_class=camel_case_name, plural_model_name=plural_snake_case_name)

        self._save_rendered_template(f'{camel_case_name}CRUD.py', rendered_template, self.crud_dir)

    def _render_template(self, template_name, **context):
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _save_rendered_template(self, filename, content, save_dir):
        file_path = os.path.join(save_dir, filename)

        # Check if file already exists and is not empty
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            # Handle edge cases: overwrite, append, skip, or prompt the user
            action = input(f"File {filename} already exists and is not empty. Overwrite (o), append (a), or skip (s)? ").lower()
            if action == 'o':
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"Overwritten: {file_path}")
            elif action == 'a':
                with open(file_path, 'a') as f:
                    f.write(content)
                print(f"Appended to: {file_path}")
            elif action == 's':
                print(f"Skipped: {file_path}")
            else:
                print("Invalid input. Skipping operation.")
        else:
            # File does not exist or is empty, safe to write
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Generated: {file_path}")

    @staticmethod
    def _camel_case_model_name(name):
        return ''.join(word.capitalize() for word in name.split('_'))

    @staticmethod
    def _pluralize_model_name(name):
        return name + 's'

    # Implement _generate_service similarly to _generate_crud if needed

# Example usage
