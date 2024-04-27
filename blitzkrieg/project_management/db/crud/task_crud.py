
from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.task import Task
class TaskCRUD:
    @staticmethod
    def create_task(session: Session, task: Task):
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_task_by_id(session: Session, task_id: int):
        return session.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Task).all()

    @staticmethod
    def get_all_paginated_task(session: Session, page: int, per_page: int):
        return session.query(Task).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_task(session: Session, task: Task):
        session.merge(task)
        session.commit()
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int):
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            session.delete(task)
            session.commit()
        return task

    @staticmethod
    def get_next_index(session: Session):
        task = session.query(Task).order_by(Task.index.desc()).first()
        if task:
            return task.index + 1
        else:
            return 1


from sqlalchemy.orm import Session
from blitzkrieg.project_management.db.models.task import Task
class TaskCRUD:
    @staticmethod
    def create_task(session: Session, task: Task):
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_task_by_id(session: Session, task_id: int):
        return session.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_all_projects(session: Session):
        return session.query(Task).all()

    @staticmethod
    def get_all_paginated_task(session: Session, page: int, per_page: int):
        return session.query(Task).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def update_task(session: Session, task: Task):
        session.merge(task)
        session.commit()
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int):
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            session.delete(task)
            session.commit()
        return task

    @staticmethod
    def get_next_index(session: Session):
        task = session.query(Task).order_by(Task.index.desc()).first()
        if task:
            return task.index + 1
        else:
            return 1

