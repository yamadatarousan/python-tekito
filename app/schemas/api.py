from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.entities import DashboardMetrics, ProjectSummary, TaskDetail, TaskStatus


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class ProjectResponse(BaseModel):
    id: int
    name: str

    @classmethod
    def from_domain(cls, project: ProjectSummary) -> "ProjectResponse":
        return cls(id=project.id, name=project.name)


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    due_date: Optional[date] = None


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    status: TaskStatus
    due_date: Optional[date]

    @classmethod
    def from_domain(cls, task: TaskDetail) -> "TaskResponse":
        return cls(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            due_date=task.due_date,
        )


class DashboardResponse(BaseModel):
    total_count: int
    done_count: int
    overdue_count: int
    completion_rate: int

    @classmethod
    def from_domain(cls, metrics: DashboardMetrics) -> "DashboardResponse":
        return cls(
            total_count=metrics.total_count,
            done_count=metrics.done_count,
            overdue_count=metrics.overdue_count,
            completion_rate=metrics.completion_rate,
        )
