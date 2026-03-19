from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db_session
from app.domain.entities import TaskStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.services.dashboard_service import DashboardService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter(tags=["web"])

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _build_services(db: Session) -> Tuple[ProjectService, TaskService, DashboardService]:
    project_repository = ProjectRepository(db)
    task_repository = TaskRepository(db)
    project_service = ProjectService(project_repository)
    task_service = TaskService(task_repository=task_repository, project_repository=project_repository)
    dashboard_service = DashboardService(task_repository=task_repository)
    return project_service, task_service, dashboard_service


@router.get("/")
def top_page(request: Request, db: Session = Depends(get_db_session)):
    project_service, _, dashboard_service = _build_services(db)
    projects = project_service.list_projects()
    metrics = dashboard_service.build_metrics()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects,
            "metrics": metrics,
        },
    )


@router.post("/projects")
def create_project_from_form(name: str = Form(...), db: Session = Depends(get_db_session)):
    project_service, _, _ = _build_services(db)
    try:
        project_service.create_project(name=name)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/projects/{project_id}")
def project_detail_page(
    project_id: int,
    request: Request,
    status_filter: Optional[TaskStatus] = Query(default=None),
    db: Session = Depends(get_db_session),
):
    project_service, task_service, _ = _build_services(db)
    project = project_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="プロジェクトが見つかりません")

    tasks = task_service.list_tasks(project_id=project_id, status=status_filter)

    return templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "project": project,
            "tasks": tasks,
            "status_filter": status_filter.value if status_filter else "",
            "status_options": [TaskStatus.todo, TaskStatus.in_progress, TaskStatus.done],
        },
    )


@router.post("/projects/{project_id}/tasks")
def create_task_from_form(
    project_id: int,
    title: str = Form(...),
    description: str = Form(default=""),
    due_date_text: str = Form(default=""),
    db: Session = Depends(get_db_session),
):
    _, task_service, _ = _build_services(db)

    parsed_due_date = None
    if due_date_text.strip():
        # ハマりどころ: 日付入力は空文字が来るので、変換前に空判定が必要。
        try:
            parsed_due_date = date.fromisoformat(due_date_text)
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="期限日の形式が不正です") from error

    try:
        task_service.create_task(
            project_id=project_id,
            title=title,
            description=description,
            due_date=parsed_due_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return RedirectResponse(url=f"/projects/{project_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/cycle")
def cycle_task_status(task_id: int, project_id: int = Form(...), db: Session = Depends(get_db_session)):
    _, task_service, _ = _build_services(db)
    try:
        task_service.cycle_status(task_id=task_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return RedirectResponse(url=f"/projects/{project_id}", status_code=status.HTTP_303_SEE_OTHER)
