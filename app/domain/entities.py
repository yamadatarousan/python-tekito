from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    """タスク状態。

    APIとDBのどちらでも同じ値を使うため、文字列Enumで定義する。
    """

    todo = "todo"
    in_progress = "in_progress"
    done = "done"


@dataclass(frozen=True)
class TaskSnapshot:
    """集計用に必要な最小情報だけを持つ読み取りモデル。"""

    id: int
    title: str
    status: TaskStatus
    due_date: Optional[date]


@dataclass(frozen=True)
class DashboardMetrics:
    """ダッシュボード表示で使う集計結果。"""

    total_count: int
    done_count: int
    overdue_count: int
    completion_rate: int


@dataclass(frozen=True)
class ProjectSummary:
    """トップ画面でプロジェクト一覧を描画するための要約情報。"""

    id: int
    name: str
    created_at: datetime


@dataclass(frozen=True)
class TaskDetail:
    """画面描画で使うタスク詳細。"""

    id: int
    project_id: int
    title: str
    description: str
    status: TaskStatus
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime
