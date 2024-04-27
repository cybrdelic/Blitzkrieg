from sqlalchemy.orm import Session
from ..models.issue import Issue
from ..crud.issue_crud import IssueCRUD

class IssueService:
    @staticmethod
    def create_issue(
        session: Session,
        id: {'str'},
        index: {'str'},
        branch_name: {'str'},
        title: {'str'},
        description: {'str'},
        created_at: {'str'},
        updated_at: {'str'},
        project_id: {'str'}
    ):
        issue = Issue(
            id=id, index=index, branch_name=branch_name, title=title, description=description, created_at=created_at, updated_at=updated_at, project_id=project_id
        )
        return IssueCRUD.create_issue(session, issue)

    @staticmethod
    def get_issues(
        session: Session,
        issues_id: int
    ):
        return IssueCRUD.get_issues(session, issues_id)

    @staticmethod
    def get_next_index(session: Session):
        return IssueCRUD.get_next_index(session)

    @staticmethod
    def get_all_issues(session: Session):
        return IssueCRUD.get_all_issues(session)

    @staticmethod
    def delete_issue(session: Session, issue_id: int):
        return IssueCRUD.delete_issue(session, issue_id)
