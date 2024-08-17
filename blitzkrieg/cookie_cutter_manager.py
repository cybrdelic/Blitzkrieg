import os
from cookiecutter.main import cookiecutter
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager

class CookieCutterManager:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.blitz_env_manager = blitz_env_manager

    def generate_project(self, project_name, template_path, description):
        try:
            console.handle_info(f"Inside of generate_project... project_name: {project_name}, template_path: {template_path}, description: {description}. About to fetch active workspace dir.")
            workspace_dir = self.blitz_env_manager.get_active_workspace_dir()
            console.handle_info(f"Active workspace dir: {workspace_dir}")
            console.handle_info(f"About to generate project using cookiecutter... ")
            cookiecutter(
                template_path,
                no_input=True,
                extra_context={
                    'project_name': project_name,
                    'project_slug': project_name.lower().replace(' ', '_'),
                    'project_description': description,
                    'author_name': self.blitz_env_manager.get_global_env_var('NAME') or 'Your Name',
                    'author_email': self.blitz_env_manager.get_global_env_var('EMAIL') or 'your.email@example.com',
                },
                output_dir=workspace_dir
            )
            console.handle_success(f"Generated project {project_name} at {workspace_dir} with the slug {project_name.lower().replace(' ', '_')}")
        except Exception as e:
            self.console.handle_error(f"Failed to generate project: {str(e)}")

    def get_template_path(self, project_type):
        project_type_template_name_mapper = {
            'cli': 'poetry-cli-template',
            'lib': 'poetry-lib-template'
        }
        template_name = project_type_template_name_mapper.get(project_type)
        if not template_name:
            raise ValueError(f"Invalid project type: {project_type}")
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template for {project_type} projects not found. Please ensure the template exists at {template_path}")
        return template_path
