from sqlalchemy.orm import Session
from ..models.task import Task
from ..crud.task_crud import TaskCRUD

class TaskService:
    @staticmethod
    def create_task(
        session: Session,
        id: {'str'},
        description: {'str'},
        project_id: {'str'},
        is_completed: {'str'},
        completion_date: {'str'}
    ):
        task = Task(
            id=id, description=description, project_id=project_id, is_completed=is_completed, completion_date=completion_date
        )
        return TaskCRUD.create_task(session, task)

    @staticmethod
    def get_task(
        session: Session,
        task_id: int
    ):
        return TaskCRUD.get_task(session, task_id)

    @staticmethod
    def get_next_index(session: Session):
        return TaskCRUD.get_next_index(session)
