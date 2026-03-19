from __future__ import annotations

from datetime import date

from app.domain.dashboard import build_dashboard_metrics
from app.domain.entities import DashboardMetrics
from app.repositories.task_repository import TaskRepository


class DashboardService:
    """ダッシュボード向けの集計ユースケース。"""

    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def build_metrics(self) -> DashboardMetrics:
        snapshots = self.task_repository.list_all_snapshots()
        return build_dashboard_metrics(snapshots=snapshots, today=date.today())
