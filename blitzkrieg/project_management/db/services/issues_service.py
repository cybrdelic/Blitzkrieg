from sqlalchemy import Integer, String
from sqlalchemy.orm import Session
from ..models.issue import Issue
from ..crud.issue_crud import IssueCRUD

class IssueService:
    @staticmethod
    def create_issue(
        session: Session,
        id: String,
        index: Integer,
        branch_name: String,
        title: String,
        description: String,
        created_at: String,
        updated_at: String,
        project_id: String
    ):
        issues = Issue(
            id=id, index=index, branch_name=branch_name, title=title, description=description, created_at=created_at, updated_at=updated_at, project_id=project_id
        )
        return IssueCRUD.create_issue(session, issues)

    @staticmethod
    def get_issues(
        session: Session,
        issues_id: int
    ):
        return IssueCRUD.get_issue_by_id(session, issues_id)

    @staticmethod
    def get_next_index(session: Session):
        return IssueCRUD.get_next_index(session)
