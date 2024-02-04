from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.issue import Issue
class IssueCRUD:
    @staticmethod
    def create_issue(session: Session, issue: Issue):
        session.add(issue)
        session.commit()
        session.refresh(issue)
        return issue

    @staticmethod
    def create_issues(session: Session, issues: list):
        session.add_all(issues)
        session.commit()
        return issues

    @staticmethod
    def get_issue_by_id(session: Session, issue_id: int):
        return session.query(Issue).filter(Issue.id == issue_id).first()

    @staticmethod
    def get_issues_by_ids(session: Session, issue_ids: list):
        return session.query(Issue).filter(Issue.id.in_(issue_ids)).all()

    @staticmethod
    def get_issue_by_index(session: Session, issue_index: int):
        return session.query(Issue).filter(Issue.index == issue_index).first()

    @staticmethod
    def get_issues_by_indices(session: Session, issue_indices: list):
        return session.query(Issue).filter(Issue.index.in_(issue_indices)).all()

    @staticmethod
    def get_all_issues(session: Session):
        return session.query(Issue).all()

    @staticmethod
    def get_all_paginated_issues(session: Session, page: int, per_page: int):
        return session.query(Issue).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def get_issue_with_relations(session: Session, issue_id: int, relations: list):
        query = session.query(Issue).options(joinedload(*relations))
        return query.filter(Issue.id == issue_id).first()

    @staticmethod
    def get_issues_with_relations(session: Session, issue_ids: list, relations: list):
        query = session.query(Issue).options(joinedload(*relations))
        return query.filter(Issue.id.in_(issue_ids)).all()


    @staticmethod
    def update_issue(session: Session, issue: Issue):
        session.merge(issue)
        session.commit()
        return issue

    @staticmethod
    def update_issues(session: Session, issues: list):
        session.bulk_update_mappings(Issue, issues)
        session.commit()
        return issues

    @staticmethod
    def delete_issue(session: Session, issue_id: int):
        issue = session.query(Issue).filter(Issue.id == issue_id).first()
        if issue:
            session.delete(issue)
            session.commit()
        return issue

    @staticmethod
    def delete_issues(session: Session, issue_ids: list):
        issues = session.query(Issue).filter(Issue.id.in_(issue_ids)).all()
        if issues:
            session.delete(issues)
            session.commit()
        return issues

    @staticmethod
    def get_next_index(session: Session):
        issue = session.query(Issue).order_by(Issue.index.desc()).first()
        if issue:
            return issue.index + 1
        else:
            return 1