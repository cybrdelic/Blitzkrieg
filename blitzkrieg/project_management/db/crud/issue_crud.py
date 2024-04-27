
from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.issue import Issue
class IssueCRUD:
    @staticmethod
    def create_issue(session: Session, issue: Issue):
        try:
            session.add(issue)
            session.commit()
            session.refresh(issue)
            return issue
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def get_issue_by_id(session: Session, issue_id: int):
        try:
            return session.query(Issue).filter(Issue.id == issue_id).first()
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Issue).all()

    @staticmethod
    def get_all_paginated_issue(session: Session, page: int, per_page: int):
        return session.query(Issue).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_issue(session: Session, issue: Issue):
        session.merge(issue)
        session.commit()
        return issue

    @staticmethod
    def delete_issue(session: Session, issue_id: int):
        issue = session.query(Issue).filter(Issue.id == issue_id).first()
        if issue:
            session.delete(issue)
            session.commit()
        return issue

    @staticmethod
    def delete_all_issues(session: Session):
        issues = session.query(Issue).all()
        for issue in issues:
            session.delete(issue)
        session.commit()
        return issues

    @staticmethod
    def get_next_index(session: Session):
        issue = session.query(Issue).order_by(Issue.index.desc()).first()
        if issue:
            return issue.index + 1
        else:
            return 1

    @staticmethod
    def get_all_issues(session: Session):
        return session.query(Issue).all()
