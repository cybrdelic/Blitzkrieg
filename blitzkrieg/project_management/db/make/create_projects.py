from faker import Faker
from blitzkrieg.db.connection import get_db_session, close_db_session
from blitzkrieg.db.services.project_service import ProjectService

def create_fake_projects(n):
    fake = Faker()
    session = get_db_session()

    all_projects = []
    for _ in range(n):
        name = fake.company()
        description = fake.catch_phrase()
        github_repo = fake.url()
        directory_path = fake.file_path()
        is_deployed = fake.boolean()
        deployment_date = fake.date_this_decade() if is_deployed else None
        pip_package_name = fake.word()

        # Randomly assign a parent project, or None if this is the first project
        parent_id = None if not all_projects else fake.random_element(all_projects).id

        project = ProjectService.create_project(session, name, description, github_repo, directory_path, is_deployed, deployment_date, pip_package_name, parent_id)
        all_projects.append(project)

    close_db_session(session)

# Create 10 fake projects
create_fake_projects(10)
