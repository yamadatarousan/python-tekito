from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import TaskDetail, TaskSnapshot, TaskStatus
from app.infrastructure.models import TaskModel


class TaskRepository:
    """タスクの永続化を担当する。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, project_id: int, title: str, description: str, due_date) -> TaskDetail:
        task = TaskModel(project_id=project_id, title=title, description=description, due_date=due_date)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return self._to_detail(task)

    def list_by_project(self, project_id: int, status: Optional[TaskStatus] = None) -> List[TaskDetail]:
        statement = select(TaskModel).where(TaskModel.project_id == project_id).order_by(TaskModel.created_at.desc())
        if status is not None:
            statement = statement.where(TaskModel.status == status.value)
        rows = self.db.scalars(statement).all()
        return [self._to_detail(row) for row in rows]

    def list_all_snapshots(self) -> List[TaskSnapshot]:
        rows = self.db.scalars(select(TaskModel)).all()
        return [
            TaskSnapshot(id=row.id, title=row.title, status=TaskStatus(row.status), due_date=row.due_date)
            for row in rows
        ]

    def get_by_id(self, task_id: int) -> Optional[TaskDetail]:
        row = self.db.get(TaskModel, task_id)
        if row is None:
            return None
        return self._to_detail(row)

    def update_status(self, task_id: int, status: TaskStatus) -> Optional[TaskDetail]:
        row = self.db.get(TaskModel, task_id)
        if row is None:
            return None

        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_detail(row)

    @staticmethod
    def _to_detail(row: TaskModel) -> TaskDetail:
        return TaskDetail(
            id=row.id,
            project_id=row.project_id,
            title=row.title,
            description=row.description,
            status=TaskStatus(row.status),
            due_date=row.due_date,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
