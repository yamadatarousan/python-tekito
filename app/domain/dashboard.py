from __future__ import annotations

from datetime import date
from typing import Iterable

from app.domain.entities import DashboardMetrics, TaskSnapshot, TaskStatus


def build_dashboard_metrics(snapshots: Iterable[TaskSnapshot], today: date) -> DashboardMetrics:
    """タスク一覧からダッシュボード集計値を構築する。

    学習ポイント:
    - 集計ロジックをDB層やWeb層から分離しておくと、テストしやすい。
    - 「期限切れ」の仕様は曖昧になりやすいので、関数として明文化する。
    """

    snapshot_list = list(snapshots)
    total_count = len(snapshot_list)
    done_count = sum(1 for task in snapshot_list if task.status == TaskStatus.done)
    overdue_count = sum(
        1
        for task in snapshot_list
        if task.status != TaskStatus.done and task.due_date is not None and task.due_date < today
    )

    if total_count == 0:
        completion_rate = 0
    else:
        # 小数点の扱いは画面表示上わかりやすい四捨五入にする。
        completion_rate = round((done_count / total_count) * 100)

    return DashboardMetrics(
        total_count=total_count,
        done_count=done_count,
        overdue_count=overdue_count,
        completion_rate=completion_rate,
    )
