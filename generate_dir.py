import os

# Define the directory structure
directory_structure = {
        'blitzkrieg': {
            'cli': {
                'parsing': {
                    '__init__.py': None,
                    'parser_manager.py': None
                },
                'ui.py': None,
                'user_input.py': None
            },
            'config': {
                '__init__.py': None,
                'settings.py': None
            },
            'core': {
                'initializers': {
                    '__init__.py': None,
                    'pgadmin_initializer.py': None
                },
                'managers': {
                    '__init__.py': None,
                    'docker_manager.py': None,
                    'postgres_manager.py': None
                },
                'shared': {
                    '__init__.py': None,
                    'command_runner.py': None
                }
            },
            '__init__.py': None,
            'main.py': None
        },
        'tests': {
            '__init__.py': None,
            'test_cli.py': None,
            'test_core.py': None
        },
}

# Function to create directories and files
def create_structure(base_path, structure):
    for name, content in structure.items():
        new_path = os.path.join(base_path, name)
        if content is None:
            # Create a file
            with open(new_path, 'w') as f:
                pass
        else:
            # Create a directory
            os.makedirs(new_path, exist_ok=True)
            create_structure(new_path, content)

# Create the directory structure
create_structure('.', directory_structure)
