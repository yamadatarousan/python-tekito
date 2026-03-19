from __future__ import annotations

from typing import List, Optional

from app.domain.entities import ProjectSummary
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    """プロジェクト操作のユースケースを担当する。"""

    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def create_project(self, name: str) -> ProjectSummary:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("プロジェクト名は必須です")
        return self.repository.create(name=normalized_name)

    def list_projects(self) -> List[ProjectSummary]:
        return self.repository.list_all()

    def get_project(self, project_id: int) -> Optional[ProjectSummary]:
        return self.repository.get_by_id(project_id)
