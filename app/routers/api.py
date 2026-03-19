from __future__ import annotations

from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db_session
from app.domain.entities import TaskStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.api import (
    DashboardResponse,
    ProjectCreateRequest,
    ProjectResponse,
    TaskCreateRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
)
from app.services.dashboard_service import DashboardService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter(prefix="/api", tags=["api"])


def _build_services(db: Session) -> Tuple[ProjectService, TaskService, DashboardService]:
    project_repository = ProjectRepository(db)
    task_repository = TaskRepository(db)
    project_service = ProjectService(project_repository)
    task_service = TaskService(task_repository=task_repository, project_repository=project_repository)
    dashboard_service = DashboardService(task_repository=task_repository)
    return project_service, task_service, dashboard_service


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreateRequest, db: Session = Depends(get_db_session)) -> ProjectResponse:
    project_service, _, _ = _build_services(db)
    try:
        project = project_service.create_project(name=payload.name)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return ProjectResponse.from_domain(project)


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(project_id: int, payload: TaskCreateRequest, db: Session = Depends(get_db_session)) -> TaskResponse:
    _, task_service, _ = _build_services(db)
    try:
        task = task_service.create_task(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return TaskResponse.from_domain(task)


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
def list_tasks(
    project_id: int,
    status: Optional[TaskStatus] = Query(default=None),
    db: Session = Depends(get_db_session),
) -> List[TaskResponse]:
    _, task_service, _ = _build_services(db)
    tasks = task_service.list_tasks(project_id=project_id, status=status)
    return [TaskResponse.from_domain(task) for task in tasks]


@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    db: Session = Depends(get_db_session),
) -> TaskResponse:
    _, task_service, _ = _build_services(db)
    try:
        task = task_service.update_status(task_id=task_id, status=payload.status)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return TaskResponse.from_domain(task)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db_session)) -> DashboardResponse:
    _, _, dashboard_service = _build_services(db)
    metrics = dashboard_service.build_metrics()
    return DashboardResponse.from_domain(metrics)
