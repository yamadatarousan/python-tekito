from __future__ import annotations

from datetime import date
from typing import List, Optional

from app.domain.entities import TaskDetail, TaskStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository


class TaskService:
    """タスク操作のユースケースを担当する。"""

    def __init__(self, task_repository: TaskRepository, project_repository: ProjectRepository) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str,
        due_date: Optional[date],
    ) -> TaskDetail:
        # 前提: プロジェクトが存在しない状態でタスクを作ると、UIとデータの整合が壊れる。
        if self.project_repository.get_by_id(project_id) is None:
            raise ValueError("対象プロジェクトが存在しません")

        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("タスク名は必須です")

        return self.task_repository.create(
            project_id=project_id,
            title=normalized_title,
            description=description.strip(),
            due_date=due_date,
        )

    def list_tasks(self, project_id: int, status: Optional[TaskStatus] = None) -> List[TaskDetail]:
        return self.task_repository.list_by_project(project_id=project_id, status=status)

    def update_status(self, task_id: int, status: TaskStatus) -> TaskDetail:
        updated = self.task_repository.update_status(task_id=task_id, status=status)
        if updated is None:
            raise ValueError("対象タスクが存在しません")
        return updated

    def cycle_status(self, task_id: int) -> TaskDetail:
        current = self.task_repository.get_by_id(task_id)
        if current is None:
            raise ValueError("対象タスクが存在しません")

        # 学習用に状態遷移を単純化し、ボタン1つで次状態へ進められるようにする。
        if current.status == TaskStatus.todo:
            next_status = TaskStatus.in_progress
        elif current.status == TaskStatus.in_progress:
            next_status = TaskStatus.done
        else:
            next_status = TaskStatus.todo

        return self.update_status(task_id=task_id, status=next_status)
