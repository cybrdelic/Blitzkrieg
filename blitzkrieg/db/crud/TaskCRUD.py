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
    def create_tasks(session: Session, tasks: list):
        session.add_all(tasks)
        session.commit()
        return tasks

    @staticmethod
    def get_task_by_id(session: Session, task_id: int):
        return session.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks_by_ids(session: Session, task_ids: list):
        return session.query(Task).filter(Task.id.in_(task_ids)).all()

    @staticmethod
    def get_task_by_index(session: Session, task_index: int):
        return session.query(Task).filter(Task.index == task_index).first()

    @staticmethod
    def get_tasks_by_indices(session: Session, task_indices: list):
        return session.query(Task).filter(Task.index.in_(task_indices)).all()

    @staticmethod
    def get_all_tasks(session: Session):
        return session.query(Task).all()

    @staticmethod
    def get_all_paginated_tasks(session: Session, page: int, per_page: int):
        return session.query(Task).offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def get_task_with_relations(session: Session, task_id: int, relations: list):
        query = session.query(Task).options(joinedload(*relations))
        return query.filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks_with_relations(session: Session, task_ids: list, relations: list):
        query = session.query(Task).options(joinedload(*relations))
        return query.filter(Task.id.in_(task_ids)).all()


    @staticmethod
    def update_task(session: Session, task: Task):
        session.merge(task)
        session.commit()
        return task

    @staticmethod
    def update_tasks(session: Session, tasks: list):
        session.bulk_update_mappings(Task, tasks)
        session.commit()
        return tasks

    @staticmethod
    def delete_task(session: Session, task_id: int):
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            session.delete(task)
            session.commit()
        return task

    @staticmethod
    def delete_tasks(session: Session, task_ids: list):
        tasks = session.query(Task).filter(Task.id.in_(task_ids)).all()
        if tasks:
            session.delete(tasks)
            session.commit()
        return tasks

    @staticmethod
    def get_next_index(session: Session):
        task = session.query(Task).order_by(Task.index.desc()).first()
        if task:
            return task.index + 1
        else:
            return 1