from blitzkrieg.db.models.project import Project, Issue
from blitzkrieg.project_management.db.connection import get_docker_db_session
from blitzkrieg.ui_management.console_instance import console
from blitzkrieg.utils.github_utils import get_repo_issues

def fetch_and_save_issues(project: Project) -> None:
    """Fetch issues for a project and save them to the database."""
    session = get_docker_db_session()
    issues = get_repo_issues(project.github_repo)
    for issue_data in issues:
        issue = Issue(
            project_id=project.id,
            issue_number=issue_data['number'],
            title=issue_data['title'],
            state=issue_data['state'],
            created_at=issue_data['created_at'],
            updated_at=issue_data['updated_at'],
            body=issue_data['body']
        )
        session.add(issue)
    session.commit()
    console.handle_success(f"Fetched and saved {len(issues)} issues for project: {project.name}")
