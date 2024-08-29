import os
from cookiecutter.main import cookiecutter
import questionary
from blitzkrieg.db.models.project import Project
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.class_instances.blitz_env_manager import blitz_env_manager

class CookieCutterManager:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.blitz_env_manager = blitz_env_manager

    def generate_project(self, project: Project, template_path):
        try:
            project_name = project.name

            workspace_dir = self.blitz_env_manager.get_active_workspace_dir()
            workspace_projects_dir = os.path.join(workspace_dir, 'projects')

            template_context = self.get_template_context(project)
            cookiecutter(
                template_path,
                no_input=True,
                extra_context=template_context,
                output_dir=workspace_projects_dir
            )
            console.handle_success(f"Generated project {project_name} at {workspace_dir} with the slug {project_name.lower().replace(' ', '_')}")
        except Exception as e:
            console.handle_error(f"Failed to generate project: {str(e)}")

    def get_template_context(self, project: Project):
        project_type = project.project_type
        project_type = project_type.lower().replace(' ', '_')
        project_name = project.name
        project_description = project.description
        project_short_description = project.short_description

        project_type_template_name_mapper = {
            'python_cli': {
                'project_name': 'Python CLI',
                'project_slug': 'python_cli',
                'project_description': 'A Python CLI project',
                'author_name': 'Your Name',
                'author_email': ''
            },
            'pyo3_rust_extension': {
                # prompt the user for text input using questionary for project_name value
                'project_name': project_name,
                'project_slug': project_name.lower().replace(' ', '_'),
                'project_description': project_description,
                'full_name': 'Your Name',
                'email': '',
                'project_short_description': project_short_description,
                'github_username': 'alexfigueroa-solutions',


            }
        }
        return project_type_template_name_mapper.get(project_type)

    def get_template_path(self, project_type):
        # make project_type snake_case
        project_type = project_type.lower().replace(' ', '_')
        project_type_template_name_mapper = {
            'python_cli': 'poetry-cli-template',
            'pyo3_rust_extension': 'pyo3-rust-extension-template'
        }
        template_name = project_type_template_name_mapper.get(project_type)
        if not template_name:
            raise ValueError(f"Invalid project type: {project_type}")
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(template_path):
            error_message = f"Template for {project_type} projects not found. Please ensure the template exists at {template_path}"
            console.handle_error(error_message)
            raise FileNotFoundError(error_message)
        return template_path
