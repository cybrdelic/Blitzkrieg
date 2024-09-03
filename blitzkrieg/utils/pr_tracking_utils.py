from blitzkrieg.db.models.project import Project, PullRequest
from blitzkrieg.project_management.db.connection import get_docker_db_session
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.utils.github_utils import get_repo_pull_requests

def fetch_and_save_pull_requests(project: Project) -> None:
    """Fetch pull requests for a project and save them to the database."""
    session = get_docker_db_session()
    pull_requests = get_repo_pull_requests(project.github_repo)
    for pr_data in pull_requests:
        pr = PullRequest(
            project_id=project.id,
            pr_number=pr_data['number'],
            title=pr_data['title'],
            state=pr_data['state'],
            created_at=pr_data['created_at'],
            updated_at=pr_data['updated_at'],
            body=pr_data['body']
        )
        session.add(pr)
    session.commit()
    console.handle_success(f"Fetched and saved {len(pull_requests)} pull requests for project: {project.name}")
