import uuid
from faker import Faker
from blitzkrieg.project_management.db.connection import get_db_session, close_db_session
from blitzkrieg.project_management.db.services.project_service import ProjectService
import requests

scaleton_name = "scaleton"
scaleton = {
    "name": scaleton_name,
    "description": "An Open Source Project for Autonomous Scaleable CLI Scaffolding, Deployment, and Management",
}

projects = [
    {
        "name": "Scaleton",
        "description": "An Open Source Project for Autonomous Scaleable CLI Scaffolding, Deployment, and Management",
    },
    {
        "name": "Prozhyk",
        "description": "An Advanced Autonomous Project Management and Extrapolation Tool"
    },
    {
        "name": "Jjugg",
        "description": "An Innovative Game-Changing Autonomous System for Job Hunting and Career Management"
    },
    {
        "name": "Blitzkrieg",
        "description": "An Autonomous System for Rapid Postgres and PgAdmin Orchestration and Management"
    },
    {
        "name": "X1dra.AI",
        "description": "An Autonomous Code Contribution System"
    },
    {
        "name": "RuntimeSense",
        "description": "An Autonomous System for User Flow Exploration and Testing, based on Runtime Analysis"
    },
    {
        "name": 'CodebasedUtils',
        "description": "A Shared Dev Util Lib for Productivity and Efficiency"
    },
    {
        "name": "Taskor",
        "description": "A real-time CLI task management 🚀 - Organize, monitor, and interact with your CLI workflows like never before! 💻✨"
    },
    {
        "name": "CybrZhyk",
        "description": "An Ecosystem of Autonomous Tools Through a Single Language Interface (basically JARVIS)"
    }
]





def check_pip_package_upload_date(pip_package_name):
    response = requests.get(f'https://pypi.org/pypi/{pip_package_name.lower()}/json')
    if response.status_code == 200:
        data = response.json()
        latest_version = data['info']['version']
        release_date = data['releases'][latest_version][0]['upload_time']
        return release_date
    else:
        return None

def add_project_from_project_name(session, project_name, description='', is_new_project=True):
    github_repo = f"github.com/alexfigueroa-solutions/{project_name}"
    directory_path = f"/{project_name}"
    deployment_date = check_pip_package_upload_date(project_name)
    if deployment_date:
        is_deployed = True
    else:
        is_deployed = False

    # lowercase project_name
    pip_package_name = project_name.lower()

    ProjectService().create_project(
        session=session,
        name=project_name,
        description=description,
        github_repo=github_repo,
        directory_path=directory_path,
        is_deployed=is_deployed,
        deployment_date=deployment_date,
        pip_package_name=pip_package_name,
        parent_id=None,
        id=uuid.uuid4()
    )



def create_seeder_projects():
    session = get_db_session()
    # add projects from project var
    for project in projects:
        add_project_from_project_name(session, project["name"], project["description"])
    close_db_session(session)

create_seeder_projects()
