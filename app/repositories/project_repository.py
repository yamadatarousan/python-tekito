from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import ProjectSummary
from app.infrastructure.models import ProjectModel


class ProjectRepository:
    """プロジェクトの永続化を担当する。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, name: str) -> ProjectSummary:
        project = ProjectModel(name=name)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return ProjectSummary(id=project.id, name=project.name, created_at=project.created_at)

    def list_all(self) -> List[ProjectSummary]:
        rows = self.db.scalars(select(ProjectModel).order_by(ProjectModel.created_at.desc())).all()
        return [ProjectSummary(id=row.id, name=row.name, created_at=row.created_at) for row in rows]

    def get_by_id(self, project_id: int) -> Optional[ProjectSummary]:
        row = self.db.get(ProjectModel, project_id)
        if row is None:
            return None
        return ProjectSummary(id=row.id, name=row.name, created_at=row.created_at)
